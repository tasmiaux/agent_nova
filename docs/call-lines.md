# Nova call lines for review

Company: **Supra AI**. Generated from `frontend/lines.js` by `node tools/lines_review.js`.
Characters are what Gnani TTS bills. Lines with a name or number use sample values (सुमन / ಸುಮನ್ / Suman, 9845012345, partial 9845012). Static lines are voiced by `python tools/voice_lines.py`; name/number lines are voiced during live calls.

## Hindi (hi-IN) · voice Nalini · STT: hinglish / digits

| Line | Hindi | English meaning | Words | Chars |
|---|---|---|---:|---:|
| opening | नमस्ते! मैं नोवा, सुप्रा एआई टीम की एआई असिस्टेंट। आपका व्हाट्सऐप सपोर्ट बॉट सेट करते हैं, बस दो छोटे सवाल। मैं कभी ओटीपी या बैंक डिटेल्स नहीं माँगूँगी; आप कभी भी "ह्यूमन" बोल सकते हैं। | Namaste! I'm Nova, an AI assistant from the Supra AI team. Let's get your WhatsApp support bot set up. It's just two quick questions. I'll never ask for OTPs or bank details, and you can say "human" anytime. | 35 | 185 |
| askName | पहले, आपका नाम क्या है? | First, what's your name? | 5 | 23 |
| nameAgain | माफ़ कीजिए, आपका नाम फिर से बताइए। | Sorry, could you say your name again? | 7 | 34 |
| nameRetry | ठीक है, अपना नाम फिर से बताइए। | Okay, please say your name again. | 7 | 30 |
| askNumber | अब अपना व्हाट्सऐप नंबर एक-एक अंक करके बताइए। | Now please tell me your WhatsApp number, one digit at a time. | 8 | 44 |
| numberRetry | ठीक है, व्हाट्सऐप नंबर फिर से बताइए। | Okay, please say the WhatsApp number again. | 7 | 36 |
| numberUnclear | नंबर साफ़ नहीं आया। पूरे दस अंक फिर से बताइए। | The number wasn't clear. Please say all ten digits again. | 10 | 45 |
| numberMissing | नंबर सुनाई नहीं दिया। फिर से बताइए। | I didn't hear a number. Please say it again. | 7 | 35 |
| confirmUnclear | कृपया हाँ या ना में बताइए। | Please answer yes or no. | 6 | 26 |
| handoff | ठीक है, हमारी टीम से कोई जल्द ही आपको कॉल करेगा। धन्यवाद। | Okay, someone from our team will call you shortly. Thank you. | 12 | 57 |
| giveUp | कोई बात नहीं, हमारी टीम आपको दोबारा कॉल करेगी। | No problem, our team will call you back. | 9 | 46 |
| done | धन्यवाद! आपकी जानकारी सेव हो गई और व्हाट्सऐप पर सारांश भेज दिया है। हमारी टीम सेटअप पूरा करेगी, और बॉट लाइव होते ही मैं बता दूँगी। | Thank you! I've saved your details and sent a summary on WhatsApp. Our team will finish the setup, and I'll confirm when the bot is live. | 26 | 130 |
| doneIncomplete | धन्यवाद! आपका नाम सेव हो गया, पर नंबर अधूरा है। हमारी टीम आपसे फिर बात करेगी। | Thank you! Your name is saved, but the number is incomplete. Our team will follow up. | 16 | 77 |
| confirmName | सुमन, सही है? | Suman, correct? | 3 | 13 |
| confirmNumber | नाइन एट फ़ोर फ़ाइव ज़ीरो, वन टू थ्री फ़ोर फ़ाइव, सही है? | 98450 12345, correct? | 12 | 56 |
| numberRest | मुझे नाइन एट फ़ोर फ़ाइव ज़ीरो, वन टू मिला। बाक़ी तीन अंक बताइए। | I have 98450 12. Please say the remaining 3 digits. | 13 | 63 |
| writtenSummary (WhatsApp text, not voiced) | नाम: सुमन। व्हाट्सऐप नंबर: 98450 12345। ग़लत हो तो जवाब दें। | Saved: Suman, 98450 12345. | 11 | 60 |

