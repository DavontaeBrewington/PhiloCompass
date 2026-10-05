"""PhiloCompass — concept & thinker constellation data.

A curated knowledge graph of philosophy: thinkers, concepts, their
lineage (who influenced whom / which school), and cross-links. This hands
the frontend enough content to render a meaningful interactive galaxy
map, and powers the "Thinker Lookup" panel, offline.
"""

from __future__ import annotations

# nodes: id -> {name, kind(thinker|concept|school), era, domain, blurb}
NODES = {
    # ── Ancient ──
    "plato": {
        "name": "Plato", "kind": "thinker", "era": "Ancient (c. 428–348 BCE)",
        "domain": "plato", "blurb": "Founded the Academy; Theory of Forms; the Republic. All philosophy since is 'a series of footnotes to Plato.'",
    },
    "socrates": {
        "name": "Socrates", "kind": "thinker", "era": "Ancient (c. 470–399 BCE)",
        "domain": "plato", "blurb": "The original Socratic method — questioned everything, taught by asking, died for it. The namesake of this app.",
    },
    "aristotle": {
        "name": "Aristotle", "kind": "thinker", "era": "Ancient (384–322 BCE)",
        "domain": "aristotle", "blurb": "Plato's student who grounded philosophy in the natural world; virtue ethics, logic, metaphysics.",
    },
    "stoicism": {
        "name": "Stoicism", "kind": "school", "era": "Hellenistic (c. 300 BCE)",
        "domain": "ethics", "blurb": "Virtue is the only good; focus on what you control. Zeno, Epictetus, Marcus Aurelius.",
    },
    "epictetus": {
        "name": "Epictetus", "kind": "thinker", "era": "Roman (c. 50–135 CE)",
        "domain": "ethics", "blurb": "Stoic slave-turned-teacher whose Discourses distill the art of living.",
    },
    "marcus_aurelius": {
        "name": "Marcus Aurelius", "kind": "thinker", "era": "Roman (121–180 CE)",
        "domain": "ethics", "blurb": "Philosopher-emperor; Meditations — Stoicism practiced at the helm of an empire.",
    },
    # ── Modern / political ──
    "descartes": {
        "name": "Descartes", "kind": "thinker", "era": "Early modern (1596–1650)",
        "domain": "epistemology", "blurb": "'I think, therefore I am.' Methodological doubt; mind–body dualism.",
    },
    "hobbes": {
        "name": "Hobbes", "kind": "thinker", "era": "Early modern (1588–1679)",
        "domain": "politics", "blurb": "Life in the state of nature is 'nasty, brutish, and short'; the Leviathan sovereign.",
    },
    "locke": {
        "name": "Locke", "kind": "thinker", "era": "Early modern (1632–1704)",
        "domain": "politics", "blurb": "Tabula rasa; life, liberty, and property; revolution justified against tyranny; personal identity via memory.",
    },
    "hume": {
        "name": "Hume", "kind": "thinker", "era": "Early modern (1711–1776)",
        "domain": "epistemology", "blurb": "Radical empiricist; the self is a 'bundle of perceptions'; is–ought gap; causation as habit.",
    },
    "kant": {
        "name": "Kant", "kind": "thinker", "era": "Modern (1724–1804)",
        "domain": "ethics", "blurb": "Categorical imperative — act only on maxims you could will universal; autonomy and duty.",
    },
    "nietzsche": {
        "name": "Nietzsche", "kind": "thinker", "era": "Modern (1844–1900)",
        "domain": "existentialism", "blurb": "'God is dead.' Will to power, Übermensch, eternal recurrence; revalued all values.",
    },
    "sartre": {
        "name": "Sartre", "kind": "thinker", "era": "20th century (1905–1980)",
        "domain": "existentialism", "blurb": "'Existence precedes essence.' Radical freedom, bad faith, radical responsibility.",
    },
    "rawls": {
        "name": "Rawls", "kind": "thinker", "era": "20th century (1921–2002)",
        "domain": "politics", "blurb": "A Theory of Justice; the veil of ignorance; justice as fairness.",
    },
    # ── Concepts ──
    "the_forms": {
        "name": "Theory of Forms", "kind": "concept", "era": "Ancient",
        "domain": "plato", "blurb": "Perfect, changeless abstract Forms; particular things are imperfect copies.",
    },
    "eudaimonia": {
        "name": "Eudaimonia", "kind": "concept", "era": "Ancient",
        "domain": "aristotle", "blurb": "Flourishing — the highest good, achieved by living a life of rational activity in accordance with virtue.",
    },
    "categorical_imperative": {
        "name": "Categorical Imperative", "kind": "concept", "era": "Modern",
        "domain": "ethics", "blurb": "Kant's unconditional moral law that reason gives to itself.",
    },
    "social_contract": {
        "name": "Social Contract", "kind": "concept", "era": "Early modern",
        "domain": "politics", "blurb": "The idea that legitimate authority derives from the consent of the governed.",
    },
    "veil_of_ignorance": {
        "name": "Veil of Ignorance", "kind": "concept", "era": "20th century",
        "domain": "politics", "blurb": "Rawls: design principles of justice without knowing your own place in society.",
    },
    "tabula_rasa": {
        "name": "Tabula Rasa", "kind": "concept", "era": "Early modern",
        "domain": "epistemology", "blurb": "The mind as a blank slate — all knowledge from experience (Locke).",
    },
    "dualism": {
        "name": "Mind–Body Dualism", "kind": "concept", "era": "Early modern",
        "domain": "metaphysics", "blurb": "Mind and body are distinct substances (Descartes); the hard problem of their interaction.",
    },
    "bundle_theory": {
        "name": "Bundle Theory of Self", "kind": "concept", "era": "Early modern",
        "domain": "metaphysics", "blurb": "The self is not a thing but a collection of perceptions (Hume).",
    },
    "free_will": {
        "name": "Free Will", "kind": "concept", "era": "Across eras",
        "domain": "metaphysics", "blurb": "Do we have the ability to choose otherwise? The battleground of determinism, compatibilism, libertarianism.",
    },
    "existentialism": {
        "name": "Existentialism", "kind": "school", "era": "20th century",
        "domain": "existentialism", "blurb": "Existence precedes essence; meaning is created through choice, not inherited.",
    },
    "ubermensch": {
        "name": "Übermensch", "kind": "concept", "era": "Modern",
        "domain": "existentialism", "blurb": "Nietzsche's ideal of one who affirms life fully, masters their own values, overcomes the last man.",
    },
    "epistemology": {
        "name": "Epistemology", "kind": "concept", "era": "Across eras",
        "domain": "epistemology", "blurb": "The study of knowledge — what it is, how we get it, and what we can be sure of.",
    },
    "metaphysics": {
        "name": "Metaphysics", "kind": "concept", "era": "Across eras",
        "domain": "metaphysics", "blurb": "The study of ultimate reality — being, time, self, God, and the nature of existence itself.",
    },
    "ethics": {
        "name": "Ethics", "kind": "concept", "era": "Across eras",
        "domain": "ethics", "blurb": "The study of right and wrong conduct, and what makes a life good.",
    },
    "utilitarianism": {
        "name": "Utilitarianism", "kind": "school", "era": "Modern",
        "domain": "ethics", "blurb": "The greatest happiness for the greatest number; consequences are all that matter (Bentham, Mill).",
    },
    "justice": {
        "name": "Justice", "kind": "concept", "era": "Across eras",
        "domain": "politics", "blurb": "What people are owed; fairness in distribution, punishment, and institutions.",
    },

    # ── New ancient / Hellenistic ──
    "sophists": {
        "name": "The Sophists", "kind": "school", "era": "Ancient",
        "domain": "politics", "blurb": "Relativist teachers of rhetoric and persuasion — Socrates' great rivals.",
    },
    "alcibiades": {
        "name": "Alcibiades", "kind": "thinker", "era": "Ancient (450–404 BCE)",
        "domain": "plato", "blurb": "Brilliant, scandalous Athenian statesman; the living test of Socratic virtue against ambition.",
    },
    "cyrenaics": {
        "name": "Cyrenaics", "kind": "school", "era": "Ancient (c. 4th c. BCE)",
        "domain": "ethics", "blurb": "Ancient hedonists — Aristippus held that immediate pleasure is the only intrinsic good.",
    },
    "epicurus": {
        "name": "Epicurus", "kind": "thinker", "era": "Hellenistic (341–270 BCE)",
        "domain": "ethics", "blurb": "Pleasure is the absence of pain and disturbance; friendship and simple living; atoms and the gods' indifference.",
    },
    "lucretius": {
        "name": "Lucretius", "kind": "thinker", "era": "Roman (c. 99–55 BCE)",
        "domain": "metaphysics", "blurb": "Poet of Epicurean atomism in On the Nature of Things; the universe is just atoms and void.",
    },
    "plotinus": {
        "name": "Plotinus", "kind": "thinker", "era": "Roman (204–270 CE)",
        "domain": "metaphysics", "blurb": "Neoplatonist whose One radiates all reality — the bridge from Plato to mysticism and medieval thought.",
    },
    "neoplatonism": {
        "name": "Neoplatonism", "kind": "school", "era": "Late antique (c. 3rd c. CE)",
        "domain": "metaphysics", "blurb": "From the One flows Intellect, Soul, then matter — reality as emanation. Plotinus, Proclus, Iamblichus.",
    },
    "sextus_empiricus": {
        "name": "Sextus Empiricus", "kind": "thinker", "era": "Roman (c. 160–210 CE)",
        "domain": "epistemology", "blurb": "Systematized ancient Scepticism — suspend judgment, and find peace (ataraxia).",
    },
    "scepticism": {
        "name": "Scepticism", "kind": "school", "era": "Ancient",
        "domain": "epistemology", "blurb": "Pyrrho and Sextus: no belief is certain; suspend judgment to live untroubled.",
    },

    # ── New early modern ──
    "spinoza": {
        "name": "Spinoza", "kind": "thinker", "era": "Early modern (1632–1677)",
        "domain": "metaphysics", "blurb": "God is Nature — one infinite substance with mind and matter as attributes; freedom as understanding necessity.",
    },
    "monism": {
        "name": "Monism", "kind": "concept", "era": "Across eras",
        "domain": "metaphysics", "blurb": "Reality is ultimately one kind of thing — matter (materialism), or mind, or spirit (Spinoza's substance).",
    },
    "pascal": {
        "name": "Pascal", "kind": "thinker", "era": "Early modern (1623–1662)",
        "domain": "epistemology", "blurb": "Wager on God; the heart has reasons reason knows not of; anxious, fragmentary human greatness.",
    },
    "leibniz": {
        "name": "Leibniz", "kind": "thinker", "era": "Early modern (1646–1716)",
        "domain": "metaphysics", "blurb": "Monads, pre-established harmony, the best of all possible worlds; a giant of logic and calculus.",
    },
    "vico": {
        "name": "Vico", "kind": "thinker", "era": "Early modern (1668–1744)",
        "domain": "politics", "blurb": "Histories are made by humans, not just fate — we can understand them from within; cycles of civilizations.",
    },
    "rousseau": {
        "name": "Rousseau", "kind": "thinker", "era": "Early modern (1712–1778)",
        "domain": "politics", "blurb": "'Man was born free, and everywhere he is in chains.' The general will; natural goodness corrupted by society.",
    },
    "berkeley": {
        "name": "Berkeley", "kind": "thinker", "era": "Early modern (1685–1753)",
        "domain": "epistemology", "blurb": "Idealism — to be is to be perceived (esse est percipi); there is no matter, only minds and God.",
    },
    "idealism": {
        "name": "Idealism", "kind": "school", "era": "Early modern – Modern",
        "domain": "metaphysics", "blurb": "Reality is mind-dependent — from Berkeley through Kant to German Idealism.",
    },

    # ── New Modern / 19th century ──
    "hegel": {
        "name": "Hegel", "kind": "thinker", "era": "Modern (1770–1831)",
        "domain": "metaphysics", "blurb": "History is the self-unfolding of Spirit through thesis, antithesis, synthesis; absolute knowledge.",
    },
    "schopenhauer": {
        "name": "Schopenhauer", "kind": "thinker", "era": "Modern (1788–1860)",
        "domain": "metaphysics", "blurb": "The world as Will and Representation — a blind striving Will, and art as a temporary escape.",
    },
    "kierkegaard": {
        "name": "Kierkegaard", "kind": "thinker", "era": "Modern (1813–1855)",
        "domain": "existentialism", "blurb": "The leap of faith; dread and the individual's passionate choosing; truth as subjectivity.",
    },
    "mills_liberty": {
        "name": "Mill", "kind": "thinker", "era": "Modern (1806–1873)",
        "domain": "politics", "blurb": "Utilitarian and defender of liberty — the harm principle; higher pleasures; equality across the sexes.",
    },
    "marx": {
        "name": "Marx", "kind": "thinker", "era": "Modern (1818–1883)",
        "domain": "politics", "blurb": "Material conditions shape consciousness; alienation, class struggle, and the critique of capitalism.",
    },
    "darwin": {
        "name": "Darwin", "kind": "thinker", "era": "Modern (1809–1882)",
        "domain": "metaphysics", "blurb": "Natural selection recasts purpose, mind, and ethics — earth-shaking for philosophy of biology and of mind.",
    },
    "pragmatism": {
        "name": "Pragmatism", "kind": "school", "era": "Modern (19th c.)",
        "domain": "epistemology", "blurb": "Peirce, James, Dewey: the meaning of an idea is its practical consequences; truth is what works.",
    },
    "william_james": {
        "name": "James", "kind": "thinker", "era": "Modern (1842–1910)",
        "domain": "epistemology", "blurb": "The stream of consciousness; the will to believe; radical empiricism and pragmatism.",
    },

    # ── New 20th century / contemporary ──
    "wittgenstein": {
        "name": "Wittgenstein", "kind": "thinker", "era": "20th century (1889–1951)",
        "domain": "epistemology", "blurb": "Philosophy as therapy — language games and forms of life; 'whereof one cannot speak, thereof one must be silent.'",
    },
    "popper": {
        "name": "Popper", "kind": "thinker", "era": "20th century (1902–1994)",
        "domain": "epistemology", "blurb": "Falsifiability marks science; the open society and its enemies.",
    },
    "heidegger": {
        "name": "Heidegger", "kind": "thinker", "era": "20th century (1889–1976)",
        "domain": "existentialism", "blurb": "Being and Time; Dasein thrown into the world, facing its own death; care and authenticity.",
    },
    "arendt": {
        "name": "Arendt", "kind": "thinker", "era": "20th century (1906–1975)",
        "domain": "politics", "blurb": "The banality of evil; the public sphere; labor, work, and action; totalitarianism's machinery.",
    },
    "foucault": {
        "name": "Foucault", "kind": "thinker", "era": "20th century (1926–1984)",
        "domain": "politics", "blurb": "Power isn't just top-down — it runs through knowledge, discipline, and institutions; the panopticon.",
    },
    "nussbaum": {
        "name": "Nussbaum", "kind": "thinker", "era": "20th century – present (b. 1947)",
        "domain": "ethics", "blurb": "Capabilities approach; emotions and the fragility of goodness; cosmopolitanism and literature as moral philosophy.",
    },
    "kripke": {
        "name": "Kripke", "kind": "thinker", "era": "20th century (1940–2022)",
        "domain": "metaphysics", "blurb": "Naming and Necessity — rigid designators, possible worlds, and the limits of description.",
    },
    "machine_ethics": {
        "name": "Machine Ethics", "kind": "concept", "era": "21st century",
        "domain": "ethics", "blurb": "Can (and should) we build moral machines? Trolleys, alignment, and the ethics of artificial agents.",
    },
    "philosophy_of_mind": {
        "name": "Philosophy of Mind", "kind": "concept", "era": "20th century – present",
        "domain": "metaphysics", "blurb": "Consciousness, intentionality, qualia; the hard problem and the gulf between brain states and felt experience.",
    },
    "the_hard_problem": {
        "name": "The Hard Problem", "kind": "concept", "era": "20th century – present",
        "domain": "metaphysics", "blurb": "Why is there subjective experience at all? Chalmers; the explanatory gap beyond computation.",
    },
    "explanatory_gap": {
        "name": "Explanatory Gap", "kind": "concept", "era": "20th century – present",
        "domain": "metaphysics", "blurb": "The felt chasm between neural functions and conscious experience.",
    },
    "algorithmic_fairness": {
        "name": "Algorithmic Fairness", "kind": "concept", "era": "21st century",
        "domain": "politics", "blurb": "Whether and how automated systems can be just — bias, transparency, and the ethics of code that governs.",
    },
}


