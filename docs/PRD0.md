# Product Requirements Document (PRD)

**Product:** Voice Inbox Concierge
**Revision:** **v1.2** ― _adds “Today Schedule” query_
**Date:** 5 July 2025

---

## 4 · Scope (updated final intent set)

### 4.1 Default behaviour

_(unchanged)_ – When no command is detected the agent executes:
**“Archive promos and draft replies to urgent messages.”**

### 4.2 Voice intents (MVP)

| #   | Spoken example                                                                        | System action                                                                                             | Voice reply style                                                        |
| --- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 1   | “Archive promos and draft replies to urgent messages.”                                | Gmail → archive last-48 h _Promotions_; create drafts for top-2 unread _Important_ threads.               | “Promos cleared; two drafts ready.”                                      |
| 2   | “Create draft for Michel with text: _Thanks for the slides—will review tonight._”     | Gmail → locate Michel’s latest thread, insert draft with supplied text.                                   | “Draft for Michel saved.”                                                |
| 3   | **Reminder** → “Book 30-min with John Friday morning.”                                | Google Calendar → event Fri 08:00-08:30, invite John.                                                     | “30-minute meeting with John booked Friday 08:00.”                       |
| 4   | **Event** → “I should take my kids from school at 17.”                                | Calendar → today 17:00-17:30 event, no invitees.                                                          | “Kid-pickup event set for 17 o’clock today.”                             |
| 5   | **Task** → “I would like tomorrow go to market.”                                      | Google Tasks → all-day task “Go to market” for tomorrow.                                                  | “Tomorrow’s task created.”                                               |
| 6   | **Schedule query** → “Tell me today’s scheduled start times.” (or simply “Reminders”) | Calendar → fetch today’s events & reminders starting now to 23:59; list title + start time (max 8 items). | “You have: 10 a.m. stand-up, 14 p.m. client call, 17 p.m. pick-up kids.” |

_(If more than 8 items, agent summarises: “plus 3 others after 18 p.m.”)_

### 4.3 Morning audio digest

_(unchanged)_ – Weekdays 06:45 CEST, 2-minute spoken summary of ≤20 unread priority emails.

---

## 6 · Functional Requirements (additions in **bold**)

- **Google APIs read/write:** Gmail (archive, draft), Calendar (event insert **+ list**), Google Tasks (task insert).
- **Intent parsing:** keyword + Llama JSON schema recognising new _ScheduleQuery_ intent.
- **Latency:** ≤1.5 s round-trip for all six intents, including **ScheduleQuery**.

---

## 8 · Open Questions (update)

1. In **ScheduleQuery**, do we include all-day events? _(default: yes, announced first)_
2. If calendar is empty, agent should say “You’re free until tomorrow.” – confirm tone.

_(Still safe for hackathon scope; decide at implementation.)_

---

All other sections (purpose, KPIs, timeline, non-functional, out-of-scope) remain as in v1.1.
