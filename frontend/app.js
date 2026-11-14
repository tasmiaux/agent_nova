/* =========================================================
   Nova — front end (Supra AI demo).

   Supra AI makes an AI WhatsApp customer-support bot for small businesses.
   Nova onboards a new customer, Kaveri Handlooms (a saree brand in Mysuru),
   in the customer's language (Hindi or Kannada, chosen in Demo controls):

   Ask Nova "Onboard Kaveri Handlooms" -> plan + real account check
   -> Call the owner (AI disclosure, name + WhatsApp number with read-backs)
   -> written summary to the customer -> Engineer connects the number and
   uploads the FAQ, marks done -> Nova tests the Supra AI platform (number
   connected, FAQ indexed, test chat in the customer's language) ->
   Blocked (engineer is messaged) / Verified -> Approve go-live
   (Avinash reads the English report).

   Modes (header switch):
     Live     real mic, real Gnani + Sarvam calls
     Offline  a scripted demo customer; saved audio only; no paid calls
   Demo state is saved in the browser (localStorage), so a reload keeps it.
   "Reset demo" in Demo controls clears it and resets the mock platform.
   ========================================================= */

// ---------------- icons ----------------
const ICONS = {
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  activity: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  phone: '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>',
  building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
  user: '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  plug: '<path d="M12 22v-5M9 8V2M15 8V2M18 8v5a6 6 0 0 1-12 0V8z"/>',
  calendar: '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  mic: '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3"/>',
  send: '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
  wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  headset: '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  alert: '<circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>',
  rocket: '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
  speaker: '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07M19.07 4.93a10 10 0 0 1 0 14.14"/>',
  chevron: '<path d="m9 18 6-6-6-6"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-2.64-6.36L21 8"/><path d="M21 3v5h-5"/>',
  message: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  handoff: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m17 11 2 2 4-4"/>',
  sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
  home: '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2h-4v-6H9v6H5a2 2 0 0 1-2-2z"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
  team: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.5a6.5 6.5 0 0 1 3.5 5.5"/>',
  chevrons: '<path d="m7 15 5 5 5-5M7 9l5-5 5 5"/>',
};
const icon = (n) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[n] || ""}</svg>`;
const hydrateIcons = (root = document) => root.querySelectorAll("[data-icon]").forEach((el) => { if (!el.innerHTML) el.innerHTML = icon(el.dataset.icon); });
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const clock = (d = new Date()) => new Date(d).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const MOCK_URL = "http://127.0.0.1:8001";
const STORE_KEY = "nova-supra-v1";

// Call lines (Hindi + Kannada packs), VENDOR and number display come from lines.js
const { VENDOR, showNumber, packs: PACKS } = window.NOVA_LINES;
// The customer being onboarded. The customer's language is picked in Demo controls.
const CUSTOMER = { id: "CUS-0142", name: "Kaveri Handlooms" };   // the owner comes from the call
const LANG_SHORT = { "hi-IN": "hi", "kn-IN": "kn" };

// =========================================================
// Offline demo: the scripted customer's replies, in order, per language.
// text = the transcript sent to the server (no paid STT). rec = an optional
// recording in test_audio/demo/<hi|kn>/ that plays so you can hear the customer.
// =========================================================
const OFFLINE_SCRIPTS = {
  "hi-IN": [
    { text: "हाँ जी, बोलिए।", rec: "greeting.wav" },                              // no name yet -> Nova asks again
    { text: "मेरा नाम सुमित है।", rec: "owner_name_misheard.wav" },               // Nova mishears the name...
    { text: "नहीं, गलत है।", rec: "no_wrong.wav" },                                 // ...the read-back catches it
    { text: "मेरा नाम सुमन है।", rec: "owner_name.wav" },                        // the right name
    { text: "हाँ, सही है।", rec: "yes_correct.wav" },                               // confirmed
    { text: "मेरा व्हाट्सऐप नंबर है नाइन एट फ़ोर फ़ाइव ज़ीरो वन टू।", rec: "number_partial.wav" }, // only 7 digits
    { text: "थ्री फ़ोर फ़ाइव।", rec: "number_rest.wav" },                           // the remaining 3
    { text: "हाँ।", rec: "yes.wav" },                                              // confirms 98450 12345
  ],
  "kn-IN": [
    { text: "ಹೇಳಿ, ಹೇಳಿ.", rec: "greeting.wav" },
    { text: "ನನ್ನ ಹೆಸರು ಸುಮಿತ್.", rec: "owner_name_misheard.wav" },
    { text: "ಇಲ್ಲ, ತಪ್ಪು.", rec: "no_wrong.wav" },
    { text: "ನನ್ನ ಹೆಸರು ಸುಮನ್.", rec: "owner_name.wav" },
    { text: "ಹೌದು, ಸರಿ.", rec: "yes_correct.wav" },
    { text: "ನನ್ನ ವಾಟ್ಸಾಪ್ ನಂಬರ್ ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ ಒಂದು ಎರಡು.", rec: "number_partial.wav" },
    { text: "ಮೂರು ನಾಲ್ಕು ಐದು.", rec: "number_rest.wav" },
    { text: "ಹೌದು.", rec: "yes.wav" },
  ],
};

// =========================================================
// State (saved to localStorage after every render)
// =========================================================
const STATUS_LABEL = { pending: "Pending", reported: "Reported", verified: "Verified", blocked: "Blocked" };
const freshState = () => ({
  planned: false,
  items: [],
  owner: null,               // confirmed owner name (English / Latin, shown on screen)
  ownerNative: null,         // same name as heard, in the customer's script (spoken read-back)
  number: null,              // confirmed WhatsApp number (10 digits)
  partialNumber: null,       // digits heard so far if still incomplete after the call
  customerLanguage: "hi-IN", // chosen in Demo controls: hi-IN or kn-IN
  language: null,            // {code, label} detected from the customer's speech
  engineerTask: null, engineerDoneAt: null, engineerMessages: [], engineerReplies: [],
  engineerSetup: false,      // simulated engineer has done the set-up task on the platform
  verification: null,
  summary: null, ctaShown: false, live: false, liveAt: null,
  firstBlock: null,          // short reasons from the first blocked test (for the founder report)
  events: [],                // activity: {id, tag, title, detail, at}
  turns: [],                 // transcript of the latest call
  showEnglish: false,
  showEarlier: false,
  tab: "phone",
  // transient (not saved)
  planning: false, verifying: false, callActive: false,
});
let state = freshState();
const TRANSIENT = ["planning", "verifying", "callActive"];
function save() {
  try {
    const copy = { ...state };
    TRANSIENT.forEach((k) => delete copy[k]);
    localStorage.setItem(STORE_KEY, JSON.stringify(copy));
  } catch {}
}
function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "null");
    if (saved) state = { ...freshState(), ...saved };
    state.items.forEach((i) => { i.checking = false; });
  } catch {}
}
const item = (id) => state.items.find((i) => i.id === id);
// Nova follows the language the customer actually speaks (if there's a pack
// for it), otherwise the customer's chosen language
const pack = () => PACKS[state.language?.code] || PACKS[state.customerLanguage] || PACKS["hi-IN"];

// ---------------- backend helpers ----------------
async function api(path, options) {
  const res = await fetch(path, options);
  if (!res.ok) {
    let msg = `${path} failed (${res.status})`;
    try { msg = (await res.json()).error || msg; } catch {}
    throw new Error(msg);
  }
  return res;
}
const post = async (path, body = {}) => (await api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).json();

let offlineMode = true;     // server-side setting, read from /config
let audioCache = new Map();
function fetchSpeech(text, voice) {
  const key = `${voice}|${text}`;
  if (!audioCache.has(key)) {
    const p = api("/speak", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, voice }) })
      .then((r) => r.blob()).then((b) => URL.createObjectURL(b));
    p.catch(() => audioCache.delete(key));
    audioCache.set(key, p);
  }
  return audioCache.get(key);
}
function playUrl(url, onStart) {
  return new Promise((resolve, reject) => {
    const a = new Audio(url);
    a.onended = resolve;
    a.onerror = () => reject(new Error("Could not play audio"));
    onStart?.(a);
    a.play().catch(reject);
  });
}
async function prefetchLines() {
  const p = PACKS[state.customerLanguage] || PACKS["hi-IN"];
  for (const line of Object.values(p.lines)) { try { await fetchSpeech(line.hi, p.voice); } catch {} }
}

// =========================================================
// Rendering
// =========================================================
function counts() {
  const c = { verified: 0, reported: 0, blocked: 0, pending: 0 };
  state.items.forEach((i) => c[i.status]++);
  return c;
}
const allVerified = () => state.planned && state.items.length > 0 && state.items.every((i) => i.status === "verified");
const isBlocked = () => Boolean(state.verification) && state.items.some((i) => i.status === "blocked");
const callDone = () => Boolean(state.owner && state.number);
const pill = (s, label) => `<span class="pill s-${s}"><span class="dot"></span>${esc(label || STATUS_LABEL[s])}</span>`;
const OWNER_AVATAR = {
  Nova: '<span class="avatar avatar-nova" aria-hidden="true"></span>',
  Customer: `<span class="avatar" aria-hidden="true">${icon("user")}</span>`,
  Engineer: `<span class="avatar" aria-hidden="true">${icon("wrench")}</span>`,
  CSM: `<span class="avatar" aria-hidden="true">${icon("headset")}</span>`,
};

function renderHeader() {
  let chip;
  if (state.live) chip = pill("verified", "Live");
  else if (allVerified()) chip = pill("verified", "Ready");
  else if (isBlocked()) chip = pill("blocked", "Blocked");
  else chip = `<span class="pill"><span class="dot"></span>${state.planned ? "Onboarding" : "Not started"} · Go live by Friday</span>`;
  $("status-chip").innerHTML = chip;
  document.querySelectorAll(".mode-btn").forEach((b) => {
    b.classList.toggle("active", (b.dataset.mode === "offline") === offlineMode);
    b.disabled = state.callActive;
  });
}

function renderSteps() {
  const blocked = isBlocked();
  const done = {
    plan: state.planned,
    call: callDone(),
    engineer: Boolean(state.engineerDoneAt) && !(blocked && state.engineerMessages.some((m) => !m.resolved)),
    verify: allVerified(),
    approve: state.live,
  };
  const steps = [["plan", "Plan"], ["call", "Call"], ["engineer", "Engineer"], ["verify", "Verify"], ["approve", "Approve"]];
  const current = steps.find(([k]) => !done[k])?.[0];
  $("steps").innerHTML = steps.map(([k, label], i) => `
    <li class="step ${done[k] ? "done" : ""} ${k === current ? "current" : ""} ${k === current && blocked ? "is-blocked" : ""}">
      <span class="step-num">${done[k] ? icon("check") : i + 1}</span><span class="step-label">${label}</span>
    </li>`).join("");

  let next;
  if (state.live) next = "<strong>Live.</strong> Onboarding complete.";
  else if (state.planning) next = "Building the plan…";
  else if (!state.planned) next = "<strong>Next:</strong> ask Nova to onboard.";
  else if (state.callActive) next = "Nova is on the call.";
  else if (!done.call) next = "<strong>Next:</strong> call the owner.";
  else if (state.verifying) next = "Testing the Supra AI setup…";
  else if (blocked) next = "<strong>Blocked:</strong> fix in Demo controls, then retry.";
  else if (!state.engineerDoneAt) next = "<strong>Next:</strong> engineer connects WhatsApp and FAQ.";
  else if (!done.verify) next = "<strong>Next:</strong> Nova verifies everything.";
  else next = "<strong>Next:</strong> approve go-live.";
  $("next-line").innerHTML = next;
}

function renderChecklist() {
  if (!state.planned) {
    $("counts").innerHTML = "";
    $("checklist").innerHTML = `<li class="empty-state">${state.planning ? '<span class="spinner"></span>Building the plan…'
      : `No plan yet. <button type="button" class="link" data-cmd="Onboard ${esc(CUSTOMER.name)}">Onboard ${esc(CUSTOMER.name)}</button>`}</li>`;
  } else {
    const c = counts();
    $("counts").innerHTML = ["verified", "reported", "blocked", "pending"]
      .map((s) => `<span><span class="dot s-${s}"></span><b>${c[s]}</b> ${s}</span>`).join("");
    $("checklist").innerHTML = state.items.map((it) => `
      <li class="check-row ${it.open ? "open" : ""}" id="row-${it.id}">
        <button type="button" class="check-main" data-row="${it.id}" aria-expanded="${Boolean(it.open)}">
          <span class="check-icon">${icon(it.icon)}</span>
          <span class="check-title">${esc(it.title)}</span>
          ${it.checking ? '<span class="pill"><span class="spinner"></span>Checking</span>' : pill(it.status)}
          <span class="check-chevron">${icon("chevron")}</span>
        </button>
        <div class="check-more">
          <span>${esc(it.desc)}</span>
          ${it.status === "blocked" && it.reason ? `<span class="plain"><span class="dot s-blocked"></span>${esc(it.reason)}</span>`
            : it.plain ? `<span class="plain">${esc(it.plain)}</span>` : ""}
          ${it.proof ? `<span class="tech">${esc(it.proof)}</span>` : ""}
          <span class="check-owner">${OWNER_AVATAR[it.owner] || ""}${esc(it.owner)}</span>
        </div>
      </li>`).join("");
  }
  const STRIPES = 48;
  const filled = state.planned ? Math.round((counts().verified / (state.items.length || 1)) * STRIPES) : 0;
  $("progress").innerHTML = Array.from({ length: STRIPES }, (_, i) => `<i class="${i < filled ? "s-verified" : ""}"></i>`).join("");
  $("progress").setAttribute("aria-valuenow", Math.round((filled / STRIPES) * 100));
}

// Verification report: hidden until the test has run; 5 plain checks, tech line on expand
let openChecks = new Set();
function renderVerification() {
  const r = state.verification;
  const show = Boolean(r) || state.verifying;
  $("verify-card").classList.toggle("hidden", !show);
  const col = document.querySelector(".col-left");
  col.classList.toggle("no-report", !show);
  // Verify step (report showing, not live yet): Verification report above the checklist, scrolled into view
  const first = show && !state.live;
  if (first && !col.classList.contains("report-first")) col.scrollTop = 0;
  col.classList.toggle("report-first", first);
  if (!show) return;
  if (state.verifying) {
    $("verify-meta").textContent = "";
    $("verification").innerHTML = `<p class="muted"><span class="spinner"></span>Testing the Supra AI setup…</p>`;
    return;
  }
  $("verify-meta").textContent = `Ran ${clock(r.ran_at)}`;
  $("verification").innerHTML = `<ul class="checks">${r.checks.map((c, i) => {
    const skip = c.proof === "skipped";
    return `<li class="vcheck ${openChecks.has(i) ? "open" : ""}">
      <button type="button" class="vcheck-main" data-vcheck="${i}">
        <span class="mark ${skip ? "" : c.ok ? "pass" : "fail"}">${skip ? "–" : icon(c.ok ? "check" : "x")}</span>
        <span>${esc(c.plain)}</span><span class="check-chevron">${icon("chevron")}</span>
      </button>
      <div class="tech">${esc(c.proof)}${c.detail ? `<br>${esc(c.detail)}` : ""}</div>
    </li>`;
  }).join("")}</ul>`;
}

function renderBanner() {
  const b = $("banner");
  let html = "", kind = "";
  if (state.live) {
    html = "";
  } else if (allVerified()) {
    kind = "ok";
    // "Approve go-live" waits until the spoken report has finished (see speakSummary)
    const cta = state.ctaShown || !reportBusy;
    html = `<div class="banner-main"><span class="ready-status"><span class="dot"></span>Ready to go live</span></div>
      <div class="banner-actions">
        <button type="button" class="btn" id="play-summary">${icon("speaker")}Play report</button>
        ${cta ? `<button type="button" class="btn btn-primary" id="approve">${icon("rocket")}Approve go-live</button>` : ""}
      </div>
      ${state.summary?.ready ? `<div class="banner-report" id="founder-report">${reportHtml()}</div>` : ""}`;
  } else if (isBlocked()) {
    kind = "bad";
    const reasons = (state.verification.reasons || []).join(" · ") || "A check failed";
    html = `<div class="banner-main">${pill("blocked")}<span class="banner-title">Go-live blocked</span><span class="banner-text">${esc(reasons)}</span></div>
      <div class="banner-actions"><button type="button" class="btn btn-primary" id="retry">${icon("refresh")}Retry test</button></div>`;
  }
  b.className = `banner card ${kind}` + (html ? "" : " hidden");
  b.innerHTML = html;
}

// Engineer's chat: Nova's task and follow-ups as bubbles, "Mark done" as the engineer's reply
function renderEngineer() {
  const t = state.engineerTask;
  if (!t) { $("engineer").innerHTML = `<p class="empty-note">No messages yet.</p>`; return; }
  const novaFrom = (at) => `<div class="msg-from"><span class="avatar avatar-nova" aria-hidden="true"></span>Nova · ${esc(clock(at))}</div>`;
  const youFrom = (at) => `<div class="msg-from">Engineer · ${esc(clock(at))}</div>`;
  const msgs = [
    { at: t.sentAt, html: `<div class="msg">${novaFrom(t.sentAt)}<div class="msg-body">
        <div>${esc(t.title)}</div>
        <div class="msg-endpoints mono"><span class="task-base">${esc(t.base_url)}</span>${t.endpoints.map((e) => `<span>${esc(e)}</span>`).join("")}</div>
      </div></div>` },
    ...state.engineerMessages.map((m) => ({ at: m.at, html: `<div class="msg ${m.resolved ? "" : "alert"}">${novaFrom(m.at)}<div class="msg-body">${esc(m.text)}</div></div>` })),
    ...state.engineerReplies.map((r, i) => ({ at: r, html: `<div class="msg me">${youFrom(r)}<div class="msg-body">${i ? "Fixed. Done again." : "Done: number connected, FAQ uploaded."}</div></div>` })),
  ].sort((a, b) => new Date(a.at) - new Date(b.at));

  const open = state.engineerMessages.some((m) => !m.resolved);
  let reply = "";
  if (!state.engineerDoneAt) reply = `<div class="reply"><span class="reply-label">Reply as the engineer</span>
      <button type="button" class="btn btn-primary btn-sm" id="engineer-done">${icon("check")}Mark done</button></div>`;
  else if (open) reply = `<div class="reply"><span class="reply-label">Reply as the engineer</span>
      <button type="button" class="btn btn-primary btn-sm" id="engineer-done">${icon("check")}Mark done again</button></div>`;

  $("engineer").innerHTML = `<div class="chat">
      <p class="chat-note">In real use, this is a Slack or WhatsApp message to your engineer.</p>
      ${msgs.map((m) => m.html).join("")}
      ${reply}
    </div>`;
  const panel = document.querySelector('[data-panel="engineer"]');
  requestAnimationFrame(() => { panel.scrollTop = panel.scrollHeight; });
}

function renderCall() {
  if (!state.callActive) {
    $("call-btn").disabled = !state.planned;
    $("call-btn").title = state.planned ? "" : "Build the plan first";
    if ($("orb").dataset.state === "idle") setOrb("idle");
  }
  $("lang-chip").innerHTML = state.language
    ? `<span class="pill">${esc(state.language.label)} detected</span>`
    : `<span class="pill">${esc(PACKS[state.customerLanguage].name)} customer</span>`;
  setChip("chip-owner", state.owner || "—", false, false);
  setChip("chip-number", state.number ? showNumber(state.number) : state.partialNumber ? `${showNumber(state.partialNumber)}…` : "—",
    !state.number && Boolean(state.partialNumber), false);
  renderTranscript();
}

// Transcript: customer's language by default (EN toggle), last two exchanges, older collapsed
function renderTranscript() {
  const box = $("transcript");
  $("en-toggle").setAttribute("aria-pressed", String(state.showEnglish));
  if (!state.turns.length) { box.innerHTML = `<div class="transcript-empty">No call yet.</div>`; return; }
  const SHOW = 4;
  const hidden = state.showEarlier ? 0 : Math.max(0, state.turns.length - SHOW);
  const visible = state.turns.slice(hidden);
  box.innerHTML = (hidden ? `<button type="button" class="earlier" id="show-earlier">${hidden} earlier</button>` : "")
    + visible.map((t) => {
      if (t.kind === "caption") return `<div class="turn"><div class="turn-who">Nova</div><div class="turn-caption">${esc(t.text)}</div></div>`;
      if (t.kind === "message") return `<div class="bubble turn"><div class="bubble-label">WhatsApp · sent</div><div>${esc(t.hi)}</div><div class="bubble-en">${esc(t.en)}</div></div>`;
      if (t.unheard) return `<div class="turn unheard"><div class="turn-who">Customer</div><div class="turn-text">Couldn't hear that</div></div>`;
      const text = state.showEnglish ? (t.en ?? "…") : t.hi;
      return `<div class="turn"><div class="turn-who">${t.kind === "nova" ? "Nova" : "Customer"}</div><div class="turn-text">${esc(text)}</div></div>`;
    }).join("");
  box.scrollTop = box.scrollHeight;
}

