⸻

🎬 DEMO SCENARIO: "Batcall Assistant" — Phase 0 Stubbed Infrastructure Demo

**🎥 Format:** 30-second screencast (Phase 0 proof-of-concept)
**🖥️ Setup:** MacBook screen with Coral Studio + LiveKit room
**🎙️ Voice:** User speaks into browser, Alfred responds via Groq TTS
**📞 Live Access:** Call +33 4 83 24 42 81 to interact with Alfred directly
**🎯 Goal:** Demonstrate multi-agent orchestration with stubbed responses

⸻

## Phase 0 Demo Script (30 seconds)

### 0:00 — Scene Setup

**Visuals:**

- MacBook desktop with two browser tabs open:
  - Tab 1: Coral Studio (http://localhost:7000) showing agent graph
  - Tab 2: LiveKit room (batcave-demo) ready for voice input
- Terminal window showing `docker compose up` output (all services green)

**Narration:**
"Phase 0 demonstration: Multi-agent voice assistant with stubbed infrastructure."

⸻

### 0:05 — Show Agent Architecture

**Visuals:**

- Focus on Coral Studio dashboard
- 5 agent nodes visible and connected:
  - GreeterA (edge agent)
  - Planner (orchestrator)
  - GMailA (email service)
  - GCalA (calendar service)
  - GTasksA (task service)

**Narration:**
"All agents running: GreeterA, Planner, Gmail, Calendar, and Google Tasks agents."

⸻

### 0:10 — First Voice Command

**Action:**
User clicks into LiveKit room and says clearly:

**"Archive promos and draft replies to urgent messages"**

**Visuals:**

- Coral Studio animates the message flow:
  - GreeterA lights up (intent detection)
  - Arrow to Planner (routing)
  - Arrow to GMailA (service execution)
- Terminal shows logs:
  ```
  GreeterA: IntentDetected(ArchiveInt)
  Planner: Task.Mail → GMailA
  GMailA: TaskCompleted(stub) mail ok
  ```

**Alfred Response (TTS):**
"Mail processed. Two promotional emails archived, one draft created."

⸻

### 0:20 — Second Voice Command

**Action:**
User says:

**"I would like to buy groceries tomorrow"**

**Visuals:**

- Coral Studio shows different routing:
  - GreeterA → Planner → GTasksA path lights up
- Terminal logs:
  ```
  GreeterA: IntentDetected(TodoInt)
  Planner: Task.Todo → GTasksA
  GTasksA: TaskCompleted(stub) task created
  ```

**Alfred Response (TTS):**
"Task created: Buy groceries scheduled for tomorrow."

⸻

### 0:28 — Completion

**Visuals:**

- Quick pan showing all systems operational:
  - Coral Studio with active agent graph
  - Health endpoint: `curl localhost:8000/health` → 200 OK
  - MCP stubs responding on ports 9101-9103

**Narration:**
"Phase 0 complete: Multi-agent voice orchestration proven with stubbed responses."

⸻

## Extended Demo Script (Optional 5-minute version)

### 0:30 — Technical Deep Dive

**Narration:**
"Let's examine the architecture in detail."

**Visuals:**

- Show docker-compose services running:
  ```bash
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
  ```
- Highlight container stack:
  - coral-server (NATS broker)
  - coral-studio (dashboard)
  - 5 agent containers
  - 3 MCP stub servers
  - voice-worker (LiveKit integration)

⸻

### 1:00 — Test All Voice Commands

**Command 1:** "Create draft for Lucius with text: Review complete"

- **Route:** GreeterA → Planner → GMailA
- **Response:** "(stub) draft created for Lucius"

**Command 2:** "Book 30-min with Sarah tomorrow morning"

- **Route:** GreeterA → Planner → GCalA
- **Response:** "(stub) meeting scheduled with Sarah"

**Command 3:** "Tell me today's scheduled start times"

- **Route:** GreeterA → Planner → GCalA
- **Response:** "(stub) schedule: 9am standup, 2pm client call"

⸻

### 2:30 — MCP Stub Testing

**Visuals:**
Terminal commands demonstrating direct MCP stub access:

```bash
# Test Gmail MCP stub
curl localhost:9101/invoke -d '{"task":"archive"}'
# Response: {"status":"ok", "result_digest":"(stub) mail archived"}

# Test Calendar MCP stub
curl localhost:9102/invoke -d '{"task":"create_event"}'
# Response: {"status":"ok", "result_digest":"(stub) event created"}

# Test Google Tasks MCP stub
curl localhost:9103/invoke -d '{"task":"create_task"}'
# Response: {"status":"ok", "result_digest":"(stub) task added"}
```

⸻

### 3:30 — Performance Metrics

**Visuals:**

- Stopwatch overlay showing voice round-trip times
- All responses under 1.5 second target
- Coral Studio showing message latencies

**Metrics Displayed:**

- Voice latency: 0.8s average
- Agent response: 0.3s (stub delay)
- Total round-trip: 1.1s ✅

⸻

### 4:00 — Deployment Verification

**Visuals:**

- Browser accessing public Vultr VM:
  - `http://vm-ip:7000` → Coral Studio loads
  - `http://vm-ip:8000/health` → 200 OK response
- Security scan showing only allowed ports open:
  ```bash
  nmap vm-ip
  # 22/tcp   open  ssh
  # 7000/tcp open  coral-studio
  # 8000/tcp open  health-check
  # 9101-9103/tcp open  mcp-stubs
  ```

⸻

### 4:30 — Phase 1 Preview

**Narration:**
"Phase 0 proves the architecture. Phase 1 will replace stubs with real APIs."

**Visuals:**

- Quick mockup showing:
  - Real Gmail integration
  - Actual Google Calendar events
  - Live Google Tasks creation
  - Llama-3 intent classification
  - Coral micro-payments

⸻

## Technical Requirements for Demo

### Environment Setup

```bash
# Ensure all services running
docker compose up -d

# Verify Coral Studio accessible
open http://localhost:7000

# Verify LiveKit room ready
# (URL provided in environment variables)

# Test voice pipeline
echo "Test Groq STT/TTS integration"
```

### Recording Setup

- **Screen Resolution:** 1920x1080 (16:9 for hackathon submission)
- **Audio:** Clear microphone for voice commands
- **Browser:** Chrome/Safari with LiveKit WebRTC support
- **Recording Tool:** QuickTime/OBS with system audio capture

### Backup Plans

- **Voice Fails:** Have pre-recorded audio commands ready
- **Coral Studio Down:** Screenshots of agent graph as fallback
- **Network Issues:** Local docker-compose deployment as backup

⸻

## Success Criteria for Demo

### Phase 0 Proof Points

- [x] All 5 agents visible in Coral Studio
- [x] Voice commands route correctly through agent pipeline
- [x] Stub responses returned within latency targets
- [x] Multi-agent choreography visible in real-time
- [x] Health endpoints responding correctly
- [x] MCP stubs operational on all ports

### Judge Impact

- **Visual:** Real-time agent orchestration in Coral Studio
- **Audio:** Natural voice interaction with immediate responses
- **Technical:** Container-based deployment ready for scaling
- **Business:** Clear path from Phase 0 stubs to Phase 1 real APIs

⸻

**🎯 Demo Objective:** Prove multi-agent voice orchestration works end-to-end
**🚀 Next Step:** Phase 1 real API integration
**🏆 Hackathon Goal:** Vultr Track submission with live judge demo

_Ready for Raise Your Hack 2025 submission! 🎬_
