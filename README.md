# ASTRA — AI Voice Assistant

> A voice-activated AI assistant built in Python that understands natural language, remembers conversations, and routes commands intelligently between multiple LLMs.

---

## What is ASTRA?

ASTRA is a personal AI voice assistant that you talk to — just say **"Jarvis"** or **"Emma"** to wake it up, speak your command, and it responds out loud. It can answer questions, play music, fetch live weather and news, search the web, open websites, send emails, and hold multi-turn conversations — all without you touching a keyboard.

Under the hood, it uses a three-layer routing system: direct keyword matching for simple actions, Groq (Llama 3.3 70B) for fast intent classification and casual chat, and Gemini for intelligent summarization and knowledge queries. Conversation memory persists across turns within a session, enabling contextual follow-up questions.

---

## Features

- 🎙️ **Wake word detection** — activates on "Jarvis" or "Emma" with distinct voice personas
- 🧠 **LLM-powered intent routing** — Groq classifies intent, Gemini handles knowledge and summarization
- 💬 **Conversation memory** — remembers context within a session for natural follow-up questions
- 🌤️ **Live weather** — fetches real-time weather via OpenWeatherMap and interprets it conversationally
- 📰 **News summarization** — pulls top headlines via NewsAPI and summarizes them naturally
- 🎵 **Music playback** — plays any song on YouTube via voice command using yt-dlp
- 🌐 **Website launcher** — opens YouTube, Google, LinkedIn, Netflix, Spotify, LeetCode and more
- 🔍 **Web search** — searches Google or YouTube directly from voice
- 📧 **Voice-commanded email** — send emails via Gmail SMTP using natural language
- 🗣️ **Bilingual recognition** — understands both English and Hindi commands
- 🔁 **Persistent session** — stays active until you say "stop", no repeated wake word needed

---

## Architecture

```
User speaks
     ↓
Wake word detected (Jarvis / Emma)
     ↓
listen_for_command()
     ↓
┌─────────────────────────────────────────┐
│           LAYER 1 — Keywords            │
│  "open", "play", "search" → direct      │
│  action, no LLM needed                  │
└──────────────────┬──────────────────────┘
                   │ no keyword match
                   ↓
┌─────────────────────────────────────────┐
│        LAYER 2 — Groq (Fast)            │
│  Classifies intent into:                │
│  weather / news / knowledge /           │
│  chat / email                           │
└──────────────────┬──────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│       LAYER 3 — Route to Handler        │
│  weather/news → fetch API → Gemini      │
│  knowledge    → Gemini                  │
│  chat         → Groq                    │
│  email        → Gmail SMTP              │
└─────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Voice Recognition | SpeechRecognition + Google STT |
| Text to Speech | pyttsx3 |
| Fast LLM (chat + routing) | Groq API — Llama 3.3 70B |
| Smart LLM (knowledge + summarization) | Google Gemini API — Gemini 3.1 Flash Lite |
| Weather | OpenWeatherMap API |
| News | NewsAPI |
| Music | yt-dlp + webbrowser |
| Email | Gmail SMTP (smtplib) |
| Translation | deep-translator |
| Environment | python-dotenv |

---

## Project Structure

```
ASTRA/
├── main.py        # entry point — wake word loop + session management
├── voice.py       # speech recognition + text to speech
├── api.py         # all API calls — Groq, Gemini, Weather, News, Email
├── command.py     # intent routing + action handlers
├── memory.py      # conversation history management
├── .env           # API keys and credentials (not uploaded)
├── .gitignore     # keeps keys and venv off GitHub
└── requirements.txt
```

---

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/shekhawat-a/ASTRA.git
cd ASTRA
```

