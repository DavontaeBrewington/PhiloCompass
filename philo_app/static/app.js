/* ══════════════════════════════════════════════════════════════
   PhiloCompass — frontend logic
   ══════════════════════════════════════════════════════════════ */

(() => {
  "use strict";

  const API = {
    health: "/api/health",
    domains: "/api/domains",
    map: "/api/map",
    paths: "/api/paths",
    glossary: "/api/glossary",
    thinker: (id) => "/api/thinker/" + encodeURIComponent(id),
    start: "/api/session/start",
    answer: "/api/session/answer",
  };

  // ── state ──
  const state = {
    tab: "explore",
    nodes: {},
    edges: [],
    domains: [],
    activeDomain: null,
    search: "",
    detailNode: null,
    sessionId: null,
    dialogMode: "idle",
    domPick: null, // chosen domain chip for dialogue
    pathPick: null, // chosen learning path
    pathIdx: 0, // current step index in the path
    pathActive: null,
    activeMode: "dialogue", // "dialogue" | "debate"
    debatePair: null, // chosen (a,b) debate pair
    debateSide: null, // current speaker A/B/student tracking
    glossary: {}, // term -> definition
    transcriptLog: [], // {role,text}[] for export
    takeaway: "",
    scaffoldLevel: 0, // progressive hint depth (0..2)
    lastNodeId: null, // most recently explored node (constructivism hook)
    teachersLens: true, // show why-the-tutor-asked rationale (educators, portfolio)
    eraCutoff: null, // timeline scrubber value (eraOrder threshold); null = all
    mapView: { x: 0, y: 0, scale: 1 }, // pan/zoom transform
    paths: {}, // learning paths
  };

  // ── DOM refs (cached) ──
  const $ = (id) => document.getElementById(id);
  const el = {
    stars: $("stars"),
    tabs: Array.from(document.querySelectorAll(".tab")),
    panels: { explore: $("tab-explore"), dialogue: $("tab-dialogue") },
    themeToggle: $("themeToggle"),
    mapSearch: $("mapSearch"),
    domainChips: $("domainTicker"),
    domainTicker: $("domainTicker"),
    constellation: $("constellation"),
    detailPanel: $("detailPanel"),
    detailClose: $("detailClose"),
    detailKind: $("detailKind"),
    detailName: $("detailName"),
    detailEra: $("detailEra"),
    detailBlurb: $("detailBlurb"),
    detailInfluencedBy: $("detailInfluencedBy"),
    detailInfluences: $("detailInfluences"),
    detailRelated: $("detailRelated"),
    detailDialogue: $("detailDialogue"),
    domainPick: $("domainPick"),
    beginBtn: $("beginBtn"),
    newQuestionBtn: $("newQuestionBtn"),
    modeBadge: $("modeBadge"),
    tutorBubble: $("tutorBubble"),
    transcript: $("transcript"),
    composer: $("composer"),
    answerBox: $("answerBox"),
    sendBtn: $("sendBtn"),
    conclusion: $("conclusion"),
    endActions: $("endActions"),
    restartBtn: $("restartBtn"),
    nextDomainBtn: $("nextDomainBtn"),
    exportRow: $("exportRow"),
    exportCopyBtn: $("exportCopyBtn"),
    exportDownloadBtn: $("exportDownloadBtn"),
    exportMdBtn: $("exportMdBtn"),
    mapLoading: $("mapLoading"),
    brandHero: $("brandHero"),
    brand: document.querySelector(".brand"),
    pathPick: $("pathPick"),
    pathProgress: $("pathProgress"),
    pathStepList: $("pathStepList"),
    nextStepBtn: $("nextStepBtn"),
    takeawayWrap: $("takeawayWrap"),
    takeawayBox: $("takeawayBox"),
    eraRow: $("eraRow"),
    eraSlider: $("eraSlider"),
    eraLabel: $("eraLabel"),
    edgeTooltip: $("edgeTooltip"),
    hintBtn: $("hintBtn"),
    rewriteBtn: $("rewriteBtn"),
    teachBtn: $("teachBtn"),
    debatePairs: $("debatePairs"),
    debateBtn: $("debateBtn"),
    customDebateBtn: $("customDebateBtn"),
    debateTopicA: $("debateTopicA"),
    debateTopicB: $("debateTopicB"),
    debateQuestion: $("debateQuestion"),
    debateNodeList: $("debateNodeList"),
    customQBox: $("customQBox"),
    customQBtn: $("customQBtn"),
    detailPanelOpen: false,
  };

  // ────────────────────────────────────────────────────────────
  //  Starfield
  // ────────────────────────────────────────────────────────────
  function initStars() {
    const canvas = el.stars;
    const ctx = canvas.getContext("2d");
    let w, h, stars = [];
    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }
    function makeStars() {
      const n = Math.floor((w * h) / 24000);
      stars = Array.from({ length: n }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: 0.3 + Math.random() * 1.5,
        a: 0.3 + Math.random() * 0.7,
        s: 0.02 + Math.random() * 0.06,
        phase: Math.random() * Math.PI * 2,
      }));
    }
    function draw() {
      ctx.clearRect(0, 0, w, h);
      const t = Date.now() / 1000;

      // Nebula drift — slow-moving translucent gold/violet wisps behind stars
      ctx.save();
      ctx.globalCompositeOperation = "lighter";
      const n1x = w * 0.3 + 40 * Math.sin(t * 0.05);
      const n2x = w * 0.7 + 50 * Math.cos(t * 0.04);
      const rad = Math.max(w, h) * 0.5;
      const g1 = ctx.createRadialGradient(n1x, h * 0.25, 0, n1x, h * 0.25, rad);
      g1.addColorStop(0, "rgba(212,168,68,0.06)");
      g1.addColorStop(1, "rgba(212,168,68,0)");
      ctx.fillStyle = g1;
      ctx.fillRect(0, 0, w, h);
      const g2 = ctx.createRadialGradient(n2x, h * 0.7, 0, n2x, h * 0.7, rad * 0.8);
      g2.addColorStop(0, "rgba(95,61,196,0.06)");
      g2.addColorStop(1, "rgba(95,61,196,0)");
      ctx.fillStyle = g2;
      ctx.fillRect(0, 0, w, h);
      ctx.restore();

      for (const s of stars) {
        s.a = 0.25 + 0.55 * (0.5 + 0.5 * Math.sin(t * s.s + s.phase));
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,235,200,${s.a})`;
        ctx.fill();
      }
      requestAnimationFrame(draw);
    }
    resize();
    makeStars();
    draw();
    window.addEventListener("resize", () => { resize(); makeStars(); });
  }

  // ────────────────────────────────────────────────────────────
  //  Tabs
  // ────────────────────────────────────────────────────────────
  function setTab(name) {
    state.tab = name;
    el.tabs.forEach((t) => t.classList.toggle("is-active", t.dataset.tab === name));
    Object.entries(el.panels).forEach(([k, p]) => p.classList.toggle("is-hidden", k !== name));
  }

  // ────────────────────────────────────────────────────────────
  //  Constellation map
  // ────────────────────────────────────────────────────────────
  const KIND_ATTR = {
    thinker: "#7a56e0",
    school: "#35bf8a",
    concept: "#eab308", // brighter gold concept dots
  };
  let positions = {}; // id -> {x,y}
  // Gentle per-node orbital drift. Each node orbits a small ellipse around
  // its hand-placed home position. Amplitudes are kept small so the lineage
  // layout stays legible, but the whole web visibly breathes.
  let drift = { t: 0, running: true };

  function nodeDrift(id, rawX, rawY) {
    const n = state.nodes[id];
    if (!n) return { x: rawX, y: rawY };
    // nodes in tight ancient cluster drift less; concept/school hubs + a few
    // thinkers drift a touch more for dynamism without overlap.
    const amp = n.kind === "concept" ? 14 : (n.kind === "school" ? 12 : 9);
    const phase = (n.eraOrder + (n.name ? n.name.length % 5 : 0)) * 0.6;
    const sp = 0.55 + (n.id.length % 3) * 0.12;
    return {
      x: rawX + Math.sin(drift.t * sp + phase) * amp,
      y: rawY + Math.cos(drift.t * sp * 0.86 + phase * 1.3) * (amp * 0.7),
    };
  }

  // Hand-placed constellation layout. Coordinates chosen so the map tells
  // the lineage story: the Ancient school at bottom, epistemic/ethical
  // streams flowing upward through the moderns and out to 20th century.
  // Roughly a "tree of ideas" across the canvas (-500..500).
  const HAND_PLACED = {
    // ── Ancient cluster (bottom center-left) ──
    socrates: { x: -140, y: 350 },
    plato: { x: -40, y: 260 },
    aristotle: { x: 100, y: 260 },
    the_forms: { x: -200, y: 210 },
    eudaimonia: { x: 170, y: 190 },
    stoicism: { x: -260, y: 300 },
    epictetus: { x: -330, y: 380 },
    marcus_aurelius: { x: -190, y: 430 },
    // ── Early modern (flowing up-right) ──
    descartes: { x: -140, y: 80 },
    locke: { x: 30, y: 60 },
    hobbes: { x: -40, y: 160 },
    tabula_rasa: { x: 140, y: 0 },
    dualism: { x: -240, y: 90 },
    hume: { x: 230, y: -40 },
    bundle_theory: { x: 330, y: -120 },
    // ── High modern (upper middle) ──
    kant: { x: 60, y: -120 },
    categorical_imperative: { x: -40, y: -200 },
    // ── 19th/20th century (top) ──
    nietzsche: { x: 200, y: -220 },
    existentialism: { x: 260, y: -300 },
    ubermensch: { x: 320, y: -210 },
    sartre: { x: 180, y: -350 },
    utilitarianism: { x: 30, y: -300 },
    // ── Political (upper left band) ──
    social_contract: { x: -320, y: -40 },
    justice: { x: -200, y: -40 },
    rawls: { x: -280, y: -140 },
    veil_of_ignorance: { x: -390, y: -190 },
    // ── Big-concept hubs ringed near center-top ──
    epistemology: { x: 60, y: 10 },
    ethics: { x: -40, y: -60 },
    metaphysics: { x: 190, y: -80 },
    free_will: { x: 140, y: -170 },
    // ── New ancient / Hellenistic ──
    sophists: { x: -40, y: 450 },
    alcibiades: { x: 150, y: 360 },
    cyrenaics: { x: 30, y: 175 },
    epicurus: { x: -150, y: 420 },
    lucretius: { x: -300, y: 470 },
    plotinus: { x: -340, y: 120 },
    neoplatonism: { x: -400, y: 220 },
    sextus_empiricus: { x: 420, y: 250 },
    scepticism: { x: 460, y: 340 },
    // ── New early modern ──
    spinoza: { x: -290, y: -20 },
    monism: { x: -360, y: 40 },
    pascal: { x: -120, y: 10 },
    leibniz: { x: 70, y: 40 },
    vico: { x: 370, y: 40 },
    rousseau: { x: -260, y: 160 },
    berkeley: { x: 120, y: 130 },
    idealism: { x: -460, y: -60 },
    // ── New modern ──
    hegel: { x: 20, y: -180 },
    schopenhauer: { x: 260, y: -260 },
    kierkegaard: { x: 140, y: -420 },
    mills_liberty: { x: 110, y: -250 },
    marx: { x: -120, y: -300 },
    darwin: { x: 330, y: -140 },
    pragmatism: { x: 400, y: -20 },
    william_james: { x: 450, y: -120 },
    // ── New 20th century ──
    wittgenstein: { x: -200, y: -380 },
    popper: { x: -320, y: -300 },
    heidegger: { x: 90, y: -470 },
    arendt: { x: -380, y: -430 },
    foucault: { x: -260, y: -450 },
    nussbaum: { x: 250, y: -400 },
    kripke: { x: 360, y: -320 },
    machine_ethics: { x: -460, y: -260 },
    philosophy_of_mind: { x: 430, y: -200 },
    the_hard_problem: { x: 490, y: -260 },
    explanatory_gap: { x: 480, y: -170 },
    algorithmic_fairness: { x: -430, y: -340 },
  };

  function computeLayout(nodes) {
    positions = {};
    let unplaced = [];
    for (const id of Object.keys(nodes)) {
      if (HAND_PLACED[id]) {
        positions[id] = { ...HAND_PLACED[id] };
      } else {
        unplaced.push(id);
      }
    }
    // Any node not hand-placed gets scattered on concentric rings so it stays
    // visible and nearby to the graph's center.
    if (unplaced.length) {
      const rings = [330, 420, 500];
      const perRing = Math.max(1, Math.ceil(unplaced.length / rings.length));
      unplaced.forEach((id, i) => {
        const ring = rings[Math.min(Math.floor(i / perRing), rings.length - 1)];
        const a = (i / Math.max(1, unplaced.length)) * Math.PI * 2 + 0.6;
        positions[id] = { x: ring * 1.4 * Math.cos(a), y: ring * 1.1 * Math.sin(a) };
      });
    }
  }

  function renderMap() {
    const svg = el.constellation;
    const NS = "http://www.w3.org/2000/svg";
    svg.innerHTML = "";
    if (el.edgeTooltip) el.edgeTooltip.classList.remove("show");

    // Apply pan/zoom transform to the whole map
    const inner = document.createElementNS(NS, "g");
    inner.setAttribute("transform", `translate(${state.mapView.x} ${state.mapView.y}) scale(${state.mapView.scale})`);
    svg.appendChild(inner);

    const nodesL = Object.values(state.nodes);
    const visible = nodesL.filter((n) => {
      if (state.activeDomain && n.domain !== state.activeDomain) return false;
      const q = state.search.toLowerCase();
      if (q && !n.name.toLowerCase().includes(q) && !n.blurb.toLowerCase().includes(q)) return false;
      return true;
    });
    const visibleIds = new Set(visible.map((n) => n.id));

    const activeId = state.detailNode ? state.detailNode.id : null;

    // edges first
    const edgeG = document.createElementNS(NS, "g");
    for (const e of state.edges) {
      if (!visibleIds.has(e.from) || !visibleIds.has(e.to)) continue;
      if (state.activeDomain) {
        const a = state.nodes[e.from], b = state.nodes[e.to];
        if (a.domain !== state.activeDomain && b.domain !== state.activeDomain) continue;
      }
      // timeline scrubber: hide influence edges whose source era is beyond the cut-off
      const src = state.nodes[e.from];
      if (state.eraCutoff !== null && e.type === "influence" && src && src.eraOrder > state.eraCutoff) continue;
      const eFrom = nodeDrift(e.from, positions[e.from].x, positions[e.from].y);
      const eTo = nodeDrift(e.to, positions[e.to].x, positions[e.to].y);
      const line = document.createElementNS(NS, "line");
      line.setAttribute("x1", eFrom.x);
      line.setAttribute("y1", eFrom.y);
      line.setAttribute("x2", eTo.x);
      line.setAttribute("y2", eTo.y);
      line.setAttribute("class", "p-edge " + (e.type === "influence" ? "influence" : "related"));
      if (activeId && (e.from === activeId || e.to === activeId)) line.classList.add("highlight");
      line.dataset.from = e.from;
      line.dataset.to = e.to;
      line.dataset.rationale = e.rationale || "";
      edgeG.appendChild(line);
    }
    inner.appendChild(edgeG);

    // nodes
    for (const n of visible) {
      // timeline scrubber: dim/hide node if its era is beyond cut-off
      if (state.eraCutoff !== null && n.eraOrder > state.eraCutoff) continue;
      const p0 = positions[n.id];
      const p = nodeDrift(n.id, p0.x, p0.y);
      const g = document.createElementNS(NS, "g");
      g.setAttribute("class", "p-node");
      g.dataset.id = n.id;
      g.setAttribute("transform", `translate(${p.x}, ${p.y})`);

      const circle = document.createElementNS(NS, "circle");
      const size = n.kind === "concept" ? 6 : 8;
      circle.setAttribute("r", size);
      circle.setAttribute("fill", KIND_ATTR[n.kind] || KIND_ATTR.concept);
      circle.setAttribute("stroke", "rgba(255,235,200,0.6)");
      circle.setAttribute("stroke-width", "1");
      if (activeId && n.id === activeId) {
        circle.setAttribute("r", size + 3);
        circle.setAttribute("stroke", "#ecc05c");
        circle.setAttribute("stroke-width", "2");
      }
      g.appendChild(circle);

      const label = document.createElementNS(NS, "text");
      label.setAttribute("class", "p-node-label" + (n.name.length > 16 ? " small" : "") + (activeId === n.id ? " highlight" : ""));
      label.setAttribute("x", 0);
      label.setAttribute("y", size + 14);
      label.setAttribute("text-anchor", "middle");
      label.textContent = n.name;
      g.appendChild(label);

      inner.appendChild(g);
    }
  }

  // Event delegation for node clicks — stable even though the drift re-renders
  // (re-creates) every node group each frame. Attaching a listener to the SVG
  // once works regardless of children being swapped out.
  // To be extra-robust against the detach-between-mousedown/up race, we fall
  // back to resolving the node at click time from *current* drift positions.
  function initNodeClicks() {
    el.constellation.addEventListener("click", (e) => {
      const g = e.target.closest ? e.target.closest(".p-node") : null;
      const id = g && g.dataset.id ? g.dataset.id : pickNodeAtEvent(e);
      if (!id) return;
      // If the user just dragged (pan), don't open a detail panel
      if (state._justPanned && Date.now() - state._justPanned < 250) return;
      openDetail(id);
    });
  }

  // Fallback: find whichever node is visually under the click point, using the
  // current drift offsets. Survives even if the clicked <g> was swapped out.
  function pickNodeAtEvent(e) {
    const svg = el.constellation;
    if (!svg.createSVGPoint) return null;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX; pt.y = e.clientY;
    const m = svg.getScreenCTM();
    if (!m) return null;
    const spt = pt.matrixTransform(m.inverse());
    // un-apply pan/zoom
    const wx = (spt.x - state.mapView.x) / state.mapView.scale;
    const wy = (spt.y - state.mapView.y) / state.mapView.scale;
    let best = null, bd = Infinity;
    for (const id of Object.keys(state.nodes)) {
      if (state.eraCutoff !== null && (state.nodes[id].eraOrder || 0) > state.eraCutoff) continue;
      const p0 = positions[id]; if (!p0) continue;
      const p = nodeDrift(id, p0.x, p0.y);
      const d = Math.hypot(wx - p.x, wy - p.y);
      if (d < bd) { bd = d; best = id; }
    }
    return (bd < 26) ? best : null; // within a generous hit radius
  }

  // ────────────────────────────────────────────────────────────
  //  Detail panel
  // ────────────────────────────────────────────────────────────
  let curDetailNodeId = null; // id of open detail node (for seeding dialogue)
  async function openDetail(id) {
    state.detailNode = state.nodes[id] || null;
    const res = await fetch(API.thinker(id));
    const data = await res.json();
    if (data.error) return;
    state.detailNode = { id, ...data };
    curDetailNodeId = id;
    state.lastNodeId = id; // track for "connect it to you" construction

    el.detailKind.textContent = data.kind;
    el.detailName.textContent = data.name;
    el.detailEra.textContent = data.era || "";
    el.detailBlurb.textContent = data.blurb || "";
    el.detailInfluencedBy.innerHTML = chips(data.influenced_by || []);
    el.detailInfluences.innerHTML = chips(data.influences || []);
    el.detailRelated.innerHTML = chips(data.related || []);
    el.detailPanel.classList.add("open");
    el.detailPanelOpen = true;
    renderMap();
  }
  function chips(names) {
    return names.length ? names.map((n) => `<span class="chip">${n}</span>`).join("") : '<span class="chip" style="opacity:.5">—</span>';
  }
  function closeDetail() {
    el.detailPanel.classList.remove("open");
    el.detailPanelOpen = false;
    state.detailNode = null;
    renderMap();
  }

  // ────────────────────────────────────────────────────────────
  //  Dialogue
  // ────────────────────────────────────────────────────────────
  async function loadDomains() {
    try {
      const res = await fetch(API.domains);
      const data = await res.json();
      state.domains = Object.entries(data.domains || {});
    } catch {
      state.domains = [];
    }
    // Explore ticker: build the single-set of chips, then render a seamless
    // loop by inserting the set twice (ScholarSift's ticker pattern).
    renderDomainTicker(state.domains);
    // dialogue pick chips (with an "Any" option) — friendly labels
    el.domainPick.innerHTML =
      '<button class="chip ' + (state.domPick == null ? "is-active" : "") + '" data-d="any" style="flex:1 1 100%;">🌌 Any (random)</button>' +
      state.domains.map(([k, v]) => `<button class="chip ${state.domPick === k ? "is-active" : ""}" data-d="${k}" title="${v}">${v}</button>`).join("");
  }

  // Fills the auto-scrolling ticker track with the domain chips duplicated
  // for a seamless 50% translate loop. Hover pauses it.
  function renderDomainTicker(domains) {
    const track = el.domainTicker;
    if (!track) return;
    const build = (items) => items.map(([k, v]) =>
      `<button class="chip ${state.activeDomain === k ? "is-active" : ""}" data-d="${k}" title="${v}">${v}</button>`
    ).join("");
    track.innerHTML = build(domains) + build(domains);
  }

  async function metaHealth() {
    try {
      const res = await fetch(API.health);
      const data = await res.json();
      if (data.llm) {
        el.modeBadge.classList.add("has-llm");
        el.modeBadge.textContent = "✦ Adaptive LLM tutor active";
      } else {
        el.modeBadge.classList.remove("has-llm");
        el.modeBadge.textContent = "Offline tutor · no API key required";
      }
    } catch {}
  }

  async function beginDialogue(preseed, opts) {
    el.tutorBubble.textContent = "Thinking…";
    opts = opts || {};
    let nodeId = null;
    if (preseed && state.nodes[preseed]) nodeId = preseed;
    const payload = {};
    if (opts.custom) { payload.custom_question = opts.custom; }
    if (nodeId) payload.node_id = nodeId;
    else payload.domain = state.domPick || null;
    // constructivism hook: connect this question to the node they just explored
    if (state.lastNodeId && state.lastNodeId !== nodeId) payload.last_node_id = state.lastNodeId;

    state.activeMode = "dialogue";
    try {
      const res = await fetch(API.start, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.error) { el.tutorBubble.textContent = data.error; return; }
      state.sessionId = data.session_id;
      state.dialogMode = "active";
      state.scaffoldLevel = 0; // reset progressive hints for the fresh question
      el.transcript.innerHTML = "";
      el.conclusion.classList.add("is-hidden");
      el.takeawayWrap.classList.add("is-hidden");
      el.endActions.classList.add("is-hidden");
      el.composer.classList.remove("is-hidden");
      el.newQuestionBtn.classList.remove("is-hidden");
      // show the "connect it to you" scaffold before the question
      if (data.connect) addTranscript("tutor", data.connect);
      el.tutorBubble.innerHTML = `<strong>${data.question}</strong>`;
      if (nodeId) {
        const label = state.nodes[nodeId].name;
        addTranscript("tutor", `Let's think about ${label} together:`);
      } else if (opts.custom) {
        addTranscript("tutor", "A question worth taking seriously. Let's dig in:");
      } else {
        addTranscript("tutor", "The question I want to explore with you:");
      }
      addTranscript("tutor", data.question);
      const hint = data.hint || "Consider what assumptions your answer rests on.";
      addHint(hint);
      state.transcriptLog = [{ role: "tutor", text: data.question }];
      state.takeaway = "";
      el.answerBox.placeholder = "Respond to the question… (your answer, your doubts, your guesses)";
      showExportBtn();
      el.answerBox.focus();
    } catch (e) {
      el.tutorBubble.textContent = "Couldn't reach the tutor. Is the server running?";
    }
  }

  // ── ON-DEMAND SCAFFOLD (I'm stuck) ─────────────────────────
  async function requestHint() {
    if (!state.sessionId) return;
    const level = Math.min((state.scaffoldLevel || 0) + 1, 2);
    state.scaffoldLevel = level;
    const btnTxt = el.hintBtn.textContent;
    el.hintBtn.disabled = true;
    try {
      const res = await fetch(API.answer, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: state.sessionId, answer: "", want_hint: true, hint_level: level }),
      });
      const data = await res.json();
      if (data.error) { addTranscript("tutor", data.error); return; }
      addTranscript("tutor", data.scaffold);
      state.transcriptLog = (state.transcriptLog || []).concat({ role: "tutor", text: data.scaffold });
      // cycle through levels; then the button degrades
      el.hintBtn.textContent = level >= 2 ? "🪜 hint (use thoughtfully)" : "🪜 I'm stuck";
      el.hintBtn.disabled = false;
    } catch {
      addTranscript("tutor", "Couldn't reach the tutor.");
      el.hintBtn.disabled = false;
      el.hintBtn.textContent = btnTxt;
    }
  }

  // ── DEBATE MODE ─────────────────────────────────────────────
  function renderDebatePairs() {
    const PRESETS = [
      // political / economic
      ["marx", "mills_liberty"],
      ["marx", "hegel"],
      ["foucault", "arendt"],
      ["foucault", "marx"],
      // modern / existential
      ["hegel", "kierkegaard"],
      ["schopenhauer", "nietzsche"],
      ["kierkegaard", "nietzsche"],
      // early modern metaphysics
      ["spinoza", "leibniz"],
      ["spinoza", "hobbes"],
      ["berkeley", "hume"],
      ["rousseau", "hobbes"],
      // originals
      ["kant", "utilitarianism"],
      ["hume", "kant"],
      ["plato", "aristotle"],
      ["sartre", "nietzsche"],
    ];
    el.debatePairs.innerHTML = PRESETS.map(([a, b]) => {
      const na = (state.nodes[a] || {}).name || a;
      const nb = (state.nodes[b] || {}).name || b;
      const active = state.debatePair && state.debatePair[0] === a && state.debatePair[1] === b;
      return `<button class="path-option ${active ? "is-active" : ""}" data-a="${a}" data-b="${b}">
        <span class="path-title">${na} ⚔️ ${nb}</span>
        <span class="path-step-count">debate</span></button>`;
    }).join("");
  }

  async function beginDebate(custom) {
    custom = custom || null;
    el.rewriteBtn.classList.remove("is-hidden");
    el.teachBtn.classList.remove("is-hidden");
    el.hintBtn.classList.remove("is-hidden");
    el.tutorBubble.textContent = "Calling both thinkers to the floor…";
    let payload;
    if (custom) {
      payload = {
        mode: "debate",
        node_id: custom.a,
        pair_with: custom.b,
        custom_question: custom.q,
      };
    } else {
      payload = {
        mode: "debate",
        node_id: state.debatePair ? state.debatePair[0] : null,
        pair_with: state.debatePair ? state.debatePair[1] : null,
      };
    }
    state.activeMode = "debate";
    try {
      const res = await fetch(API.start, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (data.error) { el.tutorBubble.textContent = data.error; return; }
      state.sessionId = data.session_id;
      state.dialogMode = "active";
      state.debateSide = data.opening ? data.opening.speaker : "A";
      resetTranscript();
      el.composer.classList.remove("is-hidden");
      el.newQuestionBtn.classList.remove("is-hidden");
      el.tutorBubble.innerHTML = `<strong>⚖️ ${data.side_a} vs ${data.side_b}</strong>`;
      addTranscript("tutor", data.question);
      addTranscript("debate", data.opening.text, data.opening.name);
      state.transcriptLog = [
        { role: "tutor", text: data.question },
        { role: data.opening.speaker, text: data.opening.text },
      ];
      state.takeaway = "";
      el.answerBox.placeholder = "Weigh in — whose side (if any) do you favor, and why?";
      showExportBtn();
      el.answerBox.focus();
    } catch (e) {
      el.tutorBubble.textContent = "Couldn't reach the tutor. Is the server running?";
    }
  }
  function resetTranscript() {
    el.transcript.innerHTML = "";
    el.conclusion.classList.add("is-hidden");
    el.takeawayWrap.classList.add("is-hidden");
    el.endActions.classList.add("is-hidden");
  }

  async function sendAnswer() {
    const answer = el.answerBox.value.trim();
    if (!answer || !state.sessionId) return;
    el.answerBox.value = "";
    addTranscript("student", answer);

    const btnTxt = el.sendBtn.textContent;
    el.sendBtn.disabled = true;
    el.sendBtn.textContent = "…";
    try {
      const res = await fetch(API.answer, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: state.sessionId,
          answer,
          mode: state.activeMode === "debate" ? "debate" : null,
        }),
      });
      const data = await res.json();
      if (data.error) { addTranscript("tutor", data.error); return; }

      if (data.mode === "debate") {
        // debate mode: reply shape is { turn: {speaker,name,text,student}, conclusion }
        state.transcriptLog = (state.transcriptLog || []).concat({ role: "student", text: answer });
        const turn = data.turn || {};
        addTranscript(turn.student ? "debate" : "debate", turn.text || "", turn.name || "");
        state.transcriptLog = (state.transcriptLog || []).concat({ role: turn.speaker || "tutor", text: turn.text });
        if (data.conclusion) {
          el.composer.classList.add("is-hidden");
          el.conclusion.classList.remove("is-hidden");
          el.conclusion.textContent = data.conclusion;
          el.takeawayWrap.classList.remove("is-hidden");
          el.endActions.classList.remove("is-hidden");
          state.dialogMode = "done";
        }
      } else if (data.conclusion) {
        addTranscript("tutor", data.follow_up);
        state.transcriptLog = (state.transcriptLog || []).concat({ role: "tutor", text: data.follow_up });
        // Teacher's lens rationale + threadback + momentum shown near the close
        if (data.pedagogy && data.pedagogy.rationale) {
          addTranscript("lens", "👁 Why I asked that: " + data.pedagogy.rationale);
        }
        if (data.threadback) addTranscript("tutor", data.threadback);
        el.composer.classList.add("is-hidden");
        el.conclusion.classList.remove("is-hidden");
        el.conclusion.textContent = data.conclusion;
        el.takeawayWrap.classList.remove("is-hidden");
        el.endActions.classList.remove("is-hidden");
        if (data.momentum) renderMomentum(data.momentum);
        maybeShowNextStep();
        state.dialogMode = "done";
      } else {
        addTranscript("tutor", data.follow_up);
        state.transcriptLog = (state.transcriptLog || []).concat({ role: "tutor", text: data.follow_up });
        // per-turn: show rationale + threadback (Teacher's lens + threading)
        if (data.threadback) addTranscript("tutor", data.threadback);
        if (data.pedagogy && data.pedagogy.rationale && state.teachersLens) {
          addTranscript("lens", "👁 Why I asked that: " + data.pedagogy.rationale);
        }
      }
      if (data.momentum) renderMomentum(data.momentum);
      persistToLocal();
    } catch (e) {
      addTranscript("tutor", "Something went wrong — check the server.");
    } finally {
      el.sendBtn.disabled = false;
      el.sendBtn.textContent = btnTxt;
      el.answerBox.focus();
    }
  }

  function addTranscript(role, text, label) {
    const turn = document.createElement("div");
    turn.className = "turn " + (role === "debate" ? "tutor" : role);
    const b = document.createElement("div");
    b.className = "turn-bubble";
    // debate turns get a colored name tag; glossify tutor text
    if (label) {
      const tag = document.createElement("div");
      tag.className = "turn-debate-name";
      tag.textContent = label;
      turn.appendChild(tag);
    }
    b.innerHTML = (role === "tutor") ? glossify(text) : text.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    turn.appendChild(b);
    el.transcript.appendChild(turn);
    el.transcript.scrollTop = el.transcript.scrollHeight;
  }
  function addHint(hint) {
    if (!hint) return;
    addTranscript("tutor", "💡 Hint: " + hint);
  }

  // Reasoning-momentum indicator — a subtle, growth-focused tally.
  function renderMomentum(m) {
    if (!m) return;
    let el_m = document.getElementById("momentum");
    if (!el_m) {
      el_m = document.createElement("div");
      el_m.id = "momentum";
      el_m.className = "momentum";
      // insert before the transcript
      if (el.transcript && el.transcript.parentNode) {
        el.transcript.parentNode.insertBefore(el_m, el.transcript);
      } else {
        document.getElementById("tab-dialogue").appendChild(el_m);
      }
    }
    el_m.innerHTML =
      `<strong>Reasoning momentum</strong> · ${m.turns} turn${m.turns === 1 ? "" : "s"} · ` +
      `${m.arguments || 0} argument${(m.arguments || 0) === 1 ? "" : "s"} · ` +
      `${m.tensions_seen || 0} tension${(m.tensions_seen || 0) === 1 ? "" : "s"} met · ` +
      `${m.refinements || 0} refinement${(m.refinements || 0) === 1 ? "" : "s"}`;
  }

  // ────────────────────────────────────────────────────────────
  //  Export / persistence
  // ────────────────────────────────────────────────────────────
  function showExportBtn() {
    el.exportRow.classList.remove("is-hidden");
  }
  function hideExportBtn() {
    el.exportRow.classList.add("is-hidden");
  }
  function exportText(md) {
    const log = state.transcriptLog || [];
    let out = "PhiloCompass — Socratic Dialogue\n" + "=".repeat(34) + "\n\n";
    for (const t of log) {
      const who = t.role === "student" ? "You" : "Tutor";
      out += (md ? `**${who}:** ` : `${who}:\n`) + t.text + "\n\n";
    }
    if (state.takeaway && state.takeaway.trim()) {
      out += (md ? "**Your takeaway:**\n" : "Your takeaway:\n") + state.takeaway.trim() + "\n\n";
    }
    return out.trimEnd() + "\n";
  }
  function download(filename, content, mime) {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 4000);
  }
  const LS_KEY = "philocompass.activeDialogue";
  function persistToLocal() {
    if (!state.sessionId) return;
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({
        sessionId: state.sessionId,
        log: state.transcriptLog || [],
        at: Date.now(),
      }));
    } catch {}
  }
  function restoreFromLocal() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return false;
      const saved = JSON.parse(raw);
      if (!saved || !saved.sessionId) return false;
      // Restore enough UI to be useful (log + a "continue" note). The live
      // session on the server may have expired, but showing prior thinking
      // is still valuable for the student.
      state.sessionId = saved.sessionId;
      state.transcriptLog = saved.log || [];
      if (state.transcriptLog.length >= 1) {
        el.transcript.innerHTML = "";
        for (const t of state.transcriptLog) addTranscript(t.role, t.text);
        el.composer.classList.remove("is-hidden");
        el.newQuestionBtn.classList.remove("is-hidden");
        showExportBtn();
        return true;
      }
    } catch {}
    return false;
  }

  // ────────────────────────────────────────────────────────────
  //  Learning paths
  // ────────────────────────────────────────────────────────────
  function renderPaths() {
    const entries = Object.entries(state.paths || {});
    el.pathPick.innerHTML = entries.map(([k, p]) =>
      `<button class="path-option ${state.pathPick === k ? "is-active" : ""}" data-p="${k}">` +
      `<span class="path-title">${p.title}</span>` +
      `<span class="path-step-count">${p.steps.length} steps</span>` +
      `</button>`).join("");
    if (!entries.length) el.pathPick.innerHTML = '<div class="side-hint is-hidden" style="opacity:.5">no paths available</div>';
  }
  function renderPathSteps() {
    const path = state.pathActive;
    if (!path) { el.pathProgress.classList.add("is-hidden"); return; }
    el.pathStepList.innerHTML = path.steps.map((s, i) => {
      const cls = i < state.pathIdx ? "done" : (i === state.pathIdx ? "active" : "");
      return `<div class="path-step ${cls}"><span class="step-num">${i + 1}</span>${s[1]}</div>`;
    }).join("");
  }
  function maybeShowNextStep() {
    if (!state.pathActive) return;
    if (state.pathIdx + 1 < state.pathActive.steps.length) {
      el.nextStepBtn.classList.remove("is-hidden");
      el.nextStepBtn.textContent = "Next in path →";
      el.restartBtn.classList.add("is-hidden");
    } else {
      el.nextStepBtn.textContent = "✓ Path complete";
      el.nextStepBtn.disabled = true;
    }
  }
  function nextPathStep() {
    if (!state.pathActive) return;
    state.pathIdx += 1;
    if (state.pathIdx >= state.pathActive.steps.length) { state.pathIdx = state.pathActive.steps.length - 1; }
    renderPathSteps();
    const nodeId = state.pathActive.steps[state.pathIdx][0];
    beginDialogue(nodeId);
  }

  // ────────────────────────────────────────────────────────────
  //  Glossary tooltip highlight inside bubble text
  // ────────────────────────────────────────────────────────────
  function glossify(text) {
    if (!state.glossary) return text;
    const terms = Object.keys(state.glossary);
    let out = text;
    for (const term of terms) {
      const re = new RegExp(`\\b(${term})\\b`, "gi");
      if (re.test(out)) {
        out = out.replace(re, `<span class="gloss" data-term="${term}">$1</span>`);
      }
    }
    return out;
  }
  function initGlossBubbles() {
    el.transcript.addEventListener("mouseover", (e) => {
      const g = e.target.closest(".gloss");
      if (!g || !state.glossary[g.dataset.term]) return;
      el.edgeTooltip.innerHTML = `<strong>${g.dataset.term}</strong><br>${state.glossary[g.dataset.term]}`;
      positionTooltip(g, el.edgeTooltip);
      el.edgeTooltip.classList.add("show");
    });
    el.transcript.addEventListener("mouseout", (e) => {
      if (e.target.closest(".gloss")) el.edgeTooltip.classList.remove("show");
    });
  }

  // ────────────────────────────────────────────────────────────
  //  Edge rationale tooltip (map)
  // ────────────────────────────────────────────────────────────
  function positionTooltip(anchor, tip) {
    const r = anchor.getBoundingClientRect();
    tip.style.top = (r.top + r.height / 2 - 20) + "px";
    tip.style.left = (r.right + 12) + "px";
  }
  function initEdgeTooltips() {
    el.constellation.parentElement.addEventListener("mouseover", (e) => {
      const line = e.target.closest("line.p-edge");
      if (!line) {
        el.edgeTooltip.classList.remove("show");
        return;
      }
      const r = (line.dataset.rationale || "").trim();
      if (!r) { el.edgeTooltip.classList.remove("show"); return; }
      const from = state.nodes[line.dataset.from], to = state.nodes[line.dataset.to];
      el.edgeTooltip.innerHTML = `<strong>${from ? from.name : "?"} → ${to ? to.name : "?"}</strong><br>${r}`;
      positionTooltip(line, el.edgeTooltip);
      el.edgeTooltip.classList.add("show");
    });
    el.constellation.parentElement.addEventListener("mouseout", (e) => {
      if (e.target.closest && e.target.closest("line.p-edge")) el.edgeTooltip.classList.remove("show");
    });
  }

  // ────────────────────────────────────────────────────────────
  //  Pan & zoom on the constellation
  // ────────────────────────────────────────────────────────────
  function initPanZoom() {
    const svg = el.constellation;
    let drag = false, last = { x: 0, y: 0 };
    svg.addEventListener("mousedown", (e) => {
      if (e.target.closest(".p-node")) return; // let node clicks through
      drag = true; svg.classList.add("dragging");
      last = { x: e.clientX, y: e.clientY };
    });
    window.addEventListener("mousemove", (e) => {
      if (!drag) return;
      state.mapView.x += (e.clientX - last.x);
      state.mapView.y += (e.clientY - last.y);
      last = { x: e.clientX, y: e.clientY };
      state._justPanned = Date.now(); // suppress a node-open right after a drag
      if (Math.abs(e.movementX) + Math.abs(e.movementY) > 3) state._moved = true;
      renderMap();
    });
    window.addEventListener("mouseup", () => {
      if (drag) { drag = false; svg.classList.remove("dragging"); }
    });
    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.88 : 1.14;
      const oldScale = state.mapView.scale;
      const newScale = Math.max(0.35, Math.min(6, oldScale * delta));

      // Zoom centered on the mouse position: keep the world point under the
      // cursor fixed on screen as we scale.
      const rect = svg.getBoundingClientRect();
      const px = e.clientX - rect.left;
      const py = e.clientY - rect.top;
      // screen→world using the CURRENT view transform (translate then scale).
      // screen = world*scale + pan  =>  world = (screen - pan)/scale.
      const wx = (px - state.mapView.x) / oldScale;
      const wy = (py - state.mapView.y) / oldScale     ;

      state.mapView.scale = newScale;
      // Re-anchor so the same world point stays under the cursor after scaling:
      // screen = world*newScale + pan  =>  pan = screen - world*newScale.
      state.mapView.x = px - wx * newScale;
      state.mapView.y = py - wy * newScale;
      renderMap();
    }, { passive: false });
  }

  // ────────────────────────────────────────────────────────────
  //  Empty search state + URL hash
  // ────────────────────────────────────────────────────────────
  function renderEmptyState() {
    // Find (or create) a small "no results" hint under the map on empty search.
    let empty = document.getElementById("mapEmpty");
    if (!state.search.trim()) {
      if (empty) empty.remove();
      return;
    }
    const q = state.search.trim().toLowerCase();
    const none = !Object.values(state.nodes).some((n) =>
      n.name.toLowerCase().includes(q) || (n.blurb || "").toLowerCase().includes(q));
    if (!none) { if (empty) empty.remove(); return; }
    if (!empty) {
      empty = document.createElement("div");
      empty.id = "mapEmpty";
      empty.className = "map-hint";
      empty.style.position = "absolute";
      empty.style.bottom = "3.2rem";
      empty.innerHTML = 'no thinkers matched "<b id="mapEmptyQ"></b>" — ' +
        '<a href="#" id="mapEmptyClear">clear search</a>';
      el.mapLoading.closest(".map-wrap").appendChild(empty);
      empty.querySelector("#mapEmptyClear").addEventListener("click", (ev) => {
        ev.preventDefault(); el.mapSearch.value = ""; state.search = "";
        renderEmptyState(); renderMap();
      });
    }
    empty.querySelector("#mapEmptyQ").textContent = state.search.trim();
  }
  function syncHash() {
    const tab = state.tab === "dialogue" ? "dialogue" : "explore";
    history.replaceState(null, "", "#" + tab);
  }
  function applyHash() {
    const h = (location.hash || "#explore").replace("#", "");
    setTab(h === "dialogue" ? "dialogue" : "explore");
  }

  // ────────────────────────────────────────────────────────────
  //  Service worker (PWA offline)
  // ────────────────────────────────────────────────────────────
  function setupSW() {
    if (!("serviceWorker" in navigator)) return;
    navigator.serviceWorker.register("/sw.js").catch((e) => console.warn("SW failed", e));
  }

  // ────────────────────────────────────────────────────────────
  //  Boot
  // ────────────────────────────────────────────────────────────
  async function boot() {
    initStars();
    setTab("explore");

    // Clicking the PhiloCompass logo returns to the home/explore view.
    if (el.brand) {
      el.brand.addEventListener("click", () => {
        setTab("explore");
        syncHash();
        location.hash = "";
        // reset search + detail so it feels like a clean home
        state.search = "";
        if (el.mapSearch) el.mapSearch.value = "";
        if (typeof closeDetail === "function") closeDetail();
        if (typeof renderMap === "function") renderMap();
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }

    el.tabs.forEach((t) => t.addEventListener("click", () => {
      setTab(t.dataset.tab);
      syncHash();
      if (t.dataset.tab === "dialogue" && !state.sessionId) el.answerBox.blur();
    }));

    el.themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("light");
      el.themeToggle.setAttribute("aria-pressed", String(document.body.classList.contains("light")));
    });

    el.hintBtn.addEventListener("click", requestHint);
    el.teachBtn.addEventListener("click", async () => {
      if (!state.sessionId) { el.tutorBubble.textContent = "Start a dialogue first."; return; }
      el.teachBtn.disabled = true;
      el.teachBtn.textContent = "Teaching…";
      try {
        // Provide a full explanatory foundation for the current question.
        const res = await fetch(API.answer, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: state.sessionId, teach_me: true }),
        });
        const data = await res.json();
        if (data.error) { addTranscript("tutor", data.error); return; }
        if (data.taught) {
          addTranscript("tutor", "📖 " + data.lesson);
          state.transcriptLog = (state.transcriptLog || []).concat({ role: "tutor", text: "📖 " + data.lesson });
        }
      } catch {
        addTranscript("tutor", "Couldn't fetch the lesson just now — try again.");
      } finally {
        el.teachBtn.disabled = false;
        el.teachBtn.textContent = "📖 Teach me";
      }
    });
    el.rewriteBtn.addEventListener("click", async () => {
      if (!state.sessionId) { el.tutorBubble.textContent = "Start a dialogue first."; return; }
      el.rewriteBtn.disabled = true;
      el.rewriteBtn.textContent = "Rewording…";
      try {
        // Reword the CURRENT question (in the live session) in plainer language.
        const res = await fetch(API.answer, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: state.sessionId, reword: true }),
        });
        const data = await res.json();
        if (data.error) { addTranscript("tutor", data.error); return; }
        addTranscript("tutor", data.reworded ? data.question : "Here's the question in plainer words:\n" + data.question);
      } catch {
        addTranscript("tutor", "Couldn't reword the question just now — try again.");
      } finally {
        el.rewriteBtn.disabled = false;
        el.rewriteBtn.textContent = "🔁 Reword the question";
      }
    });

    // explore events
    el.mapSearch.addEventListener("input", (e) => { state.search = e.target.value; renderEmptyState(); renderMap(); });
    el.domainChips.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      const alreadyActive = state.activeDomain && state.activeDomain === (chip.dataset.d === "all" ? null : chip.dataset.d);
      // clicking the SAME active chip (or "All") un-selects it
      state.activeDomain = (alreadyActive || chip.dataset.d === "all") ? null : chip.dataset.d;
      loadDomains(); // re-render chip active states
      renderMap();
    });
    // clicking anywhere else on the map unwraps the active topic filter
    document.addEventListener("click", (e) => {
      if (!state.activeDomain) return;
      // ignore clicks inside the ticker, its chips, or the search bar
      if (e.target.closest(".chips-scroller") || e.target.closest(".chip") || e.target.closest(".search-input")) return;
      state.activeDomain = null;
      loadDomains();
      renderMap();
    });
    // pause the ticker while the user interacts with the chips
    el.domainTicker.addEventListener("mouseenter", () => el.domainTicker.classList.add("paused"));
    el.domainTicker.addEventListener("mouseleave", () => el.domainTicker.classList.remove("paused"));
    el.detailClose.addEventListener("click", closeDetail);
    el.detailPanel.addEventListener("click", (e) => {
      if (e.target === el.detailPanel) closeDetail();
    });
    el.detailDialogue.addEventListener("click", () => {
      if (curDetailNodeId) {
        closeDetail();
        setTab("dialogue");
        showExportBtn(); // ensure export button exists for an active dialogue
        beginDialogue(curDetailNodeId);
      }
    });

    // dialogue events
    el.domainPick.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      state.domPick = chip.dataset.d === "any" ? null : chip.dataset.d;
      loadDomains();
    });
    el.beginBtn.addEventListener("click", beginDialogue);
    el.newQuestionBtn.addEventListener("click", beginDialogue);
    el.sendBtn.addEventListener("click", sendAnswer);
    el.answerBox.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendAnswer(); }
    });
    el.restartBtn.addEventListener("click", beginDialogue);
    el.nextDomainBtn.addEventListener("click", () => { setTab("explore"); });
    el.exportCopyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(exportText(false));
        el.exportCopyBtn.textContent = "✓ Copied";
        setTimeout(() => (el.exportCopyBtn.textContent = "⧉ Copy transcript + takeaway"), 1600);
      } catch {
        el.exportCopyBtn.textContent = "Copy blocked by browser";
        setTimeout(() => (el.exportCopyBtn.textContent = "⧉ Copy transcript + takeaway"), 2000);
      }
    });
    el.exportDownloadBtn.addEventListener("click", () => {
      download("philocompass-dialogue.txt", exportText(false), "text/plain");
    });
    el.exportMdBtn.addEventListener("click", () => {
      download("philocompass-dialogue.md", exportText(true), "text/markdown");
    });
    el.takeawayBox.addEventListener("input", (e) => { state.takeaway = e.target.value; });
    el.nextStepBtn.addEventListener("click", nextPathStep);
    el.debatePairs.addEventListener("click", (e) => {
      const opt = e.target.closest(".path-option");
      if (!opt) return;
      state.debatePair = [opt.dataset.a, opt.dataset.b];
      renderDebatePairs();
    });
    el.debateBtn.addEventListener("click", beginDebate);

    // Custom debate: resolve the two thinkers (by name/id) + the question, then start.
    el.customDebateBtn.addEventListener("click", () => {
      const aRaw = (el.debateTopicA.value || "").trim();
      const bRaw = (el.debateTopicB.value || "").trim();
      const q = (el.debateQuestion.value || "").trim();
      if (!aRaw || !bRaw) { el.tutorBubble.textContent = "Name both thinkers to debate."; return; }
      if (!q) { el.tutorBubble.textContent = "Give the two sides a question to argue about."; return; }
      // resolve display names to node ids (case-insensitive match on name)
      const lookup = (raw) => {
        const L = raw.toLowerCase();
        for (const [id, n] of Object.entries(state.nodes)) {
          if (id === L || (n.name || "").toLowerCase() === L) return id;
        }
        return raw; // if it isn't a known node, treat literally
      };
      const a = lookup(aRaw), b = lookup(bRaw);
      if (a === b) { el.tutorBubble.textContent = "Pick two different views to debate."; return; }
      beginDebate({ a, b, q });
    });

    el.customQBtn.addEventListener("click", () => {
      const q = el.customQBox.value.trim();
      if (!q) { el.tutorBubble.textContent = "Type a question first."; return; }
      beginDialogue(null, { custom: q });
    });
    el.pathPick.addEventListener("click", (e) => {
      const opt = e.target.closest(".path-option");
      if (!opt) return;
      state.pathPick = opt.dataset.p;
      state.pathIdx = 0;
      state.pathActive = state.paths[state.pathPick] || null;
      renderPaths();
      el.pathProgress.classList.remove("is-hidden");
      renderPathSteps();
      // clear any in-progress debate dialog state and pick a fresh question
      state.dialogMode = "idle";
    });
    el.beginBtn.addEventListener("click", () => {
      // If a path is selected, start its first node; otherwise normal dialogue.
      if (state.pathActive && state.pathActive.steps && state.pathActive.steps.length) {
        beginDialogue(state.pathActive.steps[0][0]);
      } else {
        beginDialogue();
      }
    });
    el.newQuestionBtn.addEventListener("click", () => {
      if (state.pathActive && state.pathActive.steps && state.pathActive.steps.length) {
        beginDialogue(state.pathActive.steps[state.pathIdx][0]);
      } else {
        beginDialogue();
      }
    });
    el.eraSlider.addEventListener("input", onEra);
    initPanZoom();
    initNodeClicks();
    initEdgeTooltips();
    initGlossBubbles();
    // Nebula drift painter (behind the map, on the starfield canvas)

    // load data
    await loadDomains();
    try {
      const res = await fetch(API.map);
      const data = await res.json();
      state.nodes = data.nodes || {};
      state.edges = data.edges || [];
      computeLayout(state.nodes);
      renderMap();
      if (el.mapLoading) el.mapLoading.classList.add("is-hidden");
      if (el.brandHero) el.brandHero.classList.add("show");
      if (el.eraRow) el.eraRow.classList.remove("is-hidden");
      // populate the custom-debate autocomplete datalist with known thinkers
      if (el.debateNodeList) {
        el.debateNodeList.innerHTML =
          Object.values(state.nodes).map((n) => `<option value="${n.name}"></option>`).join("");
      }
    } catch (e) {
      console.error("Map load failed", e);
      if (el.mapLoading) {
        el.mapLoading.textContent = "map unavailable — is the server running?";
        el.mapLoading.classList.remove("is-hidden");
      }
    }
    // Load learning paths + glossary
    try {
      const pres = await fetch(API.paths);
      state.paths = (await pres.json()).paths || {};
      renderPaths();
    } catch {}
    try {
      const gres = await fetch(API.glossary);
      state.glossary = (await gres.json()).glossary || {};
    } catch {}
    renderDebatePairs();
    metaHealth();
    setupSW();
    applyHash();

    // restore a prior in-progress dialogue on load
    restoreFromLocal();
  }

  // ────────────────────────────────────────────────────────────
  //  Timeline scrubber
  // ────────────────────────────────────────────────────────────
  const ERA_LABELS = ["Ancient", "Hellenistic", "Roman", "Early modern", "Modern", "20th century"];

  function onEra(e) {
    const v = parseInt(e.target.value, 10);
    if (v >= 100) {
      state.eraCutoff = null;
      el.eraLabel.textContent = "All eras";
    } else {
      state.eraCutoff = Math.floor(v / 20);
      el.eraLabel.textContent = ERA_LABELS[state.eraCutoff] || "Ancient";
    }
    renderMap();
  }

  // ────────────────────────────────────────────────────────────
  //  Living constellation — animate the node drift each frame
  // ────────────────────────────────────────────────────────────
  function animateDrift() {
    if (!drift.running) return;
    drift.t += 0.013; // slightly faster breathing
    if (document.visibilityState === "visible" && state.tab === "explore") {
      renderMap();
    }
    requestAnimationFrame(animateDrift);
  }
  document.addEventListener("visibilitychange", () => {
    // pause pumping when the page is hidden
    if (document.visibilityState !== "visible" && drift.tick) cancelAnimationFrame(drift.tick);
    else if (document.visibilityState === "visible") drift.tick = requestAnimationFrame(animateDrift);
  });

  document.addEventListener("DOMContentLoaded", () => {
    initStars();
    drift.tick = requestAnimationFrame(animateDrift);
    boot();
  });
})();