// Activity: one line per event, detail on click, repeats grouped, last 8 shown
let openEvent = null;
let newestShown = null;
const TAG_ICON = { Call: "phone", Captured: "check", Reported: "send", Verified: "shield", Plan: "list", Task: "send",
  Blocked: "alert", Live: "rocket", Message: "message", Handoff: "handoff" };
function renderActivity() {
  const groups = [];
  for (const e of state.events) {
    const last = groups[groups.length - 1];
    if (last && last.title === e.title) { last.count++; last.at = e.at; last.id = e.id; last.details.push(e.detail); }
    else groups.push({ ...e, count: 1, details: [e.detail] });
  }
  const shown = groups.slice(-8).reverse();
  const newest = shown[0]?.id;
  $("timeline").innerHTML = shown.map((g) => `
    <li class="event ${openEvent === g.id ? "open" : ""} ${g.id === newest && newest !== newestShown ? "new" : ""}">
      <button type="button" class="event-main" data-event="${g.id}">
        <span class="event-node">${icon(TAG_ICON[g.tag] || "activity")}</span>
        <span class="event-text">
          <span class="event-title">${esc(g.title)}${g.count > 1 ? `<span class="event-count">×${g.count}</span>` : ""}</span>
          <span class="event-time">${clock(g.at)}</span>
        </span>
      </button>
      ${g.details.filter(Boolean).length ? `<div class="event-detail">${g.details.filter(Boolean).join("<br>")}</div>` : ""}
    </li>`).join("") || `<li class="muted">Nothing yet.</li>`;
  newestShown = newest;
}

