# Nova, a voice-first onboarding operator that verifies, not just reports

**Nova calls a new customer in their own language, confirms their details by reading them back, tests the setup itself, and only asks the founder to approve go-live once every check has really passed.**

Onboarding a new customer usually means phone calls, chasing details on WhatsApp and following up with engineers, and most tools only report that a step "was done". Nova checks that it actually works.

Built for the Gnani AI challenge.

## What Nova does

1. **Plans the onboarding** from one command ("Onboard Kaveri Handlooms", typed or spoken) and checks the customer's account.
2. **Calls the owner in Kannada or Hindi** and asks for their name and WhatsApp number.
3. **Reads every detail back** for a yes or no ("ಸುಮನ್, ಸರಿನಾ?"). It handles a misheard name, a partly said number and a request for a human, and prepares a written WhatsApp summary.
4. **Messages the engineer** with the exact set-up task.
5. **Tests the setup itself** against the platform: number connected, FAQ indexed, a test chat in the customer's language, training booked.
6. **Marks each item Reported, Verified or Blocked.** When a check fails, Nova blocks go-live and tells the engineer exactly what to fix ("The test reply came in English. Please fix it and mark done again.").
7. **Reports to the founder in English**, with a spoken summary. The founder approves go-live.

## Demo scenario (fictional, demo only)

**Supra AI**, a fictional startup that sells an AI WhatsApp support bot, is onboarding **Kaveri Handlooms**, a fictional customer in Mysuru. The owner's name (Suman) and number (98450 12345) are synthetic.

## How Gnani is used

| Gnani model | Used for |
|---|---|
| **Prisma** speech to text (`prisma-v3.0`) | The customer's replies in Kannada, Hindi and code-mixed speech (Kanglish, Hinglish), plus a verbatim mode for digits so phone numbers come through exactly |
| **Timbre** text to speech (`timbre-v3.0`, `timbre-v2.5`) | Nova's voices: **Lakshmi** (Kannada), **Nalini** (Hindi), and **Avinash** for the founder's English report |

**Sarvam** (`sarvam-105b-conversations`) is used only to pull the details out of what the customer said (name, number, yes or no) and to understand typed commands.

## What is built vs simulated

| Built and working | Simulated or out of scope |
|---|---|
| Real Gnani speech to text and voices in Live mode | **Supra AI platform**: a mock API (`backend/mock_system.py`) stands in for the real product |
| Real HTTP checks against that platform | **Phone line**: the "call" uses your laptop microphone and speakers, not a telephone |
| Hindi and Kannada call flow with read-back and correction | **Engineer**: "Mark done" applies the engineer's fix on the mock platform |
| Phone-number normaliser (Kannada, Hindi and English digit words) | **WhatsApp summary**: shown in the app, not sent |
| Verification, blocking and the founder report | Runs locally only; not deployed |

## Folder structure

```
backend/
  app.py            Flask app: serves the page and the API, starts the mock platform
  mock_system.py    Simulated Supra AI platform (accounts, WhatsApp, FAQ, test chat, calendar) on port 8001
  nova_flow.py      Plan, verification checks, founder report
  stt.py, tts.py    Gnani Prisma (speech to text) and Timbre (voices)
  extract.py        Sarvam: name, number, yes/no from the transcript
  dialog.py         Call turn logic (language detection, yes/no)
  phone_number.py   Turns spoken digits into a 10-digit mobile number
  offline.py        Offline mode: scripted customer, saved audio, no paid calls
  tts_cache/        Saved Nova audio, so Offline mode needs no paid calls
  test_*.py         Tests
frontend/
  index.html, app.js, styles.css
  lines.js          Language packs: everything Nova says, in Hindi and Kannada
tools/              Voice the lines once, check the audio cache, write docs/call-lines.md
docs/call-lines.md  Every line Nova says, with its English meaning
nova-intro/         Source for the intro video (HTML animation, render and voice-over scripts)
```

## Setup and run

You need **Python 3.10+**. Node.js is only needed for the tools.

```bash
pip install -r backend/requirements.txt
```

Copy `.env.example` to **`.env.local`** (the app reads `.env.local`) and add your own keys:

```
GNANI_API_KEY=your-gnani-api-key
SARVAM_API_KEY=your-sarvam-api-key
DRY_RUN=true
```

Start Nova. This also starts the mock Supra AI platform on port 8001:

```bash
python backend/app.py --offline
```

Then open **http://localhost:8000**.

To run the mock platform on its own: `python backend/mock_system.py`.

### Offline vs Live mode

- **Offline** (`--offline`, or `DRY_RUN=true`): **no paid calls**. A scripted customer answers the call and Nova plays saved audio from `backend/tts_cache/`. The whole flow runs with no keys at all.
- **Live**: set `DRY_RUN=false` in `.env.local` and run `python backend/app.py`. You speak as the customer through the microphone (use Chrome and allow mic access). This makes real Gnani and Sarvam calls.

Use the **Live / Offline** switch and **Demo controls** (top right) to change mode, pick Kannada or Hindi, and reset the demo.

## Tests

```bash
cd backend
python test_phone_number.py   # 31 cases: spoken digits in Kannada, Hindi and English
python test_dialog.py         # 26 cases: call turn logic
```

## Demo

- **Video:** [add link]
- **Demo steps:**
  1. Ask Nova: click the mic and say "Onboard Kaveri Handlooms".
  2. Call customer, then answer in Kannada: "ನನ್ನ ಹೆಸರು ಸುಮನ್.", "ಹೌದು, ಸರಿ.", then the number one digit at a time, then "ಹೌದು, ಸರಿ."
  3. Engineer's chat → **Mark done**. The first test is blocked: the bot replies in English.
  4. **Mark done again**. Nova re-tests: all verified, and Avinash reads the English report.
  5. **Approve go-live**.

## Limitations and honest scope

- The Supra AI platform, the engineer and the WhatsApp summary are simulated; there is no real telephony.
- Live mode needs a quiet room and a headset. Very rare names can be misheard, but the read-back catches them.
- A number must be a 10-digit Indian mobile number starting with 6 to 9.
- In Offline mode a few scripted read-backs have no saved audio and play silently (the Hindi number read-back, the deliberately misheard name "Sumit", and the "rest of the number" line).
- Runs on one laptop. There is no login, database or deployment.

## Author

Sayeda Tasmia Fathima
