/* =========================================================
   Nova's call lines, one pack per customer language.
   Loaded by index.html before app.js, and by tools/lines_review.js
   (which writes docs/call-lines.md with character counts for review).

   Keep lines short: about 20 words max, the opening about 35.
   Each pack: TTS voice key (backend config.TTS_VOICES), STT modes
   (backend config.STT_SETTINGS), static lines {hi: native text, en: meaning},
   and a few lines built from values (name, number).
   ========================================================= */
(function (root) {
  // The company Nova works for. Change here.
  const VENDOR = { en: "Supra AI", hi: "सुप्रा एआई", kn: "ಸುಪ್ರಾ ಎಐ" };

  // 9845012345 -> "98450 12345"
  const showNumber = (d) => (d && d.length > 5 ? `${d.slice(0, 5)} ${d.slice(5)}` : d || "");
  const spell = (digits, words) => {
    const w = [...digits].map((c) => words[+c]);
    return w.length > 5 ? `${w.slice(0, 5).join(" ")}, ${w.slice(5).join(" ")}` : w.join(" ");
  };

  // ---------------- Hindi (Nalini, timbre-v2.5) ----------------
  const HI_DIGITS = ["ज़ीरो", "वन", "टू", "थ्री", "फ़ोर", "फ़ाइव", "सिक्स", "सेवन", "एट", "नाइन"];
  const HI_COUNT = ["", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ", "दस"];
  const HINDI = {
    code: "hi-IN",
    name: "Hindi",
    voice: "customer",
    voiceName: "Nalini",
    stt: { general: "hinglish", digits: "digits" },
    lines: {
      opening: {
        hi: `नमस्ते! मैं नोवा, ${VENDOR.hi} टीम की एआई असिस्टेंट। आपका व्हाट्सऐप सपोर्ट बॉट सेट करते हैं, बस दो छोटे सवाल। मैं कभी ओटीपी या बैंक डिटेल्स नहीं माँगूँगी; आप कभी भी "ह्यूमन" बोल सकते हैं।`,
        en: `Namaste! I'm Nova, an AI assistant from the ${VENDOR.en} team. Let's get your WhatsApp support bot set up. It's just two quick questions. I'll never ask for OTPs or bank details, and you can say "human" anytime.`,
        caption: "AI introduction given",
      },
      askName: { hi: "पहले, आपका नाम क्या है?", en: "First, what's your name?" },
      nameAgain: { hi: "माफ़ कीजिए, आपका नाम फिर से बताइए।", en: "Sorry, could you say your name again?" },
      nameRetry: { hi: "ठीक है, अपना नाम फिर से बताइए।", en: "Okay, please say your name again." },
      askNumber: { hi: "अब अपना व्हाट्सऐप नंबर एक-एक अंक करके बताइए।", en: "Now please tell me your WhatsApp number, one digit at a time." },
      numberRetry: { hi: "ठीक है, व्हाट्सऐप नंबर फिर से बताइए।", en: "Okay, please say the WhatsApp number again." },
      numberUnclear: { hi: "नंबर साफ़ नहीं आया। पूरे दस अंक फिर से बताइए।", en: "The number wasn't clear. Please say all ten digits again." },
      numberMissing: { hi: "नंबर सुनाई नहीं दिया। फिर से बताइए।", en: "I didn't hear a number. Please say it again." },
      confirmUnclear: { hi: "कृपया हाँ या ना में बताइए।", en: "Please answer yes or no." },
      handoff: { hi: "ठीक है, हमारी टीम से कोई जल्द ही आपको कॉल करेगा। धन्यवाद।", en: "Okay, someone from our team will call you shortly. Thank you." },
      giveUp: { hi: "कोई बात नहीं, हमारी टीम आपको दोबारा कॉल करेगी।", en: "No problem, our team will call you back." },
      done: {
        hi: "धन्यवाद! आपकी जानकारी सेव हो गई और व्हाट्सऐप पर सारांश भेज दिया है। हमारी टीम सेटअप पूरा करेगी, और बॉट लाइव होते ही मैं बता दूँगी।",
        en: "Thank you! I've saved your details and sent a summary on WhatsApp. Our team will finish the setup, and I'll confirm when the bot is live.",
      },
      doneIncomplete: { hi: "धन्यवाद! आपका नाम सेव हो गया, पर नंबर अधूरा है। हमारी टीम आपसे फिर बात करेगी।", en: "Thank you! Your name is saved, but the number is incomplete. Our team will follow up." },
    },
    // n = name as heard (spoken); nEn = English version for the EN line
    confirmName: (n, nEn) => ({ hi: `${n}, सही है?`, en: `${nEn || n}, correct?` }),
    confirmNumber: (d) => ({ hi: `${spell(d, HI_DIGITS)}, सही है?`, en: `${showNumber(d)}, correct?` }),
    numberRest: (have, missing) => ({
      hi: `मुझे ${spell(have, HI_DIGITS)} मिला। बाक़ी ${HI_COUNT[missing] || missing} अंक बताइए।`,
      en: `I have ${showNumber(have)}. Please say the remaining ${missing} digits.`,
    }),
    // ownerNative = name in the customer's script; owner = English (for the small English line)
    writtenSummary: (owner, number, ownerNative) => ({
      hi: `नाम: ${ownerNative || owner || "—"}। व्हाट्सऐप नंबर: ${showNumber(number) || "अधूरा"}। ग़लत हो तो जवाब दें।`,
      en: `Saved: ${owner || "—"}, ${showNumber(number) || "number incomplete"}.`,
    }),
  };

  // ---------------- Kannada (Lakshmi, timbre-v3.0) ----------------
  // Natural spoken Kanglish: English words (WhatsApp, bot, setup) in Kannada script.
  const KN_DIGITS = ["ಸೊನ್ನೆ", "ಒಂದು", "ಎರಡು", "ಮೂರು", "ನಾಲ್ಕು", "ಐದು", "ಆರು", "ಏಳು", "ಎಂಟು", "ಒಂಬತ್ತು"];
  const KN_COUNT = ["", "ಒಂದು", "ಎರಡು", "ಮೂರು", "ನಾಲ್ಕು", "ಐದು", "ಆರು", "ಏಳು", "ಎಂಟು", "ಒಂಬತ್ತು", "ಹತ್ತು"];
  const KANNADA = {
    code: "kn-IN",
    name: "Kannada",
    voice: "customer_kn",
    voiceName: "Lakshmi",
    stt: { general: "kanglish", digits: "digits_kn" },
    lines: {
      opening: {
        hi: `ನಮಸ್ಕಾರ! ನಾನು ನೋವಾ, ${VENDOR.kn} ಟೀಮ್‌ನ ಎಐ ಅಸಿಸ್ಟೆಂಟ್. ನಿಮ್ಮ ವಾಟ್ಸಾಪ್ ಸಪೋರ್ಟ್ ಬಾಟ್ ಸೆಟಪ್ ಮಾಡೋಣ, ಎರಡೇ ಚಿಕ್ಕ ಪ್ರಶ್ನೆ. ನಾನು ಯಾವತ್ತೂ ಓಟಿಪಿ ಅಥವಾ ಬ್ಯಾಂಕ್ ಡೀಟೇಲ್ಸ್ ಕೇಳಲ್ಲ, ಯಾವಾಗ ಬೇಕಾದರೂ "ಹ್ಯೂಮನ್" ಅಂತ ಹೇಳಿ.`,
        en: `Namaskara! I'm Nova, an AI assistant from the ${VENDOR.en} team. Let's get your WhatsApp support bot set up. It's just two quick questions. I'll never ask for OTPs or bank details, and you can say "human" anytime.`,
        caption: "AI introduction given",
      },
      askName: { hi: "ಮೊದಲು, ನಿಮ್ಮ ಹೆಸರು ಏನು?", en: "First, what's your name?" },
      nameAgain: { hi: "ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ಹೆಸರು ಇನ್ನೊಮ್ಮೆ ಹೇಳಿ.", en: "Sorry, could you say your name again?" },
      nameRetry: { hi: "ಸರಿ, ನಿಮ್ಮ ಹೆಸರು ಮತ್ತೆ ಹೇಳಿ.", en: "Okay, please say your name again." },
      // "ಬಾಟ್‌ನ ವಾಟ್ಸಾಪ್" ran together as "botsapp" in TTS, so "bot" is dropped here
      askNumber: { hi: "ಈಗ ವಾಟ್ಸಾಪ್ ನಂಬರ್ ಒಂದೊಂದಾಗಿ ಹೇಳಿ.", en: "Now tell me the WhatsApp number, one digit at a time." },
      numberRetry: { hi: "ಸರಿ, ವಾಟ್ಸಾಪ್ ನಂಬರ್ ಮತ್ತೆ ಹೇಳಿ.", en: "Okay, please say the WhatsApp number again." },
      numberUnclear: { hi: "ನಂಬರ್ ಸರಿಯಾಗಿ ಕೇಳಿಸಲಿಲ್ಲ. ಹತ್ತೂ ಅಂಕಿ ಮತ್ತೆ ಹೇಳಿ.", en: "The number wasn't clear. Please say all ten digits again." },
      numberMissing: { hi: "ನಂಬರ್ ಕೇಳಿಸಲಿಲ್ಲ. ಇನ್ನೊಮ್ಮೆ ಹೇಳಿ.", en: "I didn't hear a number. Please say it again." },
      confirmUnclear: { hi: "ದಯವಿಟ್ಟು ಹೌದು ಅಥವಾ ಇಲ್ಲ ಅಂತ ಹೇಳಿ.", en: "Please answer yes or no." },
      handoff: { hi: "ಸರಿ, ನಮ್ಮ ಟೀಮ್‌ನವರು ಬೇಗ ನಿಮಗೆ ಕಾಲ್ ಮಾಡ್ತಾರೆ. ಧನ್ಯವಾದ.", en: "Okay, someone from our team will call you shortly. Thank you." },
      giveUp: { hi: "ಪರವಾಗಿಲ್ಲ, ನಮ್ಮ ಟೀಮ್ ನಿಮಗೆ ಮತ್ತೆ ಕಾಲ್ ಮಾಡುತ್ತೆ.", en: "No problem, our team will call you back." },
      done: {
        hi: "ಧನ್ಯವಾದ! ನಿಮ್ಮ ಡೀಟೇಲ್ಸ್ ಸೇವ್ ಆಗಿದೆ, ವಾಟ್ಸಾಪ್‌ನಲ್ಲಿ ಸಮರಿ ಕಳಿಸಿದ್ದೀನಿ. ನಮ್ಮ ಟೀಮ್ ಸೆಟಪ್ ಮುಗಿಸುತ್ತೆ, ಬಾಟ್ ಲೈವ್ ಆದಾಗ ನಾನು ತಿಳಿಸ್ತೀನಿ.",
        en: "Thank you! I've saved your details and sent a summary on WhatsApp. Our team will finish the setup, and I'll confirm when the bot is live.",
      },
      doneIncomplete: { hi: "ಧನ್ಯವಾದ! ನಿಮ್ಮ ಹೆಸರು ಸೇವ್ ಆಗಿದೆ, ಆದರೆ ನಂಬರ್ ಪೂರ್ತಿ ಆಗಿಲ್ಲ. ನಮ್ಮ ಟೀಮ್ ಮತ್ತೆ ಕಾಲ್ ಮಾಡುತ್ತೆ.", en: "Thank you! Your name is saved, but the number is incomplete. Our team will follow up." },
    },
    confirmName: (n, nEn) => ({ hi: `${n}, ಸರಿನಾ?`, en: `${nEn || n}, correct?` }),
    confirmNumber: (d) => ({ hi: `${spell(d, KN_DIGITS)}, ಸರಿನಾ?`, en: `${showNumber(d)}, correct?` }),
    numberRest: (have, missing) => ({
      hi: `ನನಗೆ ${spell(have, KN_DIGITS)} ಸಿಕ್ತು. ಇನ್ನೂ ${KN_COUNT[missing] || missing} ಅಂಕಿ ಹೇಳಿ.`,
      en: `I have ${showNumber(have)}. Please say the remaining ${missing} digits.`,
    }),
    writtenSummary: (owner, number, ownerNative) => ({
      hi: `ಹೆಸರು: ${ownerNative || owner || "—"}. ವಾಟ್ಸಾಪ್ ನಂಬರ್: ${showNumber(number) || "ಪೂರ್ತಿ ಆಗಿಲ್ಲ"}. ತಪ್ಪಿದ್ದರೆ ರಿಪ್ಲೈ ಮಾಡಿ.`,
      en: `Saved: ${owner || "—"}, ${showNumber(number) || "number incomplete"}.`,
    }),
  };

  root.NOVA_LINES = { VENDOR, showNumber, packs: { "hi-IN": HINDI, "kn-IN": KANNADA } };
})(typeof window !== "undefined" ? window : globalThis);