function renderAll() {
  renderHeader(); renderSteps(); renderChecklist(); renderVerification(); renderBanner();
  renderEngineer(); renderCall(); renderActivity(); renderTabs();
  save();
}

function setItem(id, status, extra = {}) {
  const it = item(id);
  if (!it) return;
  Object.assign(it, { status, checking: false }, extra);
  renderAll();
  const row = $(`row-${id}`);
  row?.classList.add("flash");
  setTimeout(() => row?.classList.remove("flash"), 1400);
}

function addActivity(tag, title, detail = "") {
  state.events.push({ id: `${Date.now()}-${Math.random().toString(36).slice(2, 6)}`, tag, title, detail, at: new Date().toISOString() });
  renderActivity();
  save();
}

// ---------------- tabs ----------------
function renderTabs() {
  document.querySelectorAll(".tab").forEach((t) => {
    const on = t.dataset.tab === state.tab;
    t.classList.toggle("active", on);
    t.setAttribute("aria-selected", on);
  });
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("hidden", p.dataset.panel !== state.tab));
  const needsEngineer = (state.engineerTask && !state.engineerDoneAt && callDone())
    || state.engineerMessages.some((m) => !m.resolved);
  const dot = document.querySelector('.tab[data-tab="engineer"] .tab-dot');
  dot.classList.toggle("hidden", state.tab === "engineer" || !needsEngineer);
}
function showTab(name) { state.tab = name; renderTabs(); save(); }