# Helpers
KIND_ORDER = {"thinker": 0, "school": 1, "concept": 2}


def node_info(nid: str) -> dict | None:
    return NODES.get(nid)


def all_nodes() -> dict:
    nodes = {}
    for k, v in NODES.items():
        nodes[k] = {**v, "id": k, "eraOrder": _era_order(v.get("era"))}
    return nodes


_ERA_ORDER = {
    "Ancient": 0,
    "Hellenistic": 1,
    "Roman": 2,
    "Early modern": 3,
    "Modern": 4,
    "20th century": 5,
    "Across eras": 0,  # timeless hubs appear from the start
}


def _era_order(era_label: str) -> int:
    if not era_label:
        return 0
    # parse first word of the era (e.g. "Ancient (c. 428...)" -> "Ancient")
    head = era_label.split("(")[0].strip()
    return _ERA_ORDER.get(head, 3)


# ──────────────────────────────────────────────────────────────────────────
#  Curated learning paths — guided sequences a teacher can assign.
#  Each step is a node whose Socratic dialogue seeds the exploration.
# ──────────────────────────────────────────────────────────────────────────

LEARNING_PATHS = {
    "ethics_introduction": {
        "title": "Ethics from the Ground Up",
        "description": "Start with your own moral intuitions, then meet the three great ethical systems — consequences, duty, and virtue — and try to synthesize your own position.",
        "steps": [
            ("ethics", "Why anything be right or wrong at all?"),
            ("utilitarianism", "The greatest happiness"),
            ("categorical_imperative", "Duty and universal law"),
            ("eudaimonia", "Virtue and flourishing"),
            ("justice", "Fairness and the common good"),
        ],
    },
    "what_can_we_know": {
        "title": "What Can We Know?",
        "description": "A short epistemology journey: where knowledge comes from, what doubt teaches us, and whether reason or experience is the true source.",
        "steps": [
            ("epistemology", "What counts as knowledge?"),
            ("descartes", "Doubting into certainty"),
            ("tabula_rasa", "The mind as blank slate"),
            ("hume", "Empiricism and its limits"),
            ("descartes", "Reason as the source"),
        ],
    },
    "meaning_and_self": {
        "title": "Meaning, Freedom & the Self",
        "description": "Do we have free will? Is there a self underneath? Existentialists thought meaning is built, not found.",
        "steps": [
            ("free_will", "Am I really free?"),
            ("dualism", "Mind and body"),
            ("bundle_theory", "Is there a self?"),
            ("existentialism", "Existence precedes essence"),
            ("sartre", "Radical freedom"),
        ],
    },

    # ── NEW: built on the expanded graph ──
    "existentialism_journey": {
        "title": "The Existentialist Turn",
        "description": "From Kierkegaard's dread to the death of God, Sartre's radical freedom, and Heidegger's being-toward-death — see how 19th-century disquiet became a 20th-century way of life.",
        "steps": [
            ("pascal", "The anxious greatness of a thinking reed"),
            ("kierkegaard", "The leap of faith"),
            ("nietzsche", "God is dead"),
            ("heidegger", "Being-toward-death"),
            ("sartre", "Condemned to be free"),
            ("existentialism", "Existence precedes essence"),
        ],
    },
    "power_and_society": {
        "title": "Power & the Modern State",
        "description": "From Hobbes' Leviathan and Rousseau's general will, through Marx's material critique, to Foucault's insight that power circulates through us all.",
        "steps": [
            ("hobbes", "The leviathan sovereign"),
            ("rousseau", "The general will"),
            ("social_contract", "Why we hand over freedom"),
            ("marx", "Material conditions & alienation"),
            ("foucault", "Power that circulates"),
            ("arendt", "The public realm"),
            ("justice", "What we are owed"),
        ],
    },
    "mind_and_machine": {
        "title": "Mind & Machine",
        "description": "A contemporary run: is there a hard problem of consciousness, and can (or should) we build machines that think and act morally?",
        "steps": [
            ("dualism", "Mind and body"),
            ("philosophy_of_mind", "Consciousness & qualia"),
            ("the_hard_problem", "Why experience at all?"),
            ("explanatory_gap", "The gap beyond computation"),
            ("machine_ethics", "Building moral machines"),
            ("algorithmic_fairness", "Justice in code"),
        ],
    },
    "raging_moderns": {
        "title": "Hegel to Nietzsche: The German Earthquake",
        "description": "The most dramatic century in philosophy — from Hegel's absolute system, through Schopenhauer's dark Will and Marx's inversion, to Nietzsche's revaluation of all values.",
        "steps": [
            ("hegel", "Spirit unfolds through history"),
            ("schopenhauer", "The blind Will"),
            ("marx", "Hegel stood on his head"),
            ("kierkegaard", "Against the system"),
            ("nietzsche", "Revalue all values"),
        ],
    },
}


