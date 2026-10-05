"""Offline Socratic tutor engine for PhiloCompass.

This is the intelligence layer that works WITHOUT any API key. It powers
the app in fully offline mode (also great for demos and for the classroom,
where you never want to depend on the network). When an LLM key is present,
`socratic_llm.py` upgrades this with richer, adaptive dialogue — but the
engine below is a complete, thoughtful tutor on its own.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


# ──────────────────────────────────────────────────────────────────────────
#  Question bank. Every entry is a real Socratic prompt with a teaching
#  note for the tutor to offer as a nudge. Organized by philosophy domain.
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Question:
    text: str
    domain: str
    hint: str
    followups: tuple[str, ...] = ()


def _bank() -> list[Question]:
    return [
        # ── Ancient / Plato-Socrates ──
        Question(
            "What does justice require of a person, and why should anyone be just if they can get away with being unjust?",
            "plato",
            "Think about Glaucon's challenge in the Republic — can you tell the difference between being just and merely seeming just?",
            (
                "Is justice good for its own sake, or only because of its consequences?",
                "If a ring made you invisible, what would you do — and what does that reveal about your view of morality?",
                "Does justice live in the individual or in the state — and how do the two relate?",
            ),
        ),
        Question(
            "Can virtue be taught?",
            "plato",
            "Socrates presses this in the Meno — consider whether knowledge alone makes someone good.",
            (
                "Is being a good person more like knowing geometry or like learning to ride a bike?",
                "If you could teach someone the definition of courage, would they become courageous?",
                "What's the difference between what can be taught and what can be practiced?",
            ),
        ),
        Question(
            "What is the best life for a human being to live?",
            "aristotle",
            "Aristotle says the best life is happiness (eudaimonia) — but what does flourishing actually consist in?",
            (
                "Is happiness a feeling, an activity, or a kind of life?",
                "Could someone be deeply happy while living a morally bad life?",
                "Is the good life the same for everyone, or does it depend on each person's nature?",
            ),
        ),
        # ── Ethics ──
        Question(
            "Is an action right because it maximizes happiness, or for some other reason?",
            "ethics",
            "This splits utilitarianism (consequences) from deontology (duties). Where do you stand — and can you defend the edge cases?",
            (
                "Would you push one person off a bridge to save five? Why or why not?",
                "Is it ever right to break a promise if it causes more overall happiness?",
                "What has intrinsic value — happiness, persons, freedom, or something else?",
            ),
        ),
        Question(
            "Where does moral obligation come from?",
            "ethics",
            "Is morality discovered (out there) or invented (up to us)? Throughout, notice which view you keep gravitating to.",
            (
                "If no one were watching and there were no consequences, would anything still be wrong?",
                "Is a moral rule valid because it's rational, because it's commanded, or because people agree on it?",
                "Does 'ought' ever really follow from 'is'?",
            ),
        ),
        Question(
            "What, if anything, makes a life meaningful?",
            "existentialism",
            "Existentialists say meaning is created, not found. Do you agree that we must build our own?",
            (
                "If there is no God, can human life still have objective meaning?",
                "Is meaning something we discover in the world or something we project onto it?",
                "Could an activity be meaningful even if it leads nowhere?",
            ),
        ),
        # ── Epistemology ──
        Question(
            "What can we know, and how can we be sure?",
            "epistemology",
            "Descartes started by doubting everything. Try it for yourself — what survives total doubt?",
            (
                "Could you be dreaming right now — and does that matter for what you know?",
                "Is knowledge just justified true belief, or is there something more?",
                "Does 'I think, therefore I am' actually prove anything?",
            ),
        ),
        Question(
            "What counts as good evidence for a belief?",
            "epistemology",
            "Consider when you're willing to believe something — is it about quantity of evidence, quality, or testimony?",
            (
                "If everyone you know believes X, but you have no reason — should you believe X too?",
                "Can testimony from an expert make something you don't understand rational to believe?",
                "Is faith a type of knowledge or a rival to it?",
            ),
        ),
        # ── Metaphysics / Free will ──
        Question(
            "If my choices are caused by prior events, am I still free?",
            "metaphysics",
            "This is the compatibilism question — does freedom survive determinism, or do the two contradict?",
            (
                "Does it require 'could have done otherwise' to be free, or is a different kind of freedom enough?",
                "If quantum randomness existed, would that make us free or just unpredictable?",
                "Is moral responsibility possible without free will?",
            ),
        ),
        Question(
            "What is the self?",
            "metaphysics",
            "Locke said a person is a sequence of memories; Hume said the self is a bundle of perceptions. What survives when you strip away the physical body?",
            (
                "If your body were replaced piece by piece, at what point (if ever) would you stop being you?",
                "If an exact copy of you were made, which one is the real you?",
                "Is the self something you have, or something you do?",
            ),
        ),
        # ── Political philosophy ──
        Question(
            "What gives a government legitimate authority over me?",
            "politics",
            "Hobbes, Locke, and Rousseau all imagine a social contract. Why would you freely hand over freedom — and under what terms?",
            (
                "If you never signed an agreement, does the state still have a claim on you?",
                "Is consent imagined conveniently after the fact?",
                "Is a legitimate state possible without coercing anyone?",
            ),
        ),
        Question(
            "What would a just society look like?",
            "politics",
            "Rawls asks you to design society behind a veil of ignorance. What rules would you choose if you didn't know your own position?",
            (
                "Would you choose equality of outcome, opportunity, or something else?",
                "Is some inequality necessary as an incentive, and is that fair?",
                "Does justice demand compensation for past injustice, and how far back?",
            ),
        ),
    ]


_BANK = _bank()
_DOMAINS = ["plato", "aristotle", "ethics", "existentialism", "epistemology", "metaphysics", "politics"]
_DOMAIN_LABELS = {
    "plato": "Ancient & Plato",
    "aristotle": "Aristotle",
    "ethics": "Ethics",
    "existentialism": "Existentialism",
    "epistemology": "Epistemology",
    "metaphysics": "Metaphysics",
    "politics": "Political Philosophy",
}


def domain_labels() -> dict[str, str]:
    return dict(_DOMAIN_LABELS)


def random_question(domain: str | None = None) -> Question:
    pool = [q for q in _BANK if domain is None or q.domain == domain]
    if not pool:
        pool = _BANK
    return random.choice(pool)


# ──────────────────────────────────────────────────────────────────────────
#  Session state — a single running dialogue with a student.
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class SocraticSession:
    question: Question
    domain: str
    turns: int = 0
    nudges_given: list[str] = field(default_factory=list)
    student_answers: list[str] = field(default_factory=list)
    motion: dict = field(default_factory=dict)  # track epistemic progress
    prior_node: str | None = None  # what the student explored just before (constructivism hook)
    last_answer: str = ""  # most recent student answer, for hint/steelman context

    @property
    def is_advanced(self) -> bool:
        return self.turns >= 3


def curated_connect(session: "SocraticSession") -> str | None:
    """Offline 'connect it to you' scaffold. Anchors a new question to whatever
    the student just explored (prior node), or to a broad friendly prompt."""
    if session.prior_node:
        prior = _DOMAIN_LABELS.get(session.prior_node, session.prior_node.replace("_", " "))
        return (
            f"Before we dive in — you were just thinking about {prior}. "
            f"Hold that in mind; see how this new question either echoes it or "
            f"tugs against it. That friction is where learning happens."
        )
    return (
        "Quick grounding: no need to be 'right.' This is about building the idea "
        "in your head, not reciting one. Take a first honest stab and we'll "
        "build from there."
    )


# ──────────────────────────────────────────────────────────────────────────
#  Cognitive-state tracking — the heart of good Socratic teaching.
# ──────────────────────────────────────────────────────────────────────────

_REASONING_MOVES = [
    "claimed",       # asserted a position
    "reasons",       # offered a supporting reason/argument
    "tension",       # noticed/struct a tension between two ideas
    "changed_mind",  # revised or abandoned an earlier view
    "receded",       # backed off / grew unsure
    "example",       # gave a concrete case or illustration
    "question",      # asked a clarifying question back
    "equal_valued",  # weighed/compared two values or sides
]


def classify_move(text: str) -> str:
    """Heuristic classification of a student's reasoning move. When the LLM is
    present, `socratic_llm` refines this; offline this gives the tutor a real
    target for the next question."""
    t = (text or "").lower()
    if not t.strip():
        return "receded"
    markers = {
        "claimed": ["i think", "i believe", "is", "should", "must", "i'd say", "my view"],
        "reasons": ["because", "since", "the reason", "this follows", "which means"],
        "tension": ["but", "however", "yet", "on the other hand", "conflict", "tension", "both"],
        "changed_mind": ["actually", "i was wrong", "now i", "on reflection", "i've come to think", "instead"],
        "receded": ["not sure", "i don't know", "guess", "maybe", "perhaps", "unsure", "?"],
        "example": ["for example", "for instance", "imagine", "like a", "such as", "e.g."],
        "question": ["what if", "does that", "how", "why would", "is it"],
        "equal_valued": ["trade-off", "balance", "between", "weigh", "prize", "value"],
    }
    counts = {k: sum(1 for m in v if m in t) for k, v in markers.items()}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "claimed"


# Each move → the pedagogical next-question + a rationale (feed into Teacher's lens)
_MOVE_PEDAGOGY = {
    "claimed": (
        "That's a position — now what makes you hold it? Give me one reason, "
        "and we'll test whether it really supports what you claim.",
        "I asked for a reason because a claim only becomes knowledge when you "
        "can say why. This moves you from assertion to argument.",
    ),
    "reasons": (
        "Good — a reason. Now, what assumption is hiding inside that reason? "
        "What had to be true for it to work?",
        "I probed the hidden assumption because finding it is where a reason "
        "either survives or collapses.",
    ),
    "tension": (
        "You've found a genuine tension. Which side do you think has more "
        "weight right now — and what would tip your judgment the other way?",
        "I asked you to weigh the tension because seeing both sides is real "
        "thinking, not just picking one.",
    ),
    "changed_mind": (
        "Good — you've revised your view. Name exactly what moved you. Honest "
        "intellectual growth is worth making explicit.",
        "I asked you to name the mover because recognizing why you changed is "
        "what makes the change stick.",
    ),
    "receded": (
        "No pressure — uncertainty is where real questions live. Say the part "
        "you're least sure about, and we'll look at it together.",
        "I met your uncertainty calmly because productive discomfort, not fear, "
        "is the right space for learning.",
    ),
    "example": (
        "A concrete example — that's excellent for grounding. Now zoom out: "
        "does your example actually prove the general claim, or could it be a "
        "special case that misleads you?",
        "I tested the example against the general claim to catch the classic "
        "mistake of one vivid case outweighing the pattern.",
    ),
    "question": (
        "Good question back. Answering your own confusion in your own words is "
        "often the strongest step — so, you ask {}\u2026 you'd say what?",
        "I returned the question to you because asking-and-answering your own "
        "doubt builds confident understanding.",
    ),
    "equal_valued": (
        "You're weighing two values — that's real ethics. What's the price of "
        "pricing one above the other? Who pays it?",
        "I asked about who pays because every value-priority has real costs, "
        "and naming them makes the choice honest.",
    ),
}


def pedagogy_for(move: str, session: "SocraticSession") -> dict:
    """Return {question, rationale} for the classified move."""
    question, rationale = _MOVE_PEDAGOGY.get(move, _MOVE_PEDAGOGY["claimed"])
    # Fill the 'question' move's placeholder with the student's own question if any
    if move == "question" and session.last_answer:
        try:
            question = question.format(session.last_answer.strip()[:30]) \
                if "{}" in question else question
        except Exception:
            pass
    return {"move": move, "question": question, "rationale": rationale}


def threadback(session: "SocraticSession", latest: str) -> str | None:
    """Cross-turn self-contradiction detection (offline heuristic)."""
    if len(session.student_answers) < 3:
        return None
    # crude contradiction: a later turn nods toward a different pole than an earlier one
    neg = ["not", "never", "no ", "actually not", "on second thought"]
    earlier = session.student_answers[0].lower()
    latest_l = (latest or "").lower()
    if any(w in latest_l for w in neg) and not any(w in earlier for w in neg):
        return (
            "I notice something worth holding up: earlier you seemed fairly "
            "settled, but now you're qualifying it strongly. Rather than call "
            "it a contradiction, let's look — what exactly changed between them? "
            "Refining is progress; let's make sure you can say what you refined."
        )
    return None


def momentum_summary(session: "SocraticSession") -> dict:
    """A lightweight 'reasoning momentum' tally for the student's sense of growth."""
    moves = [v.get("move") for v in (session.motion or {}).values()]
    return {
        "turns": session.turns,
        "arguments": moves.count("reasons") + moves.count("claimed"),
        "tensions_seen": moves.count("tension") + moves.count("equal_valued"),
        "refinements": moves.count("changed_mind") + moves.count("receded"),
    }


