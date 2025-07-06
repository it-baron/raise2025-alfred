Here's a **turn-by-turn production cheat-sheet** that maps your 10-minute "_"Batcall Assistant"_ video to the stubbed system you'll build in Phase 0.
(It finishes the "Optional final screen" and shows exactly what has to run in the background at every moment.)

---

## 0. Prep at a glance

| Asset                   | Stub you'll show                                               | How to prep it quickly                                           |
| ----------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------- |
| **LiveKit room**        | `batcave-demo` (Hetzner)                                       | Room URL pre-loaded in browser tab.                              |
| **Coral Studio**        | Live graph; nodes renamed _GreeterA_, _Planner_, _GMailA_…     | Open in second tab; dark theme.                                  |
| **Alfred UI skin**      | Simple HTML page that swaps to dark mode on "cave mode" signal | One CSS class + "Alfred" SVG logo.                               |
| **Voice models**        | Groq Whisper (STT) & PlayAI TTS                                | Keep same voices for Butler + Alfred for speed (or pitch-shift). |
| **Email summaries**     | Hard-coded three strings in GMailA stub                        | JSON file in repo.                                               |
| **Calendar event stub** | Always "✅ event_created"                                      | Planner echoes to terminal.                                      |
| **Google Tasks stub**   | Always "✅ task_created"                                       | GTasksA echoes to terminal.                                      |

---

## 1. Time-coded rundown (all stubs)

| Time     | Screen / Action                                                         | Behind-the-scenes stub flow                                                                         |
| -------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **0:00** | Desktop + iPhone in frame.                                              | Voice worker already connected to LiveKit.                                                          |
| **0:10** | Butler TTS: "Hello... password."                                        | `GreeterA` publishes `IntentDetected{ raw:"batman" }`                                               |
|          | User: "batman."                                                         | Planner triggers `Task.System{ mode:"cave" }` → Alfred UI JS toggles dark class.                    |
| **0:30** | Alfred TTS greeting + menu list. Studio graph visible in corner.        | GreeterA detects "greeting" intent but does nothing further.                                        |
| **0:50** | User: "Read my mail."                                                   | `IntentDetected(ArchiveInt)` → `Task.Mail` → `GMailA` stub waits 0.3 s → `TaskCompleted(summary…)`. |
|          | Desktop shows three fake e-mail cards.                                  | Alfred UI JavaScript just inserts pre-set strings.                                                  |
| **2:00** | Alfred asks, user responds.                                             | No new Coral traffic yet.                                                                           |
| **2:20** | User: "Create draft to Lucius..."                                       | Planner emits `Task.Mail{ action:"draft" }` → gmailA stub returns `(stub) draft ok`.                |
|          | Draft confirmation overlay.                                             | Terminal logs: `taskId stub-XYZ status done`.                                                       |
| **3:30** | Alfred offers tool list; show icons.                                    | Static HTML list.                                                                                   |
| **5:00** | User: "Schedule a team sync tomorrow at 10 am."                         | Planner → `Task.Schedule` → gcalA stub fake success. Coral Studio edge lights up green.             |
| **7:00** | Narration overlay: animated arrow diagram (gif).                        | Pre-rendered gif; no runtime dependency.                                                            |
| **8:30** | User ends session. Alfred: "I'll wait in the shadows."                  | Voice worker sends `/leave` to LiveKit.                                                             |
| **9:00** | **Optional final screen (5 s)**:                                        |                                                                                                     |
|          | Big Bat-signal logo + QR code "Join beta / Scan Me."                    | Static PNG.                                                                                         |
|          | Caption: "_"Built with Groq · Coral Protocol · LiveKit · Vultr · 48 h"_ |                                                                                                     |

_(Total runtime ≈ 9 min 10 s; leaves \~50 s buffer.)_

---

## 2. Stub implementation checklist

1. **GreeterA (keyword only)**

   - `"batman"` → `Task.System{ mode:"cave" }`
   - Else route keywords: _read_, _draft_, _schedule_, _task_.

2. **Planner**

   - Maps intent → one downstream `Task.*` with fixed `taskId:"stub-<uuid>"`.

3. **GMailA / GCalA / GTasksA stubs**

   - Single Python FastAPI endpoint `/invoke` returning JSON with `status:"ok"` and a `result_digest` string you want Alfred to speak.

4. **Voice worker**

   - If `TaskCompleted` arrives, just TTS `result_digest`.
   - Ignore payment fields for now.

5. **UI toggles**

   - JavaScript listens to WebSocket from voice worker (`mode:"cave"` event) → add `.dark` class.
   - Email summaries & draft confirmation are static DOM inserts.

---

## 3. Quick script assets

| Asset                  | File                 | Note                                                                |
| ---------------------- | -------------------- | ------------------------------------------------------------------- |
| **Alfred dark CSS**    | `alfred.css`         | `.dark { background:#0a0a0a; color:#e0e0e0 }`                       |
| **Email HTML snippet** | `emails.html`        | 3 `<div class="mail">…` lines.                                      |
| **Flow GIF**           | `architecture.gif`   | Export from Figma or Keynote.                                       |
| **QR Code**            | `beta_qr.png`        | Points to wait-list Google Form.                                    |
| **Studio layout**      | `studio_preset.json` | Save positions so nodes aren't scattered when you load Studio live. |

---

## 4. Dry-run "Definition of Ready"

- [ ] Run `docker compose up stub` on Vultr: Studio shows 5 agents.
- [ ] Say "Read my mail" – Alfred UI updates, TTS speaks `(stub) inbox read`.
- [ ] "Schedule…" – Studio arrow to GCalA turns green.
- [ ] "I would like to buy groceries tomorrow" – Studio arrow to GTasksA turns green.
- [ ] End screen appears when worker receives "That's all".

Once all green, **record the one-take screencast** and keep moving to Phase 1 (swapping stubs for real Gmail / Calendar / Tasks calls).

That gives you a **fully coherent, visually impressive demo** even if APIs misbehave later—and judges see the multi-agent choreography in Coral Studio from the first second. Good luck! 🎬🦇