def learning_paths() -> dict:
    # Drop steps whose node we removed from the graph (placeholder names).
    cleaned = {}
    for name, path in LEARNING_PATHS.items():
        steps = [s for s in path["steps"] if s[0] in NODES]
        cleaned[name] = {**path, "steps": steps}
    return cleaned


# Quick-look glossary: term -> one-line definition. Used for inline tooltips.
GLOSSARY = {
    "epistemology": "The study of knowledge — what it is, where it comes from, how to be sure.",
    "metaphysics": "The study of ultimate reality — being, time, self, and what exists.",
    "ethics": "The study of right and wrong, and what makes a life go well.",
    "ontology": "The branch of metaphysics asking what things exist and what they are.",
    "determinism": "The view that every event, including choice, is caused by prior events.",
    "compatibilism": "The view that free will is compatible with determinism.",
    "libertarianism": "In free will, the view that we can genuinely choose otherwise.",
    "dualism": "The view that mind and body are two fundamentally different things.",
    "monism": "The view that reality is one kind of thing (matter, mind, or spirit).",
    "empiricism": "Knowledge comes primarily from sensory experience.",
    "rationalism": "Knowledge can be gained primarily from reason, independent of experience.",
    "tabula_rasa": "Latin for 'blank slate' — the mind begins empty (Locke).",
    "utilitarianism": "An act is right if it produces the greatest happiness for the greatest number.",
    "deontology": "Ethics based on duty and rules, regardless of consequences.",
    "virtue ethics": "Focuses on character — what a virtuous person would do.",
    "teleology": "Explaining things by their purpose or end (telos).",
    "phenomenology": "Studying experience as it is lived from the first-person point of view.",
    "existentialism": "Existence precedes essence — meaning is created through choice.",
    "theodicy": "The attempt to reconcile God's goodness with evil and suffering.",
    "aporia": "A state of puzzlement or dead-end in inquiry (a Socratic favourite).",
    "elenchus": "Socrates' method of cross-examining a view into contradiction.",
    "dialectic": "Reasoning through opposing positions to reach a truer view.",
    "syllogism": "A form of deductive argument: major + minor premise → conclusion.",
    "categorical imperative": "Kant's unconditional moral law, given by reason to itself.",
    "eudaimonia": "Flourishing — the highest human good in Aristotle.",
    "the forms": "Plato's perfect, changeless realities that particular things imitate.",
    "ubermensch": "Nietzsche's ideal one who overcomes themselves and affirms life.",
    "bad faith": "Sartre: denying our freedom and responsibility to avoid anxiety.",
    "the sublime": "An overwhelming, awe-filled experience of greatness or beauty.",
}


