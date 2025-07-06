### **Voice Inbox Concierge – “Ready-to-Ship” Spec**

| Section                       | Detail                                                                                                                                              | Why it matters             |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **Elevator one-liner**        | “Talk to your Gmail while you commute: archive promos, draft replies, book meetings, and hear a 2-minute morning digest—powered by Groq + LiveKit.” | Judges grasp value in 5 s. |
| **Hackathon tracks / prizes** | **Primary:** Vultr _Agentic Workflows_ (USD 5 000). <br>**Side-pot:** Best Use of Groq Speech (no extra work), plus “Most Innovative” wildcard.     | Maximises cash + odds.     |

---

## 1 · Scope-locked feature list (MVP + polish)

| #   | Capability                    | Done-is-done test                                                                                                                                                                                                                                                        |
| --- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Voice command inbox agent** | - Spoken request arrives in LiveKit room.<br> - Within ≤1.5 s voice round-trip:<br>  • Promotions ≤2 days old archived<br>  • Draft replies created for latest “Important” ✉️ (top 2)<br>  • Calendar event booked if requested<br> - Agent speaks back concise summary. |
| 2   | **Morning audio digest**      | GET `/:8000/daily-digest` streams MP3 generated @ 06 h 45 CEST Mon-Fri summarising ≤20 unread primary e-mails.                                                                                                                                                           |
| 3   | **/health** endpoint          | Returns HTTP 200 & “ok”.                                                                                                                                                                                                                                                 |
| 4   | **Live demo room**            | `wss://LIVEKIT_URL/voice-inbox-demo` is open & usable by judges.                                                                                                                                                                                                         |

💡 _Anything not in this table is out-of-scope—drop it if time is tight._

---

## 2 · System architecture (single Vultr VM)

```
Browser (Playground)
        ▲ WebRTC
        ▼
LiveKit Cloud  (free tier)
        ▼ gRPC
Vultr VM  (1 vCPU, 2 GB RAM)
  ├─ worker.py  ← LiveKit Agents SDK
  │    • STT  groq.whisper-large-v3-turbo
  │    • LLM  groq.llama3-70b-8192
  │    • TTS  groq.playai-tts  (voice="Fritz-PlayAI")
  │
  ├─ Google helpers
  │    • Gmail API  (archive, draft)
  │    • Calendar API (event)
  │
  ├─ Digest cron  (APSheduler 06:45 weekdays)
  │
  └─ FastAPI  (/:8000)
         • /health
         • /daily-digest
```

---

## 3 · Tech stack & repo layout

```
📂 inbox-concierge/
├─ Dockerfile
├─ requirements.txt
├─ .env.example           # redact keys in repo
├─ worker.py              # LiveKit Agent Session
├─ digest.py              # scheduler + MP3 writer
├─ README.md              # install, run, demo
└─ slides/
    ├─ 1_title.png
    ├─ 2_demo.gif
    ├─ 3_architecture.png
    └─ 4_business.png
```

### Key deps

```text
livekit-agents[groq]  ~=1.0
google-api-python-client
google-auth-oauthlib
fastapi  +  uvicorn
apscheduler
python-dotenv
```

---

## 4 · Environment variables (.env)

| Var                         | Example                           |
| --------------------------- | --------------------------------- |
| `LIVEKIT_URL`               | `wss://voice-inbox.livekit.cloud` |
| `LIVEKIT_API_KEY / SECRET`  | …                                 |
| `GROQ_API_KEY`              | …                                 |
| `GOOGLE_CLIENT_ID / SECRET` | …                                 |
| `GOOGLE_REFRESH_TOKEN`      | …                                 |
| `DIGEST_CRON_TZ`            | `Europe/Paris`                    |

_(Ship `.env.example`; keep real file only on VM & local.)_

---

## 5 · Milestone schedule (Paris time)

| When                 | Deliverable                                                                                   | Notes                  |
| -------------------- | --------------------------------------------------------------------------------------------- | ---------------------- |
| **Sat 5 Jul 23:00**  | • LiveKit room reachable<br>• STT→TTS “echo bot” works                                        | Validate Groq latency. |
| **Sun 6 Jul 18:00**  | • Inbox actions (archive, draft, schedule) via CLI tested<br>• Voice agent calls them         | Hard-code Gmail creds. |
| **Mon 7 Jul 22:00**  | • VM deployed (Docker) + `/health` green<br>• Digest cron writes MP3; `/daily-digest` streams | Full E2E.              |
| **Tue 8 Jul 12:00**  | • 3-min demo video recorded<br>• 4-slide deck exported                                        | Buffer for re-takes.   |
| **Tue 8 Jul ≤17:00** | **Submission** (GitHub, video link, live URL)                                                 | Triple-check form.     |

---

## 6 · Demo video script (02:30 total)

1. **Intro (0:10)** – camera: problem & claim.
2. **Live voice demo (0:40)** – speak request, show Gmail & Calendar changes, agent reply audio.
3. **Morning digest (0:20)** – play `/daily-digest` on phone.
4. **Tech slide (0:40)** – highlight Groq + LiveKit + Gmail.
5. **Business slide & ask (0:30)** – savings & next steps.
   _(Leave 10 s buffer.)_

---

## 7 · Submission checklist

- [ ] GitHub public repo (MIT license, README with build/run).
- [ ] `docker pull … && docker run …` works.
- [ ] LiveKit room & `/health` reachable from outside.
- [ ] 3-min MP4 on YouTube/Drive (public or unlisted).
- [ ] Slide deck PDF (4 pages).
- [ ] Filled Vultr track form **before 17:00 CEST, Tue 8 Jul**.

---

## 8 · Fast fail-safes

| Risk                         | Pre-emptive fix                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------- |
| Google OAuth refresh expires | Generate new token morning of submission.                                         |
| STT picks wrong words        | Wear headset in demo; include promo filter on transcript.                         |
| Traffic blocked              | Put VM in **FRA-1** (low latency to LiveKit EU servers).                          |
| LiveKit Cloud outage         | Backup self-hosted LiveKit in same VM (`docker compose up`) – switch URL in .env. |

---

### **You’re set.**

_Lock this spec, create the repo, and start cutting code now._
Ping me with your language preference (Python is assumed) or any blocker—I’ll supply code snippets, OAuth step-by-step, or last-minute deck polish as you need.