**2. Create and activate virtual environment**
```bash
python -m venv env
env\Scripts\activate        # Windows
source env/bin/activate     # Mac/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create your `.env` file**
```
GEMINI_API_KEY=your_gemini_key_here
GROQ_API_KEY=your_groq_key_here
NEWS_API_KEY=your_news_key_here
WEATHER_API_KEY=your_weather_key_here
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
```

**5. Get your free API keys**
- Gemini → [aistudio.google.com](https://aistudio.google.com)
- Groq → [console.groq.com](https://console.groq.com)
- NewsAPI → [newsapi.org](https://newsapi.org)
- OpenWeatherMap → [openweathermap.org/api](https://openweathermap.org/api)

**6. Set up Gmail App Password (for email feature)**

Gmail requires an App Password to send emails programmatically:
- Go to [myaccount.google.com](https://myaccount.google.com) → Security
- Enable **2-Step Verification** (required)
- Go to **App Passwords** → Create new → Name it "ASTRA"
- Copy the 16-character password into your `.env` as `EMAIL_PASSWORD`

> Note: Use the App Password — not your regular Gmail password.

**7. Run**
```bash
python main.py
```

---

## How to Use

1. Run `python main.py`
2. Say **"Jarvis"** or **"Emma"** to wake the assistant
3. Speak your command naturally
4. Say **"stop"** / **"bye"** / **"exit"** to end the session

**Example commands:**
```
"What's the weather in Jaipur?"
"Play Believer by Imagine Dragons"
"Open LinkedIn"
"Search Python tutorials on YouTube"
"Who is APJ Abdul Kalam?"
"What's happening in the news today?"
"Send an email to rahul@gmail.com about tomorrow's meeting"
"Email john saying happy birthday"
"How are you?"
```

---

## How Email Works

ASTRA uses Gmail SMTP to send emails via voice commands. Groq extracts the recipient, subject, and body directly from your spoken command — no typing required.

```
You:   "Send an email to rahul@gmail.com about the project deadline"

ASTRA: Groq extracts →
       recipient: rahul@gmail.com
       subject:   "project deadline"
       body:      "about the project deadline"

       Gmail SMTP sends the email
       ASTRA confirms: "Email sent successfully"
```

Credentials are stored securely in `.env` and never hardcoded.

---

## How Memory Works

ASTRA remembers the last 10 exchanges within a session. This means follow-up questions work naturally:

```
You:   "Who is Virat Kohli?"
ASTRA: "Virat Kohli is an Indian cricketer..."

You:   "How many centuries does he have?"
ASTRA: (knows "he" = Virat Kohli from context)
       "He has 80 international centuries..."

You:   "Is he married?"
ASTRA: "Yes, he is married to Anushka Sharma..."
```

Memory clears automatically when you say "stop" or switch between Jarvis and Emma.

---

## Why Two LLMs?

| Task | Model | Reason |
|---|---|---|
| Intent classification | Groq (Llama 70B) | Sub-second response, speed critical |
| Casual conversation | Groq (Llama 70B) | Fast, lightweight |
| Email extraction | Groq (Llama 70B) | Fast structured JSON output |
| Weather interpretation | Gemini | Better natural language quality |
| News summarization | Gemini | Superior summarization |
| General knowledge | Gemini | More accurate factual responses |

---

## Free APIs Only

Every API used in this project has a free tier. Zero cost to run.

| API | Free Limit |
|---|---|
| Gemini 3.1 Flash Lite | 500 requests/day |
| Groq Llama 3.3 70B | 1,000 requests/day |
| OpenWeatherMap | 1,000 requests/day |
| NewsAPI | 100 requests/day (dev) |
| Gmail SMTP | 500 emails/day (free Gmail) |

---

## Future Roadmap

- [x] Gmail SMTP — send emails via voice
- [ ] Gmail API — read and reply to emails via voice
- [ ] Google Calendar integration — schedule meetings via voice
- [ ] Flask web UI with microphone button
- [ ] Persistent memory across sessions
- [ ] Wake word detection using Porcupine (no internet needed)
- [ ] WhatsApp integration

---

## Built By

**Abhishek Singh Shekhawat**
B.Tech CSE (AI/ML) — Chandigarh University

[LinkedIn](https://www.linkedin.com/in/shekhawat-abhi/) · [GitHub](https://github.com/shekhawat-a)

---

## License

MIT License — free to use, modify, and distribute.
