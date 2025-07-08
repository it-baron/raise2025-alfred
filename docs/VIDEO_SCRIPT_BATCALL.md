# Batcall Assistant - 5-Minute Demo Video Script

**Format**: One-take screencast
**Setup**: MacBook screen + iPhone visible on desk
**Duration**: 5:00 minutes

---

## [0:00-0:10] Scene Opens

**[VISUAL: Clean MacBook desktop with terminal/UI open, iPhone on desk]**

**ACTION**: User picks up iPhone and dials +33 4 83 24 42 81

---

## [0:10-0:30] Password Authentication

**ASSISTANT** (standard voice): "Hello, I am the Butler. Please tell me your password."

**USER**: "batman"

**ASSISTANT**: "Password accepted. Welcome home Bruce Wayne..."

**[VISUAL: Terminal/UI transitions to dark "cave mode" theme]**

---

## [0:30-1:00] Alfred Introduction

**ALFRED** (British accent): "Good evening, Bruce Wayne. I am Alfred, your assistant in the cave."

**[VISUAL: Alfred assistant UI appears on MacBook]**

**ALFRED**: "You can ask me to:

- Schedule tasks
- Read your mail
- Create drafts
  Just tell me what you'd like to do."

---

## [1:00-1:45] Email Reading Demo

**USER**: "Read my mail"

**ALFRED**: "Certainly. Reading your inbox..."

**[VISUAL: Email summaries appear on screen]**

- 📨 Lucius Fox: "Prototype upgrade ready for review"
- 📨 Commissioner Gordon: "Midnight signal test successful"
- 📨 Selina Kyle: "Dinner still on?"

**ALFRED**: "You have 3 new messages. I've summarized them for you. What would you like to do next?"

---

## [1:45-2:30] Draft Creation

**USER**: "Create a draft to Lucius: I'll review the upgrade tonight"

**ALFRED**: "Creating draft to Lucius: 'I'll review the upgrade tonight.' Draft saved."

**[VISUAL: Draft confirmation appears]**

**ALFRED**: "Would you like to send it now or save for later?"

**USER**: "Save for later"

**ALFRED**: "Very well, sir. Draft saved in your outbox."

---

## [2:30-3:15] Calendar Scheduling

**USER**: "Schedule a team sync tomorrow at 10am"

**ALFRED**: "Understood. Contacting the Calendar Agent..."

**[VISUAL: Terminal shows agent routing]**

```
user_input: "Schedule a team sync tomorrow at 10am"
intent: calendar.create_event
agent: calendar-agent
status: ✅ event_created
```

**ALFRED**: "Team sync scheduled for tomorrow at 10am. Shall I send invitations to the usual suspects?"

---

## [3:15-4:00] Technical Architecture Display

**[VISUAL: Split screen - phone call continues while showing architecture diagram]**

**NARRATOR** (voice-over): "Behind the scenes, each command flows through our multi-agent system:"

**[VISUAL: Animated flow diagram]**

```
Voice Input → Groq STT → Intent Detection → Agent Router → Service Agent → Response → Groq TTS
```

**NARRATOR**: "Specialized agents handle email, calendar, and tasks - all orchestrated by Coral Protocol in under 1.5 seconds."

---

## [4:00-4:30] Available Tools Demo

**USER**: "What tools do I have?"

**ALFRED**: "Here's what's currently available:

- Calendar integration for Wayne Enterprises
- Mail assistant for all your correspondence
- Task planner for both lives you lead
- Agentic responder for complex requests"

**[VISUAL: Tool icons appear on screen]**

---

## [4:30-5:00] Closing

**USER**: "That's all for now"

**ALFRED**: "As you wish. I'll wait here in the shadows, Master Wayne."

**[VISUAL: Screen fades to black with Alfred logo]**

**[VISUAL: Final screen shows]**

```
🦇 ALFRED - Your AI Butler
📞 +33 4 83 24 42 81
🔐 Password: batman

Built for Raise Your Hack 2025
Powered by Groq + Coral Protocol
```

---

## Production Notes

### Key Elements to Capture:

1. **Real phone call** to +33 4 83 24 42 81
2. **Password authentication** showing security
3. **Voice commands** processed in real-time
4. **Agent routing** visualization
5. **Multiple use cases** (email, calendar, tasks)

### Technical Requirements:

- Clean MacBook desktop
- iPhone clearly visible
- Terminal showing agent logs
- Smooth transitions between modes
- Clear audio capture of both user and Alfred

### Timing Breakdown:

- 0:00-0:30: Setup & authentication (30s)
- 0:30-1:00: Introduction (30s)
- 1:00-3:15: Core demos (2m 15s)
- 3:15-4:00: Technical explanation (45s)
- 4:00-5:00: Tools & closing (1m)

This focused 5-minute demo proves the concept while maintaining the Batman narrative!