// =========================================================
// Ask Nova
// =========================================================
let commandBusy = false;
let replyTimer = null;
function setReply(text, kind = "") {
  const el = $("command-reply");
  clearTimeout(replyTimer);
  if (!text) { el.classList.add("hidden"); return; }
  el.className = "popover " + kind;
  el.innerHTML = text;
  if (!text.includes("spinner")) replyTimer = setTimeout(() => el.classList.add("hidden"), kind === "error" ? 8000 : 4500);
}
function toggleSuggestions(show) { $("suggestions").classList.toggle("hidden", !show); }

async function runCommand(text) {
  text = (text || "").trim();
  if (!text || commandBusy) return;
  commandBusy = true;
  toggleSuggestions(false);
  $("command-run").disabled = true;
  setReply('<span class="spinner"></span>Thinking…');
  try {
    const { intent } = await post("/nova/command", { text });
    $("command-input").value = "";
    setReply("");
    if (intent === "onboard") {
      if (state.planned) setReply("Plan already built."); else await runPlan();
    } else if (intent === "call") {
      if (!state.planned) await runPlan();
      if (!session) startCall();
    } else if (intent === "verify") {
      if (!verifyReady()) setReply("Not ready to test yet."); else await runVerification();
    } else if (intent === "summary") {
      await speakSummary({ show: true });
    } else {
      setReply("Try: onboard, call, verify or summary.");
    }
  } catch (e) {
    setReply(esc(e.message || "Nova couldn't run that."), "error");
  } finally {
    commandBusy = false;
    $("command-run").disabled = false;
  }
}

async function voiceCommand() {
  if (commandBusy || session) return;
  if (offlineMode) { setReply("Voice commands need Live mode."); return; }
  let rec;
  try { rec = await MicRecorder.open(); } catch { setReply("Allow the microphone to speak.", "error"); return; }
  $("command-mic").classList.add("listening");
  setReply('<span class="spinner"></span>Listening…');
  try {
    const { wav } = await rec.record();
    if (!wav) { setReply("Couldn't hear that."); return; }
    const form = new FormData();
    form.append("audio", wav, "command.wav");
    form.append("mode", "hinglish");
    const { transcript } = await (await api("/transcribe", { method: "POST", body: form })).json();
    if (!transcript) { setReply("Couldn't hear that."); return; }
    $("command-input").value = transcript;
    await runCommand(transcript);
  } catch (e) { setReply(esc(e.message), "error"); }
  finally { $("command-mic").classList.remove("listening"); rec.close(); }
}

// =========================================================
// Plan
// =========================================================
async function runPlan() {
  if (state.planned || state.planning) return;
  state.planning = true;
  renderAll();
  const plan = await post("/nova/plan");
  state.planned = true;
  state.planning = false;
  for (const def of plan.items) {
    state.items.push({ ...def, status: "pending", checking: def.id === "account" });
    renderAll();
    await sleep(120);
  }
  addActivity("Plan", "Built plan", `${plan.items.length} items`);
  await sleep(350);
  const acc = plan.account;
  if (acc.status === "verified") {
    setItem("account", "verified", { plain: acc.plain, proof: acc.proof });
    addActivity("Verified", "Verified account", `${esc(acc.plain)}<br><span class="mono">${esc(acc.proof)}</span>`);
  } else {
    setItem("account", "blocked", { plain: acc.plain, proof: acc.proof, reason: acc.reason, open: true });
    addActivity("Blocked", "Account check failed", esc(acc.reason));
  }
  state.engineerTask = { ...plan.engineer_task, sentAt: new Date().toISOString() };
  addActivity("Task", "Sent task to engineer", esc(plan.engineer_task.title));
  renderAll();
}

// =========================================================
// Engineer + verification
// =========================================================
function engineerDone() {
  const again = Boolean(state.engineerDoneAt);
  const blockedBefore = state.items.filter((i) => i.status === "blocked").map((i) => i.id);   // what to fix
  state.engineerDoneAt = new Date().toISOString();
  state.engineerReplies.push(state.engineerDoneAt);
  state.engineerMessages.forEach((m) => { m.resolved = true; });
  setItem("testchat", "reported", { desc: "Engineer says WhatsApp and the FAQ are set up" });
  addActivity("Reported", "Engineer marked done");
  if (again) engineerFixes(blockedBefore).then(runVerification); else maybeAutoVerify();
}

