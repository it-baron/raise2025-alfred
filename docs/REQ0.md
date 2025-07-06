### Voice Inbox Concierge — Requirements & Business Solution (No Code)

---

## 1. Problem & Opportunity

- **Information overload:** Knowledge-workers receive \~120 emails/day and lose >1 hr/week triaging them.
- **Hands-free demand:** Commuters already consume podcasts/news; a voice-controlled inbox naturally fits this habit.
- **AI edge:** Sub-second speech↔text↔speech loops (Groq hardware) finally make conversational email viable.

---

## 2. Solution Overview

A cloud-hosted voice agent you summon in a browser (or car/earbuds) to **clean, reply and schedule** by speech, plus a **2-minute spoken digest** that auto-generates every weekday at 06 h 45 (Paris time).
It satisfies the hackathon’s “agentic workflow” rubric while demonstrating real-world value.

---

## 3. Core User Stories

| Role                  | “As a … I want to …”                                            | Success Criteria                                                         |
| --------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Professional commuter | Hear a concise audio brief of new priority emails while driving | Digest plays without touching the phone; ends in ≤2 min                  |
| Busy manager          | Say “Archive promos and draft replies to urgent messages”       | Those messages are archived, two drafts appear, agent confirms aloud     |
| Sales rep             | Say “Book 30-min with John Friday morning”                      | Calendar invite created, recipient added, confirmation voiced within 2 s |

---

## 4. Functional Requirements

1. **Voice Command Agent**

   - Understand natural-language requests containing _archive, draft, schedule_.
   - Perform Gmail & Google Calendar actions accordingly.
   - Speak a confirmation summary.

2. **Morning Digest**

   - Every weekday at 06:45 CEST, fetch ≤20 unread “Primary/Important” emails from last 24 h.
   - Summarise into \~250 words; convert to speech; expose via HTTPS endpoint `/daily-digest`.

3. **Health & Observability**

   - `/health` endpoint returns _200_ and build hash.
   - Basic request logging and error capture.

4. **Live Demo Room**

   - Public LiveKit room `voice-inbox-demo` available for judges to test.

---

## 5. Non-Functional Requirements

| Category                     | Requirement                                                                                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Latency**                  | End-to-end voice round-trip ≤1.5 s for typical request (Europe region).                                  |
| **Scalability (demo scope)** | Runs on a single 1 vCPU / 2 GB Vultr instance; ready to shard STT/LLM/TTS in separate workers post-hack. |
| **Security**                 | Secrets loaded from environment; OAuth tokens stored server-side only; HTTPS enforced.                   |
| **Reliability**              | Morning digest retries up to 3×; if fails, fallback email digest (text) is sent.                         |
| **Maintainability**          | Modular service layers (voice I/O, AI reasoning, email/calendar adapters); clear README & diagrams.      |

---

## 6. External Dependencies

| Service            | Purpose                                                                 | Notes                                                             |
| ------------------ | ----------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **Groq Cloud**     | Ultra-low-latency Whisper STT, Llama-3-70B (text), PlayAI TTS           | Mandatory for hackathon scoring                                   |
| **LiveKit Cloud**  | WebRTC signalling, media relays                                         | Free tier sufficient; self-host fallback container shipped        |
| **Google APIs**    | Gmail + Calendar manipulation                                           | Single OAuth “Desktop” client bound to founder’s account for demo |
| **Vultr Cloud VM** | Hosts worker container, FastAPI endpoints, optional self-hosted LiveKit |                                                                   |

---

## 7. Key Performance Indicators (post-hack)

- **Digest completion rate:** % of days digest generated & listened to within 30 min of creation.
- **Time saved per user:** Average archived + drafted + scheduled actions × estimated manual handling time.
- **Conversion:** Free-to-paid upgrade rate after 14-day trial.

---

## 8. Business Model & Go-to-Market

| Phase               | Offering                                                           | Revenue Stream               |
| ------------------- | ------------------------------------------------------------------ | ---------------------------- |
| **MVP (0–3 mo)**    | Free beta (Gmail only, 2 actions/day, weekday digest)              | Collect usage & testimonials |
| **Launch (3–9 mo)** | **Pro €9/mo**: unlimited actions, Slack/Teams push, weekend digest | Subscription SaaS            |
| **Growth (>9 mo)**  | **Enterprise**: custom models, on-prem deploy, admin analytics     | Seat licenses + setup fee    |

**Target beach-heads:** freelancers, sales teams, legal & consulting firms accustomed to heavy email workflows.

---

## 9. Competitive Advantage

- **Speed:** Groq inference <1 s voice round-trip vs. 3-6 s typical cloud LLM stacks.
- **Hands-free UX:** Pure voice, no taps; digest auto-plays.
- **Agentic extensibility:** Same architecture can add Slack, CRM, ticket systems without rewrites.

---

## 10. Roadmap Snapshot

| Month | Milestone                                                          |
| ----- | ------------------------------------------------------------------ |
| 0     | Hackathon submission; secure Vultr prize funding                   |
| 1     | Mobile PWA wrapper for one-tap access                              |
| 2     | Multi-language (French, Spanish) via Whisper + Llama prompt switch |
| 4     | Team dashboard & admin controls                                    |
| 6     | Marketplace integrations (HubSpot, Salesforce)                     |
| 9     | Fundraising seed round, \~€350 k for GTM push                      |

---

### How this meets hackathon scoring

1. **Innovation & impact:** Transforms a universal daily pain-point into a set-and-forget voice service.
2. **Technical excellence:** Demonstrates Groq’s full speech-pipeline + LiveKit WebRTC in production.
3. **Polish & UX:** Live, sub-second conversation and slick 2-minute digest prove readiness.
4. **Viability:** Clear SaaS path with freemium funnel and enterprise upsell.

---

**Next step:** lock these requirements into your submission form and craft the 3-minute pitch video around the “listen on your commute” hero use-case. You’re set to impress both judges and future users. 🚀
