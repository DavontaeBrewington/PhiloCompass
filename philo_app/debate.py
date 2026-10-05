"""Debate mode for PhiloCompass.

Runs a structured, two-sided philosophical debate between two nodes
(thinkers/schools/concepts). The tutor alternates turns, and hands the
student the floor to weigh in. Works fully offline with curated canned
positions OR (when an LLM key is present) with real, argumentative turns.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import data_thinkers
from .socratic_engine import _DOMAIN_LABELS


# ──────────────────────────────────────────────────────────────────────────
#  Curated debate pairings + canned openers. When no LLM is available these
#  give a real, structured back-and-forth from stored positions.
# ──────────────────────────────────────────────────────────────────────────

# node_id -> list of (opener, key idea)
_DEBATE_POSITIONS = {
    "plato": [
        ("Justice is a harmony of the soul — right action flows from a well-ordered self.",
         "The Forms give us an objective standard for truth and goodness."),
        ("The unexamined life is not worth living.",
         "Knowledge, not opinion, is what a philosopher must build on."),
    ],
    "aristotle": [
        ("Virtue is a settled habit, a mean between extremes.",
         "Happiness (eudaimonia) is activity of the soul in accordance with virtue."),
        ("We acquire virtues by practicing them, like learning to play a flute.",
         "Ethics is about becoming, not just rules."),
    ],
    "kant": [
        ("Act only on maxims you could will as universal law.",
         "Moral worth lies in duty, not results — autonomy is reason giving law to itself."),
        ("Persons are ends in themselves, never mere means.",
         "Consequences can't make an act right; only the good will can."),
    ],
    "utilitarianism": [
        ("An act is right if it maximizes happiness for the greatest number.",
         "Pain and pleasure are the sovereign masters that ground all our judgments."),
        ("Consequences — not intentions — determine right and wrong.",
         "No act is good or bad in itself; context decides."),
    ],
    "sartre": [
        ("Existence precedes essence — you are what you make through your choices.",
         "We are condemned to be free; there is no fixed human nature to fall back on."),
        ("You are radically responsible, even for how the world seems to you.",
         "Bad faith is pretending you have no choice."),
    ],
    "nietzsche": [
        ("God is dead — we must revalue all values ourselves.",
         "Will to power is the drive behind all life and excellence."),
        ("Morality is a prison invented by the weak to tame the strong.",
         "The Übermensch creates their own law."),
    ],
    "hume": [
        ("All knowledge of fact traces to experience and custom.",
         "Reason is the slave of the passions — it can't ground morality on its own."),
        ("You can't get an 'ought' from an 'is'.",
         "The self is just a bundle of perceptions."),
    ],
    "stoicism": [
        ("Focus only on what is in your control.",
         "Virtue is the only good; externals are indifferent."),
        ("The obstacle is the way — adversity becomes material for character.",
         "Live according to nature and reason."),
    ],
}

_DEFAULT_POSITION = [
    ("Here's where I stand: I'll defend a view I hold with real conviction.",
     "Let's test it the way honest people test ideas — openly."),
]


# Positions for the newly added thinkers (so new debate pairings feel real
# even in fully-offline mode).
def _positions_for(node_id: str) -> list[tuple[str, str]]:
    return {
        "marx": [
            ("Material conditions shape consciousness — not the other way around.",
             "Freedom means ending alienation and the exploitation of labor, not just rights declared on paper."),
            ("History is the record of class struggle over the means of production.",
             "Justice is impossible while capital owns the power that labor creates."),
        ],
        "mills_liberty": [
            ("The only just reason to coerce someone is to prevent harm to others.",
             "Individual liberty is the engine of progress and truth; the harm principle sets its limit."),
            ("Higher pleasures outrank lower ones — a dissatisfied Socrates beats a satisfied fool.",
             "Free discussion is how we distinguish true from false opinions."),
        ],
        "hegel": [
            ("History is Spirit coming to know itself through conflict and synthesis.",
             "Freedom is not just doing what you like but the rational recognition of necessity."),
            ("The whole is the true; individuals are moments in a larger ethical life.",
             "Dialectics: every thesis breeds its opposite, and together they advance."),
        ],
        "schopenhauer": [
            ("The world is Will — a blind, endless striving that guarantees suffering.",
             "Desire can never be satisfied; peace comes only through denying the will."),
            ("Art, especially music, briefly lifts us out of willing.",
             "Optimism is a cruel illusion; the honest view of life is tragic."),
        ],
        "kierkegaard": [
            ("Truth is subjectivity — what matters is the passion of the individual's existing.",
             "The leap of faith cannot be justified by reason; it demands a risk of the whole self."),
            ("The crowd is untruth; the single individual is the category of authentic existence.",
             "Dread reveals our freedom and our responsibility."),
        ],
        "foucault": [
            ("Power is not owned by a sovereign — it circulates through knowledge and institutions.",
             "Discipline, surveillance, and 'normal' shape subjects as much as laws do."),
            ("Truth is produced by power; the archive is a site of struggle.",
             "Critique means exposing the hidden exclusions that make our categories seem natural."),
        ],
        "arendt": [
            ("The public realm is where we appear to one another and act — the space of freedom.",
             "Totalitarian evil is banal: it is done by bureaucrats who stop thinking.",
            ),
            ("Labor, work, and action are three distinct human activities.",
             "Thinking must keep judging, even against every received rule."),
        ],
        "spinoza": [
            ("God is Nature — mind and matter are two attributes of one substance.",
             "Freedom is understanding necessity; the free person acts from reason, not fear."),
            ("Democracy is the most natural regime because it most expresses reason.",
             "The emotions master us only when we misunderstand their causes."),
        ],
        "leibniz": [
            ("This is the best of all possible worlds — God chose it for maximal richness.",
             "Monads are windowless centers of perception harmonized by God's design."),
            ("Everything has a sufficient reason; nothing is arbitrary.",
             "The mind is not a blank slate — it contains innate principles."),
        ],
        "rousseau": [
            ("Man was born free, and everywhere he is in chains.",
             "The general will, not private interest, is the ground of legitimate authority."),
            ("Civilization corrupts our natural goodness.",
             "True freedom is obedience to a law one gives oneself."),
        ],
        "berkeley": [
            ("To be is to be perceived — there is no matter, only minds and their ideas.",
             "God is the universal perceiver holding the world in being."),
            ("Common sense and idealism actually agree; materialism is the wild theory.",
             "We never observe matter — only ideas."),
        ],
        "hegel_to_marx": [
            ("Hegel stood Spirit on its head — I stand it back on its feet.",
             "The dialectic is material: contradictions are in the economy, not in the mind."),
            ("Philosophy must change the world, not merely interpret it.",
             "Alienation is concrete — of worker from labor, product, and humanity."),
        ],
    }.get(node_id, _DEFAULT_POSITION)


# Well-known rivalries, plus their framing question.
_PAIRINGS = [
    # ── original ──
    ("kant", "utilitarianism", "Is an act right because it follows a moral law, or because of its consequences?"),
    ("hume", "kant", "Does reason ground morality, or is it always the servant of passion?"),
    ("plato", "aristotle", "Is the good real and objective, or grounded in the natural world and practice?"),
    ("sartre", "nietzsche", "Is radical freedom a burden to bear, or a power to be affirmed?"),
    ("nietzsche", "utilitarianism", "Are 'good' and 'evil' exhausted by consequences, or are they inventions of power?"),
    ("stoicism", "sartre", "Am I free to choose my world, or must I accept what is not in my control?"),
    ("hume", "nietzsche", "Is the self a fiction, or the creator of all value?"),
    # ── new: modern political / economic ──
    ("marx", "mills_liberty", "Is freedom found in collective self-determination, or in the liberty of each individual?"),
    ("marx", "hegel", "Is history driven by material struggle, or by the self-unfolding of Spirit?"),
    ("hegel", "kierkegaard", "Is the individual a moment in the system, or the one truth that matters?"),
    ("schopenhauer", "nietzsche", "Is the Will to be denied for peace, or affirmed as the will to power?"),
    ("kierkegaard", "nietzsche", "Is faith a leap into the absurd, or something the free spirit must overcome?"),
    ("foucault", "arendt", "Is freedom won in the public realm, or in resisting the power that shapes us?"),
    ("foucault", "marx", "Is power economic — owned by a class — or does it circulate through everything?"),
    # ── new: early modern metaphysics ──
    ("spinoza", "leibniz", "Is ultimate reality one undivided substance, or a harmony of many monads?"),
    ("spinoza", "hobbes", "Is freedom compatible with necessity, or is it merely the absence of external restraint?"),
    ("berkeley", "hume", "Is the world a mind, or just bundles of impressions in that mind?"),
    ("rousseau", "hobbes", "Is civil society our salvation from the state of nature, or our corruption of it?"),
]


def _position(node_id: str) -> str:
    pos = (_positions_for(node_id) or _DEFAULT_POSITION)[0]
    return pos[0]


def _key_idea(node_id: str) -> str:
    pos = (_positions_for(node_id) or _DEFAULT_POSITION)[0]
    return pos[1]


@dataclass
class Debate:
    a: str
    b: str
    prompt: str
    turn: int = 0  # 0 = A opens
    log: list[tuple[str, str]] = field(default_factory=list)
    active_side: str = ""  # "A" | "B" | "STUDENT"

    def next_speaker(self) -> str:
        return "A" if self.turn % 2 == 0 else "B"


def pick_pair() -> tuple[str, str, str]:
    import random

    a, b, prompt = random.choice(_PAIRINGS)
    return a, b, prompt


def pair_from_id(a: str, b: str) -> tuple[str, str, str] | None:
    for x, y, prompt in _PAIRINGS:
        if {x, y} == {a, b}:
            return x, y, prompt
    return None


def speaker_label(node_id: str) -> str:
    n = (data_thinkers.node_info(node_id) or {}).get("name", node_id)
    return n


def next_debate_turn(d: Debate, student_text: str | None = None) -> dict:
    """Return the next debate turn. When an LLM key is NOT present, uses
    curated canned positions for a real two-sided exchange."""
    a_name = speaker_label(d.a)
    b_name = speaker_label(d.b)

    if student_text is not None:
        # Student is weighing in; hand back to whichever side is due.
        speaker = d.next_speaker()
        side_id = d.a if speaker == "A" else d.b
        side_name = speaker_label(side_id)
        reply = f"{side_name}: Right — and that's exactly my concern. {_key_idea(side_id)} Think about this when you weigh your verdict."
        d.turn += 1
        d.log.append(("student", student_text))
        d.active_side = speaker
        return {"speaker": speaker, "name": side_name, "text": reply, "student": True}

    speaker = d.next_speaker()
    side_id = d.a if speaker == "A" else d.b
    side_name = speaker_label(side_id)
    if d.turn == 0:
        text = f"{side_name} ({_position(side_id)})"
    else:
        other_id = d.b if side_id == d.a else d.a
        other_name = speaker_label(other_id)
        text = f"{side_name}: {_position(side_id)} And that puts real pressure on {other_name}'s view — {_key_idea(side_id)}"
    d.turn += 1
    d.log.append((side_id, text))
    d.active_side = speaker
    return {"speaker": speaker, "name": side_name, "text": text, "student": False}