// The simulated engineer: "Mark done" also does the work on the simulated Supra AI platform, so the
// demo runs end to end without Demo controls. Demo controls still work for showing other problems.
const mockPost = (path, body) => fetch(`${MOCK_URL}${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }).catch(() => {});
async function faqCount() {
  try { return (await (await fetch(`${MOCK_URL}/kb/${CUSTOMER.id}`)).json()).documents || 0; } catch { return 0; }
}
// First round, the set-up task: connect the confirmed number and make sure the FAQ is indexed.
// The bot language is left as it was, so the first test can still catch a wrong language.
async function engineerSetup() {
  if (state.number) await mockPost("/channels/whatsapp", { number: state.number, account: CUSTOMER.id });
  if (await faqCount() === 0) await mockPost(`/kb/${CUSTOMER.id}/upload`, { count: 3 });
  loadPlatform();
}
// Later rounds: fix exactly what the last test blocked on (what Nova's message asked for)
async function engineerFixes(blockedIds = []) {
  const blocked = (id) => blockedIds.includes(id);
  if (blocked("number") && state.number) await mockPost("/channels/whatsapp", { number: state.number, account: CUSTOMER.id });
  if (blocked("testchat")) {
    await mockPost(`/bot/${CUSTOMER.id}`, { reply_language: state.customerLanguage });
    if (await faqCount() === 0) await mockPost(`/kb/${CUSTOMER.id}/upload`, { count: 3 });
  }
  loadPlatform();
}

const verifyReady = () => state.planned && callDone() && Boolean(state.engineerDoneAt);
function maybeAutoVerify() {
  if (verifyReady() && !state.verifying && !state.verification) runVerification();
  else renderAll();
}

async function runVerification() {
  if (state.verifying || !verifyReady()) return;
  if (!state.engineerSetup) { state.engineerSetup = true; await engineerSetup(); }   // engineer's set-up task, before the first test
  state.verifying = true;
  ["owner", "number", "testchat", "training"].forEach((id) => { const it = item(id); if (it) it.checking = true; });
  renderAll();
  let r;
  try {
    r = await post("/nova/verify", { owner: state.owner, number: state.number });
  } catch (e) {
    state.verifying = false;
    state.items.forEach((i) => { i.checking = false; });
    renderAll();
    setReply(esc(e.message), "error");
    return;
  }
  state.verifying = false;
  state.verification = r;
  openChecks = new Set();
  state.items.forEach((i) => { i.checking = false; });
  for (const [id, res] of Object.entries(r.items)) {
    const it = item(id);
    if (!it) continue;
    // Blocked rows open automatically
    Object.assign(it, { status: res.status, plain: res.plain, proof: res.proof, reason: res.status === "blocked" ? res.reason : "", open: res.status === "blocked" });
  }
  if (r.outcome === "verified") {
    state.engineerMessages.forEach((m) => { m.resolved = true; });
    addActivity("Verified", "Verification passed", `${r.checks.length} checks passed`);
  } else {
    if (!state.firstBlock) state.firstBlock = r.reasons || [];
    addActivity("Blocked", "Verification blocked", esc((r.reasons || []).join(" · ") || r.reason));
    if (r.engineer_message) {
      state.engineerMessages.forEach((m) => { m.resolved = true; });
      state.engineerMessages.push({ text: r.engineer_message, at: new Date().toISOString(), resolved: false });
      addActivity("Task", "Messaged engineer", esc(r.engineer_message));
      state.tab = "engineer";
    }
  }
  renderAll();
  // Verify step: Nova reports the main activity to the founder, in English (Avinash)
  if (allVerified()) await speakSummary({ report: true });
}

// Founder report: Avinash says it in English while the key points type out
// on screen in step with the voice ("Here are your updates" + up to 4 points).
// Bullets reveal strictly top to bottom: bullet N types while Avinash says
// spoken_parts[N], and the next one starts only after it finishes.
let summaryAudio = null;
let reportShown = Infinity;   // characters of the report revealed so far (typewriter)
let typingRun = 0;
let reportBusy = false;       // true while the report is being spoken / typed (CTA hidden)
const STEADY_MS_PER_CHAR = 32;
const MIN_REAL_AUDIO_S = 1.2; // shorter = silence (offline / DRY_RUN): type at a steady pace

function reportParts() {
  const s = state.summary;
  return s?.ready ? [s.intro || "Here are your updates", ...(s.points || [])] : [];
}
function reportHtml() {
  const parts = reportParts();
  let left = reportShown;
  const typing = Number.isFinite(reportShown) && reportShown < parts.join("").length;
  const out = parts.map((text, i) => {
    if (left <= 0) return "";
    const shown = text.slice(0, Math.max(0, left));
    left -= text.length;
    const caret = typing && left < 0 ? '<span class="caret"></span>' : "";
    return i === 0 ? `<div class="report-intro">${esc(shown)}${caret}</div>` : `<li>${esc(shown)}${caret}</li>`;
  });
  const intro = out[0] || (typing ? '<div class="report-intro"><span class="caret"></span></div>' : "");
  const items = out.slice(1).filter(Boolean);
  return intro + (items.length ? `<ul class="report-points">${items.join("")}</ul>` : "");
}
function renderReport() { const el = $("founder-report"); if (el) el.innerHTML = reportHtml(); }

// Audio progress (0..1) -> characters to reveal. The audio is split into one
// slice per bullet, sized by that bullet's share of the spoken script, so each
// bullet types only while its own sentence is being said.
function charsAtProgress(frac) {
  const shown = reportParts();
  const spoken = state.summary?.spoken_parts?.length === shown.length ? state.summary.spoken_parts : shown;
  const weights = spoken.map((t) => t.length);
  const total = weights.reduce((a, b) => a + b, 0) || 1;
  let acc = 0, chars = 0;
  for (let i = 0; i < shown.length; i++) {
    const from = acc / total, to = (acc + weights[i]) / total;
    acc += weights[i];
    if (frac >= to) { chars += shown[i].length; continue; }
    if (frac > from) chars += Math.floor(shown[i].length * (frac - from) / (to - from));
    break;
  }
  return chars;
}

// Types the report; resolves when every bullet is shown. With real audio the
// typing follows the voice; without it (silence, autoplay blocked, error) it
// types at a steady pace from wherever it already is.
function typeReport(audio, run) {
  const total = reportParts().join("").length;
  return new Promise((resolve) => {
    const start = performance.now();
    const from = Number.isFinite(reportShown) ? reportShown : 0;
    const finish = () => { reportShown = Infinity; renderReport(); resolve(); };
    const tick = () => {
      if (run !== typingRun) return resolve();
      const known = audio && audio.duration && Number.isFinite(audio.duration);
      // wait (briefly) for the audio's length, so text and voice start together
      if (audio && !known && !audio.ended && performance.now() - start < 4000) { requestAnimationFrame(tick); return; }
      if (known && audio.duration >= MIN_REAL_AUDIO_S) {
        if (audio.ended) return finish();
        reportShown = charsAtProgress(Math.min(1, (audio.currentTime / audio.duration) * 1.04));
      } else {
        reportShown = Math.min(total, from + Math.floor((performance.now() - start) / STEADY_MS_PER_CHAR));
      }
      renderReport();
      if (reportShown >= total) return finish();
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });
}

// Show "Approve go-live" (once shown, it stays, including on replays)
function showCta() {
  reportBusy = false;
  if (!state.summary?.ready || state.ctaShown) return;
  state.ctaShown = true;
  save();
  renderBanner();
}

async function speakSummary({ show = false, report = false } = {}) {
  const statuses = Object.fromEntries(state.items.map((i) => [i.id, i.status]));
  state.summary = await post("/nova/summary", { owner: state.owner || "", number: state.number || "", statuses,
    language: state.customerLanguage, first_block: state.firstBlock || [] });
  const ready = state.summary.ready;
  // Activity keeps the full saved summary (process, first block, fix); the card shows key points only
  if (report && ready) addActivity("Message", "Reported to founder in English", esc(state.summary.en || ""));
  const run = ++typingRun;
  if (ready) { reportShown = 0; if (!state.ctaShown) reportBusy = true; }   // start blank; text types as Avinash speaks
  renderBanner();
  save();
  if (show && !ready) setReply(esc(state.summary.en));
  if (!ready) {
    try { await playUrl(await fetchSpeech(state.summary.spoken, "founder")); } catch {}
    return;
  }
  const safety = setTimeout(showCta, 60000);   // never leave the CTA stuck
  let audio = null;
  try {
    // Cached: Play report replays the same audio (no new paid call)
    const url = await fetchSpeech(state.summary.spoken, "founder");
    if (run !== typingRun) return;
    summaryAudio?.pause();
    const done = playUrl(url, (a) => { audio = a; summaryAudio = a; });
    const typed = typeReport(audio, run);
    await done;          // audio ended
    await typed;
    if (run === typingRun) showCta();
  } catch {
    // audio failed / autoplay blocked: finish typing at a steady pace, then show the CTA
    if (run !== typingRun) return;
    audio?.pause();
    const run2 = ++typingRun;
    await typeReport(null, run2);
    if (run2 === typingRun) showCta();
  } finally {
    clearTimeout(safety);
  }
}

function approveGoLive() {
  state.live = true;
  state.liveAt = new Date().toISOString();
  addActivity("Live", "Approved go-live");
  renderAll();
}

// =========================================================
// Demo controls drawer (mock Supra AI platform)
// =========================================================
let platform = null;  // {connected: [numbers], faq: n, lang: "en-IN"}
async function loadPlatform() {
  try {
    const [channels, kb, bot] = await Promise.all([
      fetch(`${MOCK_URL}/channels/whatsapp`).then((r) => r.json()),
      fetch(`${MOCK_URL}/kb/${CUSTOMER.id}`).then((r) => r.json()),
      fetch(`${MOCK_URL}/bot/${CUSTOMER.id}`).then((r) => r.json()),
    ]);
    platform = { connected: channels.map((c) => c.number), faq: kb.indexed, lang: bot.reply_language };
  } catch { platform = null; }
  renderPlatform();
}
function renderPlatform() {
  const langs = [["hi-IN", "Hindi"], ["kn-IN", "Kannada"]];
  const custLang = `<div class="seg">${langs.map(([c, n]) => `<button type="button" class="seg-btn ${state.customerLanguage === c ? "active" : ""}" data-custlang="${c}" ${state.callActive ? "disabled" : ""}>${n}</button>`).join("")}</div>`;
  if (!platform) {
    $("mock").innerHTML = `<div class="drawer-row"><span>Customer language</span>${custLang}</div><p class="muted small">Platform not reachable.</p>`;
    return;
  }
  const n = state.number;
  const connected = n && platform.connected.includes(n);
  const botLangs = [["en-IN", "EN"], ["hi-IN", "HI"], ["kn-IN", "KN"]];
  $("mock").innerHTML = `
    <div class="drawer-row"><span>Customer language</span>${custLang}</div>
    <ul class="records">
      <li class="record"><span>WhatsApp number</span>
        <span class="record-value mono">${n ? showNumber(n) : "not captured yet"}</span>
        ${n ? `<button type="button" class="link small" data-platform="${connected ? "disconnect" : "connect"}">${connected ? "Disconnect" : "Connect"}</button>` : "<span></span>"}</li>
      <li class="record"><span>FAQ documents</span><span class="record-value">${platform.faq} indexed</span>
        <button type="button" class="link small" data-platform="upload">Upload FAQ</button></li>
      <li class="record"><span>Bot reply language</span><span class="record-value"></span>
        <span class="seg">${botLangs.map(([c, l]) => `<button type="button" class="seg-btn ${platform.lang === c ? "active" : ""}" data-botlang="${c}">${l}</button>`).join("")}</span></li>
    </ul>`;
}
async function setCustomerLanguage(code) {
  if (state.callActive || code === state.customerLanguage) return;
  state.customerLanguage = code;
  state.language = null;
  try {
    await fetch(`${MOCK_URL}/accounts/${CUSTOMER.id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ preferred_language: code }) });
  } catch {}
  renderAll();
  renderPlatform();
  if (offlineMode) prefetchLines();
}
async function setBotLanguage(code) {
  await fetch(`${MOCK_URL}/bot/${CUSTOMER.id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reply_language: code }) });
  loadPlatform();
}
async function platformAction(action) {
  const n = state.number;
  if (action === "connect") await fetch(`${MOCK_URL}/channels/whatsapp`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ number: n, account: CUSTOMER.id }) });
  if (action === "disconnect") await fetch(`${MOCK_URL}/channels/whatsapp/${n}`, { method: "DELETE" });
  if (action === "upload") await fetch(`${MOCK_URL}/kb/${CUSTOMER.id}/upload`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ count: 3 }) });
  loadPlatform();
}
function openDrawer(open) {
  $("drawer").classList.toggle("open", open);
  $("drawer").setAttribute("aria-hidden", String(!open));
  $("drawer-scrim").classList.toggle("hidden", !open);
  if (open) loadPlatform();
}
async function resetDemo() {
  if (session) finishCall("ended");
  try { localStorage.removeItem(STORE_KEY); } catch {}
  try { await fetch(`${MOCK_URL}/reset`, { method: "POST" }); } catch {}
  location.reload();
}

// =========================================================
// Call
// =========================================================
const STATE_WORD = { idle: "Ready", speaking: "Speaking", listening: "Listening", thinking: "Thinking" };
function setOrb(s) {
  $("orb").dataset.state = s;
  $("orb-status").textContent = STATE_WORD[s];
}
const showError = (m) => { $("call-error").textContent = m; $("call-error").classList.remove("hidden"); };

function addTurn(kind, hi, en, extra = {}) {
  const t = { kind, hi, en, ...extra };
  state.turns.push(t);
  renderTranscript();
  save();
  return { setEnglish(text) { t.en = text; renderTranscript(); save(); } };
}

function setChip(id, text, partial = false, flash = true) {
  const el = $(id);
  el.textContent = text;
  el.classList.toggle("partial", partial);
  if (flash) { el.parentElement.classList.add("flash"); setTimeout(() => el.parentElement.classList.remove("flash"), 1200); }
}

let session = null;
class CallEnded extends Error {}
class HandOff extends Error {}
const checkAborted = () => { if (!session || session.aborted) throw new CallEnded(); };

async function say(line) {
  checkAborted();
  const p = pack();
  setOrb("thinking");
  const url = await fetchSpeech(line.hi, p.voice);
  checkAborted();
  if (line.caption) addTurn("caption", null, null, { text: line.caption }); // full line is spoken, short caption shown
  else addTurn("nova", line.hi, line.en);
  setOrb("speaking");
  await playUrl(url, (a) => { session.audio = a; });
  session.audio = null;
  checkAborted();
}

async function listen(mode) {
  checkAborted();
  setOrb("listening");
  $("done-btn").classList.toggle("hidden", offlineMode);
  let rec;
  try { rec = await session.recorder.record({ onLevel: (l) => $("orb").style.setProperty("--level", l) }); }
  finally { $("done-btn").classList.add("hidden"); $("orb").style.setProperty("--level", 0); }
  checkAborted();
  if (!rec.wav) return { transcript: "", language: null };
  setOrb("thinking");
  const form = new FormData();
  form.append("audio", rec.wav, rec.filename || "reply.wav");
  form.append("mode", mode);
  if (rec.demoText) form.append("demo_text", rec.demoText);
  const res = await (await api("/transcribe", { method: "POST", body: form })).json();
  checkAborted();
  return { transcript: res.transcript || "", language: res.language };
}

// One customer turn. Throws HandOff if they ask for a person.
async function ask(want, mode, partial = null) {
  const { transcript, language } = await listen(mode);
  if (language) { state.language = language; renderCall(); }
  if (!transcript) {
    addTurn("customer", "", "", { unheard: true });
    return { numbers: [], owner_name: null, confirm: null, wants_human: false };
  }
  const turn = addTurn("customer", transcript, null);
  const r = await post("/extract", { transcript, want, partial_number: partial });
  checkAborted();
  turn.setEnglish(r.english);
  if (r.wants_human) throw new HandOff();
  return r;
}

async function confirm(line) {
  await say(line);
  for (let i = 0; i < 2; i++) {
    const r = await ask([], pack().stt.general);
    if (r.confirm === "yes") return true;
    if (r.confirm === "no") return false;
    if (i === 0) await say(pack().lines.confirmUnclear);
  }
  return false;
}

function captureOwner(name, native) {
  session.owner = name;
  state.owner = name;
  state.ownerNative = native || name;
  setChip("chip-owner", name);
  setItem("owner", "reported", { desc: `Owner: ${name} (confirmed on the call)` });
  addActivity("Captured", "Confirmed owner name", esc(name));
  saveOwner(name);
}

// Save the owner confirmed on the call to the Supra AI account, so any name works end to end
async function saveOwner(name) {
  try {
    const r = await fetch(`${MOCK_URL}/accounts/${CUSTOMER.id}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ owner: name }) });
    if (r.ok) addActivity("Captured", "Saved owner to the Supra AI account", esc(name));
  } catch {}
}