def glossary() -> dict[str, str]:
    return dict(GLOSSARY)


# ──────────────────────────────────────────────────────────────────────────
#  Lineage / influence edges: from -> to  (from influenced / shaped to)
# ──────────────────────────────────────────────────────────────────────────

INFLUENCE_EDGES = [
    ("socrates", "plato"),
    ("plato", "aristotle"),
    ("aristotle", "stoicism"),
    ("socrates", "stoicism"),
    ("plato", "the_forms"),
    ("plato", "dualism"),  # indirect, but conceptually tied
    ("aristotle", "eudaimonia"),
    ("stoicism", "epictetus"),
    ("stoicism", "marcus_aurelius"),
    ("descartes", "dualism"),
    ("hume", "bundle_theory"),
    ("descartes", "tabula_rasa"),
    ("locke", "tabula_rasa"),
    ("hobbes", "social_contract"),
    ("locke", "social_contract"),
    ("kant", "categorical_imperative"),
    ("kant", "utilitarianism"),  # critical response
    ("hume", "kant"),  # "awakened from dogmatic slumber"
    ("kant", "nietzsche"),
    ("nietzsche", "existentialism"),
    ("nietzsche", "ubermensch"),
    ("existentialism", "sartre"),
    ("rawls", "veil_of_ignorance"),
    ("rawls", "justice"),
    ("kant", "free_will"),
    ("descartes", "epistemology"),
    ("hume", "epistemology"),
    ("plato", "ethics"),
    ("aristotle", "ethics"),
    ("kant", "ethics"),
    ("utilitarianism", "ethics"),
    # ── new ancient / Hellenistic lineages ──
    ("sophists", "socrates"),           # Socrates reacted against the sophists
    ("socrates", "scepticism"),
    ("plato", "plotinus"),              # Neoplatonism reads through Plato
    ("plotinus", "neoplatonism"),
    ("plato", "neoplatonism"),
    ("socrates", "cyrenaics"),          # Socratic circle split into hedonists
    ("cyrenaics", "epicurus"),
    ("epicurus", "lucretius"),
    # ── new early-modern lineages ──
    ("descartes", "spinoza"),
    ("spinoza", "monism"),
    ("descartes", "leibniz"),
    ("leibniz", "idealism"),
    ("berkeley", "idealism"),
    ("kant", "idealism"),               # Kant's transcendental turn
    ("locke", "berkeley"),
    ("hobbes", "rousseau"),
    ("rousseau", "rawls"),              # social-contract revival
    ("rousseau", "marx"),
    ("hume", "pragmatism"),
    # ── new modern lineages ──
    ("kant", "hegel"),
    ("hegel", "marx"),
    ("kant", "schopenhauer"),
    ("schopenhauer", "nietzsche"),
    ("hegel", "kierkegaard"),
    ("kierkegaard", "existentialism"),
    ("darwin", "pragmatism"),
    ("darwin", "philosophy_of_mind"),
    ("mills_liberty", "utilitarianism"),
    ("mills_liberty", "nussbaum"),
    ("pascal", "kierkegaard"),          # the leap
    ("marx", "foucault"),               # materialist critique of power
    # ── new 20th-century lineages ──
    ("wittgenstein", "popper"),         # Vienna circle & beyond
    ("heidegger", "existentialism"),
    ("foucault", "algorithmic_fairness"),
    ("nussbaum", "justice"),
    ("utilitarianism", "algorithmic_fairness"),
    ("philosophy_of_mind", "the_hard_problem"),
    ("philosophy_of_mind", "explanatory_gap"),
    ("the_hard_problem", "explanatory_gap"),
    ("ethics", "machine_ethics"),
    ("machine_ethics", "algorithmic_fairness"),
]


