// Writes docs/call-lines.md: every line Nova says, per language pack, with the
// English meaning, word count and character count (TTS is billed by characters).
// Reads the same frontend/lines.js the app uses, so the review always matches.
//
// Run from nova-ai/:  node tools/lines_review.js
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.join(__dirname, "..");
const ctx = { globalThis: {} };
ctx.window = ctx.globalThis;
vm.runInNewContext(fs.readFileSync(path.join(root, "frontend", "lines.js"), "utf8"), ctx);
const { packs, VENDOR } = ctx.window.NOVA_LINES;

// Sample values for lines built from the call
const SAMPLE = { name: "Suman", native: { "hi-IN": "सुमन", "kn-IN": "ಸುಮನ್" }, number: "9845012345", partial: "9845012", missing: 3 };
const WORD_LIMIT = { opening: 35, done: 30 }; // everything else: 20 (closing text was given longer)
const words = (t) => t.trim().split(/\s+/).filter(Boolean).length;
const chars = (t) => [...t].length;

let md = `# Nova call lines for review\n\n`;
md += `Company: **${VENDOR.en}**. Generated from \`frontend/lines.js\` by \`node tools/lines_review.js\`.\n`;
md += `Characters are what Gnani TTS bills. Lines with a name or number use sample values `;
md += `(${SAMPLE.native["hi-IN"]} / ${SAMPLE.native["kn-IN"]} / ${SAMPLE.name}, ${SAMPLE.number}, partial ${SAMPLE.partial}). `;
md += `Static lines are voiced by \`python tools/voice_lines.py\`; name/number lines are voiced during live calls.\n\n`;

const summary = [];
for (const [code, p] of Object.entries(packs)) {
  const rows = [];
  for (const [key, line] of Object.entries(p.lines)) rows.push([key, line]);
  rows.push(["confirmName", p.confirmName(SAMPLE.native[code] || SAMPLE.name, SAMPLE.name)]);  // read-back uses the native-script name
  rows.push(["confirmNumber", p.confirmNumber(SAMPLE.number)]);
  rows.push(["numberRest", p.numberRest(SAMPLE.partial, SAMPLE.missing)]);
  rows.push(["writtenSummary (WhatsApp text, not voiced)", p.writtenSummary(SAMPLE.name, SAMPLE.number, SAMPLE.native[code])]);

  md += `## ${p.name} (${code}) · voice ${p.voiceName} · STT: ${p.stt.general} / ${p.stt.digits}\n\n`;
  md += `| Line | ${p.name} | English meaning | Words | Chars |\n|---|---|---|---:|---:|\n`;
  let total = 0, voiced = 0, over = [];
  for (const [key, line] of rows) {
    const c = chars(line.hi), w = words(line.hi);
    total += c;
    if (!key.startsWith("writtenSummary")) voiced += c;
    const limit = WORD_LIMIT[key] || 20;
    const flag = w > limit ? " ⚠" : "";
    if (flag) over.push(`${key} (${w} words)`);
    md += `| ${key} | ${line.hi.replace(/\|/g, "\\|")} | ${line.en.replace(/\|/g, "\\|")} | ${w}${flag} | ${c} |\n`;
  }
  md += `\n**${p.name} pack total: ${total} characters** (${voiced} voiced; the WhatsApp text isn't spoken).`;
  md += over.length ? ` Over the word limit: ${over.join(", ")}.\n\n` : ` All lines within the word limits.\n\n`;
  summary.push([p.name, voiced, total]);
}
md += `## Totals\n\n| Pack | Voiced chars | All chars |\n|---|---:|---:|\n`;
for (const [n, v, t] of summary) md += `| ${n} | ${v} | ${t} |\n`;
md += `\nA typical call voices: opening + askName + confirmName + askNumber + confirmNumber + done `;
md += `(plus retries only when needed). Static lines are voiced once and then served from tts_cache/.\n`;

fs.writeFileSync(path.join(root, "docs", "call-lines.md"), md);
console.log(summary.map(([n, v, t]) => `${n}: ${v} voiced / ${t} total chars`).join("\n"));