function captureNumber(digits) {
  session.number = digits;
  state.number = digits;
  state.partialNumber = null;
  setChip("chip-number", showNumber(digits));
  setItem("number", "reported", { desc: `WhatsApp: ${showNumber(digits)} (confirmed on the call)` });
  addActivity("Captured", "Confirmed WhatsApp number", `<span class="mono">${esc(showNumber(digits))}</span>`);
}

async function collectOwner() {
  let prompt = pack().lines.askName;
  for (let attempt = 1; attempt <= 3 && !session.owner; attempt++) {
    await say(prompt);
    const r = await ask(["owner"], pack().stt.general);
    if (!r.owner_name) { prompt = pack().lines.nameAgain; addActivity("Call", "Asked again", "Owner name"); continue; }
    // Read back in the customer's script (Devanagari / Kannada); screen keeps English
    if (await confirm(pack().confirmName(r.owner_name_native || r.owner_name, r.owner_name))) { captureOwner(r.owner_name, r.owner_name_native); break; }
    addActivity("Call", "Corrected owner name", `Read back ${esc(r.owner_name)} · customer said no`);
    prompt = pack().lines.nameRetry;
  }
}

async function collectNumber() {
  let partial = null;
  let prompt = pack().lines.askNumber;
  for (let attempt = 1; attempt <= 5 && !session.number; attempt++) {
    await say(prompt);
    const r = await ask(["number"], pack().stt.digits, partial);
    const best = (r.numbers || [])[0];
    if (best && best.status === "complete") {
      if (await confirm(pack().confirmNumber(best.number))) { captureNumber(best.number); break; }
      addActivity("Call", "Corrected WhatsApp number", `Read back <span class="mono">${esc(best.display)}</span> · customer said no`);
      partial = null;
      prompt = pack().lines.numberRetry;
    } else if (best && best.status === "partial") {
      // Incomplete: say what Nova has and ask for the rest
      partial = best.number;
      state.partialNumber = partial;
      setChip("chip-number", `${showNumber(partial)}…`, true);
      addActivity("Call", "Asked again", `Heard <span class="mono">${esc(best.display)}</span> · ${best.missing} digits missing`);
      prompt = pack().numberRest(partial, best.missing);
    } else if (best) {
      partial = null;
      addActivity("Call", "Asked again", `Unclear number <span class="mono">${esc(best.display)}</span>`);
      prompt = pack().lines.numberUnclear;
    } else {
      addActivity("Call", "Asked again", r.numbers ? "No number in the reply" : "Couldn't hear the reply");
      prompt = partial ? pack().numberRest(partial, 10 - partial.length) : pack().lines.numberMissing;
    }
  }
}