def reword_question(text: str) -> str:
    """Offline plainer-language re-cast of a philosophical question.
    Acknowledges the confusion and reframes simply — supporting, not condescending."""
    # Generic welcoming framing; keeps the question's thrust but plainer.
    return (
        "No trouble at all if this one feels heavy — let's take the jargon off. "
        "Put simply, I'm asking: " + text.rstrip("?") + "?"
    )


def teach_me(session: "SocraticSession") -> str:
    """Offline 'teach me' foundation: gives someone with zero background enough
    context to actually engage the question — what's at stake, the key terms,
    and who/what is being referenced. Frames it so they can then answer."""
    q = session.question.text
    node_hint = ""
    if session.prior_node:
        node_hint = (
            f"\n\nYou were just reading about {session.prior_node.replace('_', ' ')} — "
            f"keep that in mind; this connects from it."
        )
    return (
        "Let's give you a foundation so the question isn't a wall you can't climb. "
        f"\n\n**What we're really asking**\n{q}\n\n"
        "**Why it matters**\nThis is one of philosophy's oldest live questions — "
        "people have argued it for centuries, and there's no single agreed answer. "
        "That's not a flaw; it means it's deep enough to think about honestly. "
        "Different thinkers have reached very different conclusions, and part of "
        "engaging it well is hearing the strongest reasons on *both* sides "
        "before you form your own.\n\n"
        "**How to approach it**\nYou're not expected to already know the answer — "
        "you're expected to *reason about it*. A useful first step: name the "
        "two or three big ideas or values it's rubbing together, then ask "
        "yourself which one pulls you toward a side and why. "
        f"{node_hint}\n\n"
        "Now — what's your first honest leaning, even if it's shaky? That's a "
        "perfect place for us to start thinking together."
    )