**Hindi pack total: 960 characters** (900 voiced; the WhatsApp text isn't spoken). All lines within the word limits.

## Kannada (kn-IN) · voice Lakshmi · STT: kanglish / digits_kn

| Line | Kannada | English meaning | Words | Chars |
|---|---|---|---:|---:|
| opening | ನಮಸ್ಕಾರ! ನಾನು ನೋವಾ, ಸುಪ್ರಾ ಎಐ ಟೀಮ್‌ನ ಎಐ ಅಸಿಸ್ಟೆಂಟ್. ನಿಮ್ಮ ವಾಟ್ಸಾಪ್ ಸಪೋರ್ಟ್ ಬಾಟ್ ಸೆಟಪ್ ಮಾಡೋಣ, ಎರಡೇ ಚಿಕ್ಕ ಪ್ರಶ್ನೆ. ನಾನು ಯಾವತ್ತೂ ಓಟಿಪಿ ಅಥವಾ ಬ್ಯಾಂಕ್ ಡೀಟೇಲ್ಸ್ ಕೇಳಲ್ಲ, ಯಾವಾಗ ಬೇಕಾದರೂ "ಹ್ಯೂಮನ್" ಅಂತ ಹೇಳಿ. | Namaskara! I'm Nova, an AI assistant from the Supra AI team. Let's get your WhatsApp support bot set up. It's just two quick questions. I'll never ask for OTPs or bank details, and you can say "human" anytime. | 29 | 195 |
| askName | ಮೊದಲು, ನಿಮ್ಮ ಹೆಸರು ಏನು? | First, what's your name? | 4 | 23 |
| nameAgain | ಕ್ಷಮಿಸಿ, ನಿಮ್ಮ ಹೆಸರು ಇನ್ನೊಮ್ಮೆ ಹೇಳಿ. | Sorry, could you say your name again? | 5 | 36 |
| nameRetry | ಸರಿ, ನಿಮ್ಮ ಹೆಸರು ಮತ್ತೆ ಹೇಳಿ. | Okay, please say your name again. | 5 | 28 |
| askNumber | ಈಗ ವಾಟ್ಸಾಪ್ ನಂಬರ್ ಒಂದೊಂದಾಗಿ ಹೇಳಿ. | Now tell me the WhatsApp number, one digit at a time. | 5 | 33 |
| numberRetry | ಸರಿ, ವಾಟ್ಸಾಪ್ ನಂಬರ್ ಮತ್ತೆ ಹೇಳಿ. | Okay, please say the WhatsApp number again. | 5 | 31 |
| numberUnclear | ನಂಬರ್ ಸರಿಯಾಗಿ ಕೇಳಿಸಲಿಲ್ಲ. ಹತ್ತೂ ಅಂಕಿ ಮತ್ತೆ ಹೇಳಿ. | The number wasn't clear. Please say all ten digits again. | 7 | 48 |
| numberMissing | ನಂಬರ್ ಕೇಳಿಸಲಿಲ್ಲ. ಇನ್ನೊಮ್ಮೆ ಹೇಳಿ. | I didn't hear a number. Please say it again. | 4 | 33 |
| confirmUnclear | ದಯವಿಟ್ಟು ಹೌದು ಅಥವಾ ಇಲ್ಲ ಅಂತ ಹೇಳಿ. | Please answer yes or no. | 6 | 33 |
| handoff | ಸರಿ, ನಮ್ಮ ಟೀಮ್‌ನವರು ಬೇಗ ನಿಮಗೆ ಕಾಲ್ ಮಾಡ್ತಾರೆ. ಧನ್ಯವಾದ. | Okay, someone from our team will call you shortly. Thank you. | 8 | 53 |
| giveUp | ಪರವಾಗಿಲ್ಲ, ನಮ್ಮ ಟೀಮ್ ನಿಮಗೆ ಮತ್ತೆ ಕಾಲ್ ಮಾಡುತ್ತೆ. | No problem, our team will call you back. | 7 | 47 |
| done | ಧನ್ಯವಾದ! ನಿಮ್ಮ ಡೀಟೇಲ್ಸ್ ಸೇವ್ ಆಗಿದೆ, ವಾಟ್ಸಾಪ್‌ನಲ್ಲಿ ಸಮರಿ ಕಳಿಸಿದ್ದೀನಿ. ನಮ್ಮ ಟೀಮ್ ಸೆಟಪ್ ಮುಗಿಸುತ್ತೆ, ಬಾಟ್ ಲೈವ್ ಆದಾಗ ನಾನು ತಿಳಿಸ್ತೀನಿ. | Thank you! I've saved your details and sent a summary on WhatsApp. Our team will finish the setup, and I'll confirm when the bot is live. | 17 | 128 |
| doneIncomplete | ಧನ್ಯವಾದ! ನಿಮ್ಮ ಹೆಸರು ಸೇವ್ ಆಗಿದೆ, ಆದರೆ ನಂಬರ್ ಪೂರ್ತಿ ಆಗಿಲ್ಲ. ನಮ್ಮ ಟೀಮ್ ಮತ್ತೆ ಕಾಲ್ ಮಾಡುತ್ತೆ. | Thank you! Your name is saved, but the number is incomplete. Our team will follow up. | 14 | 89 |
| confirmName | ಸುಮನ್, ಸರಿನಾ? | Suman, correct? | 2 | 13 |
| confirmNumber | ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ, ಒಂದು ಎರಡು ಮೂರು ನಾಲ್ಕು ಐದು, ಸರಿನಾ? | 98450 12345, correct? | 11 | 65 |
| numberRest | ನನಗೆ ಒಂಬತ್ತು ಎಂಟು ನಾಲ್ಕು ಐದು ಸೊನ್ನೆ, ಒಂದು ಎರಡು ಸಿಕ್ತು. ಇನ್ನೂ ಮೂರು ಅಂಕಿ ಹೇಳಿ. | I have 98450 12. Please say the remaining 3 digits. | 13 | 76 |
| writtenSummary (WhatsApp text, not voiced) | ಹೆಸರು: ಸುಮನ್. ವಾಟ್ಸಾಪ್ ನಂಬರ್: 98450 12345. ತಪ್ಪಿದ್ದರೆ ರಿಪ್ಲೈ ಮಾಡಿ. | Saved: Suman, 98450 12345. | 9 | 66 |

**Kannada pack total: 997 characters** (931 voiced; the WhatsApp text isn't spoken). All lines within the word limits.

## Totals

| Pack | Voiced chars | All chars |
|---|---:|---:|
| Hindi | 900 | 960 |
| Kannada | 931 | 997 |

A typical call voices: opening + askName + confirmName + askNumber + confirmNumber + done (plus retries only when needed). Static lines are voiced once and then served from tts_cache/.