async function runCall() {
  await say(pack().lines.opening);
  await collectOwner();
  if (!session.owner) { await say(pack().lines.giveUp); return "incomplete"; }
  await collectNumber();
  if (!session.number) { await say(pack().lines.doneIncomplete); return "partial"; }
  await say(pack().lines.done);
  return "complete";
}

async function startCall() {
  if (session || !state.planned) return;
  $("call-error").classList.add("hidden");
  session = { aborted: false, audio: null, recorder: null, owner: null, number: null, started: Date.now() };
  state.callActive = true;
  state.language = null; // detected again from this call's replies
  state.turns = [];
  state.showEarlier = false;
  state.tab = "phone";
  $("call-btn").disabled = false;
  $("call-btn").innerHTML = `${icon("phone")}End call`;
  $("call-btn").classList.remove("btn-primary");
  try {
    session.recorder = offlineMode ? DemoCustomer.open() : await MicRecorder.open();
  } catch {
    showError("Allow the microphone to call.");
    return finishCall(null);
  }
  addActivity("Call", "Called the owner", "AI introduction given");
  renderAll();
  startTimer();

  let outcome = null;
  try {
    outcome = await runCall();
  } catch (e) {
    if (e instanceof HandOff) {
      outcome = "handoff";
      try { await say(pack().lines.handoff); } catch {}
    } else if (e instanceof CallEnded) outcome = "ended";
    else { console.error(e); showError(e.message || "The call stopped."); outcome = "error"; }
  }
  finishCall(outcome);
}

function finishCall(outcome) {
  if (!session) return;
  const s = session;
  session = null;
  s.aborted = true;
  s.audio?.pause();
  s.recorder?.close();
  state.callActive = false;
  stopTimer();
  $("done-btn").classList.add("hidden");
  $("call-btn").innerHTML = `${icon("phone")}Call customer`;
  $("call-btn").classList.add("btn-primary");
  setOrb("idle");
  if (outcome == null) { renderAll(); return; }

  const secs = Math.round((Date.now() - s.started) / 1000);
  if (outcome === "handoff") addActivity("Handoff", "Handed off to human", "A team member will call back");
  if (s.owner || s.number) {
    const msg = pack().writtenSummary(state.owner, state.number, state.ownerNative);
    addTurn("message", msg.hi, msg.en);
    addActivity("Message", "Sent WhatsApp summary", esc(msg.en));
  }
  const label = { complete: "", partial: " · number incomplete", incomplete: " · details missing", ended: " · ended early", error: " · error", handoff: " · handed off" }[outcome];
  addActivity("Call", "Ended call", `${Math.floor(secs / 60)}m ${String(secs % 60).padStart(2, "0")}s${label}`);
  if (callDone() && !state.engineerDoneAt) state.tab = "engineer";  // Engineer step next
  maybeAutoVerify();
}