# ──────────────────────────────────────────────────────────────────────────
#  Related-concept edges: simple conceptual proximity (undirected)
# ──────────────────────────────────────────────────────────────────────────

RELATED_EDGES = [
    ("epistemology", "ethics"),
    ("epistemology", "metaphysics"),
    ("metaphysics", "free_will"),
    ("free_will", "ethics"),
    ("justice", "social_contract"),
    ("social_contract", "veil_of_ignorance"),
    ("justice", "veil_of_ignorance"),
    ("existentialism", "free_will"),
    ("existentialism", "ethics"),
    ("dualism", "free_will"),
    ("bundle_theory", "dualism"),
    ("the_forms", "metaphysics"),
    ("eudaimonia", "ethics"),
    ("categorical_imperative", "ethics"),
    ("tabula_rasa", "epistemology"),
    ("ubermensch", "existentialism"),
    # ── new related edges ──
    ("spinoza", "monism"),
    ("idealism", "metaphysics"),
    ("scepticism", "epistemology"),
    ("philosophy_of_mind", "the_hard_problem"),
    ("wittgenstein", "epistemology"),
    ("hegel", "metaphysics"),
    ("schopenhauer", "metaphysics"),
    ("kierkegaard", "existentialism"),
    ("pragmatism", "epistemology"),
    ("machine_ethics", "ethics"),
    ("machine_ethics", "philosophy_of_mind"),
    ("algorithmic_fairness", "justice"),
    ("marx", "justice"),
    ("eudaimonia", "nussbaum"),
    ("the_forms", "neoplatonism"),
    ("dualism", "monism"),
    ("existentialism", "kierkegaard"),
    ("hegel", "idealism"),
    ("utilitarianism", "machine_ethics"),
]


