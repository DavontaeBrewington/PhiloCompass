"""PhiloCompass — a Socratic teaching app.

FastAPI backend serving a vanilla-JS SPA that lets users explore a
concept galaxy, look up thinkers, and be drawn into Socratic dialogue.

The app runs fully offline (curated question bank + knowledge graph) and
OPTIONALLY upgrades to adaptive LLM-driven dialogue when OPENAI_API_KEY is
present. It never requires credentials.

Run:  uvicorn philo_app.main:app --port 8000
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

from . import socratic_engine, socratic_llm, data_thinkers, envdot, debate

envdot.load_dotenv()

app = FastAPI(title="PhiloCompass", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ──────────────────────────────────────────────────────────────────────────
#  Models
# ──────────────────────────────────────────────────────────────────────────

class SessionStart(BaseModel):
    domain: str | None = None  # optional filter
    custom_question: str | None = None
    node_id: str | None = None  # seed a Socratic question about a specific thinker/concept
    mode: str | None = None  # "debate" | None (dialogue)
    pair_with: str | None = None  # debate opponent node id
    last_node_id: str | None = None  # connect this question to what they just explored
    reword: bool = False  # re-cast the current question in plainer language


class AnswerIn(BaseModel):
    session_id: str
    answer: str | None = None
    mode: str | None = None  # "debate" reasons it differently
    want_hint: bool = False  # student asked for an on-demand scaffold
    hint_level: int = 0  # 0=conceptual, 1=worked-example, 2=direct-lead
    reword: bool = False  # re-cast the current question in plainer language
    teach_me: bool = False  # give a full explanatory foundation for the question


class HintRequest(BaseModel):
    session_id: str
    hint_level: int = 0


class TeachRequest(BaseModel):
    session_id: str


# In-memory session store (fine for single-user / demo use). Sessions die
# on server restart — acceptable for a teaching tool.
_SESSIONS: dict[str, socratic_engine.SocraticSession] = {}
_DEBATES: dict[str, debate.Debate] = {}


def _scaffold_hint(req: AnswerIn) -> dict | None:
    """Progressive, construction-of-knowledge scaffolding: conceptual nudge →
    worked example → direct lead. Support that fades as the student builds
    the idea themselves."""
    session = _SESSIONS.get(req.session_id)
    if not session:
        return {"error": "Session not found or expired. Start a new one."}
    level = max(0, min(2, req.hint_level))
    if level == 0:
        text = (
            "🪜 Scaffold step 1 — the concept: try to reframe the question "
            "without giving an answer yet. Name the two ideas that are rubbing "
            "against each other in what you're wrestling with (even vaguely). "
            "Often the act of naming the conflict loosens it."
        )
    elif level == 1:
        text = (
            "🪜 Scaffold step 2 — a worked example: imagine a concrete, small "
            "case. If your view were right, what would that case look like — "
            "what decision, feeling, or judgment would follow? Test your idea "
            "on that little example before you search for the grand answer."
        )
    else:
        text = (
            "🪜 Scaffold step 3 — a direct lead: look for the assumption hiding "
            "under your answer and question it. Whatever you just said, ask "
            "yourself 'what had to be true for me to think that?' — then ask "
            "whether that hidden premise actually holds."
        )
    return {"scaffold": text, "scaffold_level": level}


def _debate_teach(d: debate.Debate) -> str:
    """A foundation for the debate question so someone with no background can
    follow who's talking and what's at stake."""
    a = debate.speaker_label(d.a)
    b = debate.speaker_label(d.b)
    ai = debate._key_idea(d.a)
    bi = debate._key_idea(d.b)
    return (
        f"Let's set the debate up for you.\n\n"
        f"**The question on the table**\n{d.prompt}\n\n"
        f"**Two sides**\n— **{a}** roughly holds: “{ai}”\n— **{b}** roughly holds: “{bi}”\n\n"
        f"**Why it matters**\nThis is a live disagreement with no settled answer — "
        f"that's exactly what makes it worth hearing out. Neither side is obviously "
        f"right, and the strongest version of each is what the debate is testing.\n\n"
        f"**How to take part**\nYou don't need to pick a side yet. As they argue, "
        f"notice which move pulls on you and which one makes you want to push back. "
        f"Then say whose reasoning held up better for you, and why. That weighing "
        f"is the whole point."
    )


def _debate_reword(d: debate.Debate) -> str:
    """Plainer-language re-cast of the debate prompt."""
    a = debate.speaker_label(d.a)
    b = debate.speaker_label(d.b)
    q = d.prompt.rstrip("?")
    return (
        f"No trouble at all — let's take the weight off. We've got {a} on one side "
        f"and {b} on the other. Put simply, the question we're really circling is: "
        f"{q}? Neither side is right yet — we're figuring it out as we go. Which "
        f"way do you lean so far?"
    )


def _debate_answer(d: debate.Debate, req: AnswerIn, session: socratic_engine.SocraticSession | None) -> dict:
    student_turn = debate.next_debate_turn(d, student_text=req.answer)
    # When both sides have spoken twice, invite a verdict
    if d.turn >= 5:
        return {
            "turn": student_turn,
            "mode": "debate",
            "conclusion": (
                f"Two views are on the table — {debate.speaker_label(d.a)} and "
                f"{debate.speaker_label(d.b)}. Which side moved you more, and "
                f"why? (Or tell us where *your* position lands between them.)"
            ),
        }
    return {"turn": student_turn, "mode": "debate", "conclusion": None}


def _reflection_text(session: socratic_engine.SocraticSession) -> str:
    """A personalized takeaway card — consolidates the question, the moves the
    student made, the tension they hit, and steelmans their best position so
    they can refine it. This is the step that makes learning stick."""
    answers = session.student_answers
    if not answers:
        return (
            "You've worked through this from a few angles — that's where real "
            "philosophy lives. Which answer would you defend to someone who "
            "disagreed, and why?"
        )
    m = socratic_engine.momentum_summary(session)
    steelman_target = answers[-1][:120] + ("…" if len(answers[-1]) > 120 else "")
    # Give the student a generous, nameable restatement on their own terms
    return (
        "🔖 Your takeaway I'm holding up\n"
        f"Here's what you actually did: you made {m['arguments'] or 1} argument(s), "
        f"met {m['tensions_seen']} genuine tension(s), and refined your view "
        f"{m['refinements'] or 1} time(s). That's not trivia — that's the shape "
        f"real thinking takes.\n\n"
        f"The strongest version of what you ended near is roughly:\n"
        f"“{steelman_target}”\n\n"
        f"To make it yours: could you say it in one sentence, without my wording? "
        f"And name one place where you think it's still wobbly — that wobble is "
        f"your next question to chase."
    )


# ──────────────────────────────────────────────────────────────────────────
#  API
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm": socratic_llm.llm_available(),
        "app": "philocompass",
    }


@app.get("/api/domains")
def domains():
    return {"domains": socratic_engine.domain_labels()}


@app.post("/api/session/start")
def session_start(req: SessionStart):
    import uuid

    # DEBATE MODE: two thinkers clash, student weighs in.
    if req.mode == "debate":
        # support explicit pairing, random pair, OR a fully custom topic
        if req.node_id:
            a = req.node_id
            b = req.pair_with
            if req.custom_question:  # fully custom debate
                a, b, prompt = a, b, req.custom_question
            else:
                pair = debate.pair_from_id(a, b) if b else (a, b, "Two thinkers lock horns. Where do you stand?")
                if not pair:
                    return {"error": f"Could not set up a debate involving {a}."}
                a, b, prompt = pair
        else:
            a, b, prompt = debate.pick_pair()
        sid = uuid.uuid4().hex
        d = debate.Debate(a=a, b=b, prompt=prompt)
        _DEBATES[sid] = d
        opening = debate.next_debate_turn(d)
        return {
            "session_id": sid,
            "mode": "debate",
            "question": prompt,
            "opening": opening,
            "side_a": debate.speaker_label(a),
            "side_b": debate.speaker_label(b),
            "llm": socratic_llm.llm_available(),
        }

    # Node-seeded dialogue: derive a Socratic question about the clicked thinker.
    if req.node_id:
        node = data_thinkers.node_info(req.node_id)
        if not node:
            return {"error": f"Unknown thinker/concept: {req.node_id}"}
        name = node.get("name", "this idea")
        blurb = node.get("blurb")
        q = socratic_engine.Question(
            text=f"What does {name} really amount to — and is it a view you can defend?",
            domain=node.get("domain") or "custom",
            hint=(f"Consider: {blurb}" if blurb else f"Press on the central claim behind {name}."),
            followups=(
                f"Put {name}'s core idea in your own words — what is it actually claiming?",
                f"What would it take for {name} to be wrong? Try to state the strongest objection.",
                f"What's the tension between {name} and a view you already hold?",
                f"If you had to defend {name} to a skeptic, where would you begin — and where does it weaken?",
            ),
        )
        domain = node.get("domain") or "custom"
    elif req.custom_question:
        q = socratic_engine.Question(
            text=req.custom_question,
            domain=req.domain or "custom",
            hint="Consider what assumptions your question rests on.",
            followups=(
                "What exactly do the key terms mean?",
                "What would count as a good answer — what criteria would it need to meet?",
                "What opposing view are you most tempted to reject, and why?",
            ),
        )
        domain = req.domain or "custom"
    else:
        q = socratic_engine.random_question(req.domain)
        domain = q.domain

    sid = uuid.uuid4().hex
    session = socratic_engine.SocraticSession(question=q, domain=domain)
    if req.last_node_id:
        session.prior_node = req.last_node_id  # for "connect it to you" scaffolding
    _SESSIONS[sid] = session

    # RE-WORD: re-cast the opening question in plainer language up front.
    reworded = None
    if req.reword:
        reworded = socratic_engine.reword_question(q.text) if not socratic_llm.llm_available() else socratic_llm.reword_question(q.text, session)
    return {
        "session_id": sid,
        "question": reworded or q.text,
        "reworded": bool(reworded),
        "hint": q.hint,
        "domain": domain,
        "domain_label": socratic_engine.domain_labels().get(domain, domain),
        "llm": socratic_llm.llm_available(),
        "connect": socratic_llm.connect_hint(session) if socratic_llm.llm_available() else socratic_engine.curated_connect(session),
    }


@app.post("/api/session/answer")
def session_answer(req: AnswerIn):
    # ── ON-DEMAND SCAFFOLD (works for dialogue AND debate) ─────
    if req.want_hint:
        res = _scaffold_hint(req)
        if res:
            return res

    # ── Options first, so teach/reword work in BOTH dialogue and debate ──
    d = _DEBATES.get(req.session_id)
    session = _SESSIONS.get(req.session_id)

    # TEACH ME — works for dialogue sessions and for the CURRENT debate question.
    if req.teach_me:
        if session:
            lesson = socratic_llm.teach_me(session) if socratic_llm.llm_available() else socratic_engine.teach_me(session)
        elif d:
            lesson = _debate_teach(d)
        else:
            return {"error": "Session not found or expired. Start a new one."}
        return {"taught": True, "lesson": lesson or "Here's the lay of the land to help you think:\n(sorry — I couldn't fetch a full lesson right now, but try 'Reword' or just make your best guess and we'll refine it.)"}

    # REWORD — re-cast the current question in plainer language.
    if req.reword:
        if session:
            rw = socratic_llm.reword_question(session.question.text, session) if socratic_llm.llm_available() else socratic_engine.reword_question(session.question.text)
            question = rw or session.question.text
        elif d:
            question = _debate_reword(d)
        else:
            return {"error": "Session not found or expired. Start a new one."}
        return {"reworded": True, "question": question, "follow_up": question}

    # ── DEBATE MODE ─────────────────────────────────────────────
    if req.mode == "debate":
        if not d:
            return {"error": "Debate session not found or expired. Start a new one."}
        return _debate_answer(d, req, session)

    # ── DIALOGUE MODE ───────────────────────────────────────────
    session = _SESSIONS.get(req.session_id)
    session.student_answers.append(req.answer or "")
    session.turns += 1
    session.last_answer = req.answer or ""

    # ── Cognitive-state tracking ───────────────────────────────
    # Classify the student's reasoning move so the next question adapts to
    # where they ARE, not just the last thing they said.
    move = socratic_engine.classify_move(req.answer)
    session.motion[step_key(session)] = {"move": move, "text": req.answer}
    pedagogy = socratic_engine.pedagogy_for(move, session)

    follow_up = None
    if socratic_llm.llm_available():
        try:
            follow_up = socratic_llm.socratic_reply(session, req.answer, pedagogy=pedagogy)
        except Exception as e:
            print(f"[Socratic-LLM] fell back to offline: {e}")
            follow_up = None

    if not follow_up:
        # Offline follow-up driven by the classified move OR the rotating list.
        follow_up = pedagogy.get("question") if pedagogy.get("question") else (
            session.question.followups[(session.turns - 1) % len(session.question.followups)]
        )

    return {
        "follow_up": follow_up,
        "turns": session.turns,
        "is_advanced": session.is_advanced,
        "mode": "llm" if (socratic_llm.llm_available() and follow_up) else "offline",
        "move": move,
        "pedagogy": pedagogy,
        "momentum": socratic_engine.momentum_summary(session),
        "threadback": socratic_engine.threadback(session, req.answer) if not socratic_llm.llm_available() else None,
        "conclusion": _reflection_text(session) if session.is_advanced else None,
    }


def step_key(session) -> str:
    return f"turn{session.turns}"


@app.get("/api/map")
def concept_map():
    return {
        "nodes": data_thinkers.all_nodes(),
        "edges": data_thinkers.all_edges(),
        "domains": socratic_engine.domain_labels(),
    }


@app.get("/api/paths")
def paths():
    return {"paths": data_thinkers.learning_paths()}


@app.get("/api/glossary")
def glossary():
    return {"glossary": data_thinkers.glossary()}


@app.get("/api/thinker/{nid}")
def thinker(nid: str):
    info = data_thinkers.node_info(nid)
    if not info:
        return {"error": "Unknown thinker/concept"}
    # Influences (things this one shaped)
    influences = [
        data_thinkers.node_info(t).get("name")
        for f, t in data_thinkers.lineage_edges()
        if f == nid and data_thinkers.node_info(t)
    ]
    # Influenced by
    influenced_by = [
        data_thinkers.node_info(f).get("name")
        for f, t in data_thinkers.lineage_edges()
        if t == nid and data_thinkers.node_info(f)
    ]
    # Related
    related = []
    for a, b in data_thinkers.related_edges():
        if a == nid and data_thinkers.node_info(b):
            related.append(data_thinkers.node_info(b).get("name"))
        elif b == nid and data_thinkers.node_info(a):
            related.append(data_thinkers.node_info(a).get("name"))
    return {
        "id": nid,
        "name": info.get("name"),
        "kind": info.get("kind"),
        "era": info.get("era"),
        "domain": info.get("domain"),
        "blurb": info.get("blurb"),
        "influences": influences,
        "influenced_by": influenced_by,
        "related": related,
    }


# ──────────────────────────────────────────────────────────────────────────
#  Frontend
# ──────────────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/sw.js")
def service_worker():
    # Serve the service worker from root scope so it can cache the whole app.
    return FileResponse(os.path.join(STATIC_DIR, "sw.js"), media_type="application/javascript")


# ──────────────────────────────────────────────────────────────────────────
#  Custom error handler so unknown routes don't leak details
# ──────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    port = int(os.environ.get("PHILO_PORT", "8001"))
    uvicorn.run("philo_app.main:app", host="0.0.0.0", port=port)