let timerId = null;
function startTimer() {
  const t0 = Date.now();
  timerId = setInterval(() => {
    const s = Math.floor((Date.now() - t0) / 1000);
    $("call-timer").textContent = `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
  }, 500);
}
function stopTimer() { clearInterval(timerId); $("call-timer").textContent = ""; }

// =========================================================
// Recorders. Both return { wav, filename?, demoText? } from record().
// =========================================================
const SILENCE_MS = 1500;

// Live: real microphone -> 16 kHz mono WAV, stops after ~1.5 s of silence
const MicRecorder = {
  async open() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const source = ctx.createMediaStreamSource(stream);
    const node = ctx.createScriptProcessor(4096, 1, 1);
    const mute = ctx.createGain();
    mute.gain.value = 0;
    source.connect(node); node.connect(mute); mute.connect(ctx.destination);
    let active = null;
    node.onaudioprocess = (e) => {
      if (!active) return;
      const data = e.inputBuffer.getChannelData(0);
      active.chunks.push(new Float32Array(data));
      let sum = 0;
      for (let i = 0; i < data.length; i++) sum += data[i] * data[i];
      const rms = Math.sqrt(sum / data.length);
      active.onLevel?.(Math.min(1, rms * 12));
      const now = performance.now();
      if (rms > 0.02) { active.heardSpeech = true; active.lastLoud = now; }
      const elapsed = now - active.start;
      if ((active.heardSpeech && now - active.lastLoud > SILENCE_MS) || (!active.heardSpeech && elapsed > 8000) || elapsed > 25000) active.finish();
    };
    return {
      record({ onLevel } = {}) {
        if (ctx.state === "suspended") ctx.resume();
        return new Promise((resolve) => {
          active = {
            chunks: [], heardSpeech: false, start: performance.now(), lastLoud: performance.now(), onLevel,
            finish: () => { const rec = active; active = null; if (!rec) return;
              resolve({ wav: rec.heardSpeech ? encodeWav(rec.chunks, ctx.sampleRate, 16000) : null }); },
          };
        });
      },
      stop() { active?.finish(); },
      close() { active?.finish(); stream.getTracks().forEach((t) => t.stop()); ctx.close(); },
    };
  },
};

// Offline demo: a scripted customer. Plays test_audio/demo/<hi|kn>/<rec> if you've
// recorded it; the transcript always comes from the script (no paid STT).
const DemoCustomer = {
  open() {
    const lang = state.customerLanguage;
    const script = (OFFLINE_SCRIPTS[lang] || OFFLINE_SCRIPTS["hi-IN"]).map((x) => ({ ...x }));
    let stopped = false;
    return {
      async record({ onLevel } = {}) {
        const next = script.shift();
        if (!next || stopped) return { wav: null };
        const tick = setInterval(() => onLevel?.(0.3 + Math.random() * 0.5), 100);
        let played = false;
        if (next.rec) {
          try {
            const res = await fetch(`/test_audio/demo/${LANG_SHORT[lang] || "hi"}/${encodeURIComponent(next.rec)}`);
            if (res.ok) {
              const blob = await res.blob();
              await new Promise((resolve) => {
                const a = new Audio(URL.createObjectURL(blob));
                a.onended = resolve; a.onerror = resolve;
                a.play().catch(() => setTimeout(resolve, 1200));
              });
              played = true;
            }
          } catch {}
        }
        if (!played) await sleep(1100); // "speaking" the scripted line
        clearInterval(tick);
        return { wav: encodeWav([new Float32Array(1600)], 16000, 16000), filename: "reply.wav", demoText: next.text };
      },
      stop() {},
      close() { stopped = true; },
    };
  },
};

function encodeWav(chunks, inRate, outRate) {
  const total = chunks.reduce((n, c) => n + c.length, 0);
  const input = new Float32Array(total);
  let off = 0;
  for (const c of chunks) { input.set(c, off); off += c.length; }
  const ratio = inRate / outRate;
  const outLen = Math.floor(input.length / ratio);
  const samples = new Int16Array(outLen);
  for (let i = 0; i < outLen; i++) {
    const a = Math.floor(i * ratio), b = Math.min(input.length, Math.floor((i + 1) * ratio));
    let sum = 0;
    for (let j = a; j < b; j++) sum += input[j];
    const v = Math.max(-1, Math.min(1, sum / Math.max(1, b - a)));
    samples[i] = v < 0 ? v * 0x8000 : v * 0x7fff;
  }
  const buf = new ArrayBuffer(44 + samples.length * 2);
  const v = new DataView(buf);
  const str = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
  str(0, "RIFF"); v.setUint32(4, 36 + samples.length * 2, true); str(8, "WAVE");
  str(12, "fmt "); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, outRate, true); v.setUint32(28, outRate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  str(36, "data"); v.setUint32(40, samples.length * 2, true);
  new Int16Array(buf, 44).set(samples);
  return new Blob([buf], { type: "audio/wav" });
}

// =========================================================
// Mode switch (tooltip says what each mode does)
// =========================================================
async function setMode(offline) {
  if (state.callActive || offline === offlineMode) return;
  const res = await post("/config", { offline });
  offlineMode = res.offline;
  audioCache = new Map();
  renderAll();
}

// =========================================================
// Events
// =========================================================
$("command-form").addEventListener("submit", (e) => { e.preventDefault(); runCommand($("command-input").value); });
$("command-input").addEventListener("focus", () => toggleSuggestions(!$("command-input").value));
$("command-input").addEventListener("input", (e) => toggleSuggestions(!e.target.value));
$("command-input").addEventListener("blur", () => setTimeout(() => toggleSuggestions(false), 150));
$("command-mic").addEventListener("click", voiceCommand);
$("call-btn").addEventListener("click", () => { if (session) finishCall("ended"); else startCall(); });
$("done-btn").addEventListener("click", () => session?.recorder?.stop());
$("drawer-open").addEventListener("click", () => openDrawer(true));
$("drawer-close").addEventListener("click", () => openDrawer(false));
$("drawer-scrim").addEventListener("click", () => openDrawer(false));
$("reset-demo").addEventListener("click", resetDemo);
$("en-toggle").addEventListener("click", () => { state.showEnglish = !state.showEnglish; renderTranscript(); save(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") { openDrawer(false); toggleSuggestions(false); } });

document.addEventListener("mousedown", (e) => {
  const s = e.target.closest(".suggestion");
  if (s) { e.preventDefault(); $("command-input").value = s.textContent.trim(); runCommand(s.textContent.trim()); }
});
document.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.dataset.cmd) runCommand(t.dataset.cmd);
  else if (t.classList.contains("tab")) showTab(t.dataset.tab);
  else if (t.classList.contains("mode-btn")) setMode(t.dataset.mode === "offline");
  else if (t.dataset.row) { const it = item(t.dataset.row); if (it) { it.open = !it.open; renderChecklist(); save(); } }
  else if (t.dataset.vcheck) { const i = +t.dataset.vcheck; openChecks.has(i) ? openChecks.delete(i) : openChecks.add(i); renderVerification(); }
  else if (t.dataset.event) { openEvent = openEvent === t.dataset.event ? null : t.dataset.event; renderActivity(); }
  else if (t.id === "show-earlier") { state.showEarlier = true; renderTranscript(); save(); }
  else if (t.id === "engineer-done") engineerDone();
  else if (t.id === "retry") runVerification();
  else if (t.id === "approve") approveGoLive();
  else if (t.id === "play-summary") speakSummary();
  else if (t.dataset.platform) platformAction(t.dataset.platform);
  else if (t.dataset.custlang) setCustomerLanguage(t.dataset.custlang);
  else if (t.dataset.botlang) setBotLanguage(t.dataset.botlang);
});

// =========================================================
// Start
// =========================================================
(async function start() {
  hydrateIcons();
  load();
  try { offlineMode = (await (await fetch("/config")).json()).offline; } catch {}
  renderAll();
  setOrb("idle");
  // Only pre-load voice lines offline (saved audio). In Live mode this would
  // make paid Gnani calls just by opening the page.
  if (offlineMode) prefetchLines();
})();