def lineage_edges() -> list[tuple[str, str]]:
    return [e for e in INFLUENCE_EDGES if e[0] in NODES and e[1] in NODES]


def related_edges() -> list[tuple[str, str]]:
    return [e for e in RELATED_EDGES if e[0] in NODES and e[1] in NODES]


# Human-readable rationale for each influence edge (used in the UI to
# explain *why* two nodes connect — turns decoration into pedagogy).
EDGE_RATIONALE = {
    ("socrates", "plato"): "Plato immortalized Socrates as the protagonist of every dialogue.",
    ("plato", "aristotle"): "Aristotle studied at the Academy but grounded Forms in the natural world.",
    ("socrates", "the_forms"): "Socrates' probing for definitions seeds Plato's perfect Forms.",
    ("plato", "the_forms"): "The Theory of Forms is Plato's central doctrine.",
    ("aristotle", "stoicism"): "Stoic virtue (aretē) echoes Aristotle's account of the good life.",
    ("plato", "dualism"): "Plato's soul/body split is an ancestor of mind-body dualism.",
    ("aristotle", "eudaimonia"): "Happy flourishing is the whole of Aristotle's ethics.",
    ("stoicism", "epictetus"): "Epictetus systematized Stoic practice for everyday life.",
    ("stoicism", "marcus_aurelius"): "The Meditations are Stoicism exercised at the height of power.",
    ("descartes", "dualism"): "Descartes made the mind/body split explicit and famous.",
    ("hume", "bundle_theory"): "Hume dissolved the self into a bundle of perceptions.",
    ("descartes", "tabula_rasa"): "Descartes doubted everything, clearing the mind of innate ideas.",
    ("locke", "tabula_rasa"): "Locke's 'blank slate' is the empiricist theory of mind.",
    ("hobbes", "social_contract"): "Hobbes founded modern social-contract theory.",
    ("locke", "social_contract"): "Locke revised the contract to protect life, liberty, property.",
    ("kant", "categorical_imperative"): "Kant's unconditional moral law is the categorical imperative.",
    ("kant", "utilitarianism"): "Kant's rivals — Bentham and Mill — measured acts by consequences.",
    ("hume", "kant"): "Hume, Kant said, 'awakened me from my dogmatic slumber.'",
    ("kant", "nietzsche"): "Nietzsche rebelled against Kant's universal moral law.",
    ("nietzsche", "existentialism"): "Nietzsche's death of God and will to power feed existentialism.",
    ("nietzsche", "ubermensch"): "The Übermensch is Nietzsche's ideal of self-overcoming.",
    ("existentialism", "sartre"): "Sartre's 'existence precedes essence' is existentialism's slogan.",
    ("rawls", "veil_of_ignorance"): "Fair principles are chosen behind the veil of ignorance.",
    ("rawls", "justice"): "Rawls' great theme is justice as fairness.",
    ("kant", "free_will"): "Kant grounded freedom in autonomy under self-given law.",
    ("descartes", "epistemology"): "Descartes made 'what can I know?' the founding question.",
    ("hume", "epistemology"): "Hume's empiricism shaped all later theories of knowledge.",
    ("plato", "ethics"): "Plato asked why we should be just at all.",
    ("aristotle", "ethics"): "Aristotle's virtues define the ethical tradition.",
    ("kant", "ethics"): "Kant's duty-based ethics is a third great school.",
    ("utilitarianism", "ethics"): "Consequentialist ethics matured through utilitarianism.",
}


def all_edges() -> list[dict]:
    out = []
    for a, b in lineage_edges():
        out.append({"from": a, "to": b, "type": "influence", "rationale": EDGE_RATIONALE.get((a, b), "")})
    for a, b in related_edges():
        out.append({"from": a, "to": b, "type": "related", "rationale": ""})
    return out
