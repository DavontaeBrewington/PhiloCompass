"""LLM-backed Socratic dialogue for PhiloCompass.

When an OpenAI-compatible key is present (OPENAI_API_KEY), this module
turns the recorded student answers from `socratic_engine` into real,
adaptive Socratic follow-ups — the model Socratic teacher. When no key is
present, callers fall back to the offline engine's curated followups, so
the app never breaks and never begs for credentials.
"""

from __future__ import annotations

import os

from .socratic_engine import SocraticSession, _DOMAIN_LABELS


def _client():
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("No OPENAI_API_KEY set")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def _domain_meta(domain: str) -> str:
    return _DOMAIN_LABELS.get(domain, domain)


def llm_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def socratic_reply(session: SocraticSession, latest_answer: str, pedagogy: dict | None = None) -> str:
    """Produce a Socratic follow-up informed by the classified reasoning move.
    Raises on failure; callers handle fallback."""
    client = _client()
    model = os.environ.get("SOCRATES_MODEL", "route-llm")

    pedagogy = pedagogy or {}
    move = pedagogy.get("move", "")
    system = (
        "You are a patient, constructivist Socratic teacher for undergraduate "
        "philosophy. You build the student's knowledge on what they ALREADY know "
        "rather than lecturing. You respond to each answer with ONE probing "
        "question that pushes them where their THINKING is, not where a script "
        "says to go. "
    )
    if move:
        system += (
            f"The last answer was classified as a '{move}' reasoning move "
            "(claimed / reasons / tension / changed_mind / receded / example / "
            "question / equal_valued). Steer your next question accordingly: if "
            "they claimed, ask why; if they gave a reason, probe a hidden "
            "assumption; if they found a tension, ask them to weigh it; if they "
            "changed their mind, ask what moved them; if they receded, gently "
            "reassure and ask for the least-certain part; if they used an "
            "example, test it against the general claim. "
        )
    system += (
        "When they hit the edge of what they can derive alone, offer a small "
        "concrete handhold (a tiny example) that lets them take the next step "
        "THEMSELVES, then hand it back with a question. Occasionally ask them to "
        "re-express the core idea in their own words (retrieval), and to say why "
        "they believe what they do (metacognition) — but not every turn. Keep "
        "follow-ups to 1-2 sentences. Ground your nudge in the student's exact "
        "words. Use plain text only."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Topic ({_domain_meta(session.domain)}):\n{session.question.text}"},
    ]
    for i, ans in enumerate(session.student_answers):
        messages.append({"role": "user", "content": f"Student ({i + 1}):\n{ans}"})
    messages.append(
        {"role": "user", "content": (
            "Now respond to the student's most recent answer with a single Socratic "
            f"follow-up question:\n\nStudent ({len(session.student_answers)}):\n{latest_answer}"
        )}
    )

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.85,
        max_tokens=180,
    )
    return resp.choices[0].message.content.strip()


def connect_hint(session: SocraticSession) -> str | None:
    """LLM 'connect it to you' scaffold — anchor the new idea to prior learning."""
    if not session.prior_node:
        return None
    try:
        client = _client()
        model = os.environ.get("SOCRATES_MODEL", "route-llm")
        prior = session.prior_node.replace("_", " ")
        system = (
            "You are a constructivist learning designer. In ONE short sentence, "
            "help a student connect the question they are about to wrestle with "
            "to the topic they just finished exploring. Make the link concrete "
            "('this pushes back on…', 'this builds on…', 'this is the flip side "
            "of…'). No lecture, plain text, max ~40 words."
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Just explored: {prior}. New question: {session.question.text}"},
            ],
            temperature=0.8,
            max_tokens=90,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def reword_question(text: str, session: SocraticSession) -> str | None:
    """LLM plainer-language re-cast of the current question."""
    if not text:
        return None
    try:
        client = _client()
        model = os.environ.get("SOCRATES_MODEL", "route-llm")
        system = (
            "You are a warm, patient philosophy teacher. Re-state the student's "
            "question in plain, everyday language they can grasp — no jargon, no "
            "new philosophical vocabulary. Keep it SHORT (1-2 sentences), keep the "
            "same intent, and do NOT answer it. Begin with a gentle, encouraging "
            "line. Plain text only."
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"The student is confused by this question; reword it plainly:\n{text}"},
            ],
            temperature=0.7,
            max_tokens=120,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None


def teach_me(session: SocraticSession) -> str | None:
    """LLM 'teach me' foundation — a full, clear run-down of what's being asked
    for someone with zero background, so they have a platform to reason from."""
    try:
        client = _client()
        model = os.environ.get("SOCRATES_MODEL", "route-llm")
        prior = session.prior_node.replace("_", " ") if session.prior_node else "none"
        system = (
            "You are a gifted, accessible philosophy teacher. The student has "
            "little or no background on this question. In a warm, plain, "
            "structured answer: "
            "1) explain, in everyday words, what the question is really asking and why it matters; "
            "2) define the 2-3 key terms or who/what is referenced with a one-line sense of each; "
            "3) lay out the two or three main stances philosophers have taken in a sentence or two each; "
            "4) end by inviting the student's own first honest lean, even if shaky. "
            "Use bold headers. Keep it genuinely clear, no dense jargon. Then gently ask them to take a first position so we can keep thinking."
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": f"Question: {session.question.text}. Prior topic explored: {prior}."},
            ],
            temperature=0.7,
            max_tokens=520,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None
