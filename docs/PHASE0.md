### Phase 0 – “Everything Runs (but Nothing Real Happens)”

The goal of this **stub sprint** is to prove that **every message route, every Coral wrapper, and every LiveKit hop works end-to-end** before you touch Gmail, Calendar, or Google Tasks.
By the end of this phase you can screen-record a full round-trip:

> voice → GreeterA (stub) → Planner (stub) → GMailA / GCalA / GTasksA (echo stubs) → spoken confirmation, **plus** Coral Studio showing the dance.

---

## 1 · Stub definitions & contracts

| Component     | Temporary logic                                                                                                                                                               | Must emit / return                                                                           |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **GreeterA**  | On any incoming transcript, tag intent by simple keyword rule: `“archive” → ArchiveInt; “draft” → DraftInt; “schedule” → EventInt; “task” → TodoInt; else ScheduleQuery`.     | Coral message `IntentDetected` with JSON `{ "intent": "ArchiveInt", "raw": "<transcript>" }` |
| **Planner**   | Map intent → one synthetic task:<br>`ArchiveInt → Task.Mail`<br>`DraftInt → Task.Mail`<br>`EventInt → Task.Schedule`<br>`TodoInt → Task.Todo`<br>`ScheduleQuery → Task.Query` | Coral `Task.*` message containing `"taskId":"stub-<uuid>"`, `"payment":0`                    |
| **GMailA**    | On `Task.Mail`, wait 0.3 s, reply `TaskCompleted` with `"summary":"(stub) mail ok"`                                                                                           | Coral reply plus console log                                                                 |
| **GCalA**     | On `Task.Schedule` or `Task.Query`, wait 0.3 s, reply `(stub) calendar ok` or fixed fake schedule list                                                                        | Coral reply                                                                                  |
| **GTasksA**   | On `Task.Todo`, wait 0.3 s, reply `(stub) task created`                                                                                                                       | Coral reply                                                                                  |
| **Voice out** | Whatever summary text arrives from service agent is TTS-echoed back to user                                                                                                   | LiveKit speech                                                                               |

---

## 2 · Runtime stack (docker-compose)

```
┌────────────────────── Vultr VM ──────────────────────┐
│  coral-server     (broker, NATS)                     │
│  coral-studio     (dashboard, port 7000)             │
│  greeter          (stub agent)                       │
│  planner          (stub agent)                       │
│  gmailA           (stub agent via coraliser)         │
│  gcalA            (stub agent via coraliser)         │
│  gtasksA          (stub agent via coraliser)         │
│  voice-worker     (LiveKit Agents, no real APIs)     │
└──────────────────────────────────────────────────────┘
LiveKit room continues to run on your Hetzner cluster.
```

_All service agents can be one **tiny Alpine container** executing a `sleep` + fixed JSON response—faster to ship._

---

## 3 · Implementation steps (± 4 hrs)

1. **Spin up Coral stack**

   - Pull docker-compose from _Coral-RaiseYourHack-Guide_.
   - Confirm `http://<vm>:7000` loads Studio.

2. **Stub agents via coraliser**

   - Write a 3-line `coraliser_settings.json` for gmailA, gcalA, gtasksA (HTTP stubs on ports 9001-9003).
   - Run `python coraliser.py …` – Studio should now list three service nodes.

3. **Greeter & Planner stubs**

   - Copy the _VoiceFrenchAgent_ skeleton, strip real logic, hard-code keyword switch.
   - Register both with `coral.register()`; watch nodes appear in Studio.

4. **Voice worker hookup**

   - Point LiveKit Agents SDK to Coral broker for event publishing.
   - For every completed service reply, just speak `result_digest` back.

5. **Dry run**

   - Join LiveKit room, say “Archive promos.”
   - Confirm Studio shows Greeter → Planner → gmailA path; end voice says “(stub) mail ok”.
   - Repeat with “Tell me today’s scheduled start times” → gcalA path.

6. **Completion criteria**

   - `/health` returns 200.
   - Studio graph animates for each command.
   - Voice round-trip ≤1.5 s (all local stubs).
   - No external API keys required yet.

---

## 4 · Deliverables for the stub milestone

| Artifact                     | Purpose                                                                             |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| **docker-compose.yml**       | One-command spin-up for broker, studio, five agents, voice worker                   |
| **README-stub.md**           | 60-second guide: clone → `docker compose up` → open Studio                          |
| **30-second screen capture** | Proof tape: voice command, Studio animation, spoken echo                            |
| **Issues backlog**           | List “Replace gmailA stub with real Gmail integration”, etc.—sets next sprint scope |

---

## 5 · Next sprint unlocks

- Swap each stub for real MCP Google calls (Gmail, Calendar, Tasks) one by one.
- Turn on `$CORAL` micro-bounty field once real agents succeed.
- Replace keyword Greeter with Llama3 JSON-schema classifier.

Achieving this stub milestone early gives you a safe rollback point and a visually complete demo if integration hits turbulence later.

---

### **PRD.md**

```markdown
# Product Requirements Document

**Product:** Voice Inbox Concierge
**Phase:** 0 – Stubbed Infrastructure Proof
**Last Updated:** 5 Jul 2025

---

## 1 · Purpose

Demonstrate an end-to-end, multi-agent voice workflow—running on Vultr, orchestrated by Coral Protocol—without relying on external APIs.
This stubbed release must be **visually demo-ready** (LiveKit voice loop, Coral Studio graph, TTS replies) and establish the skeleton for later real-API integration.

---

## 2 · Goals & Success Metrics

| Goal                              | KPI (for Phase 0)                                       |
| --------------------------------- | ------------------------------------------------------- |
| All roles visible in Coral Studio | 5 agent nodes + planner → service edges light up        |
| Voice round-trip                  | ≤ 1.5 s from spoken command to TTS reply                |
| Zero external secrets             | Demo runs with no Gmail / Calendar / Google Tasks creds |
| Judge-ready URL                   | `/health` on Vultr VM returns **200 OK**                |

---

## 3 · User Stories (stub scope)

1. **As a judge**, I can join the LiveKit room, say “Archive promos,” and hear a spoken response in under two seconds.
2. **As a viewer**, I see Coral Studio animate the flow from **Edge Agent → Planner Agent → GMail Agent**.
3. **As a developer**, I can run `docker compose up` on a fresh VM and all containers start green.

---

## 4 · Functional Scope

| Capability                                | Included in Phase 0? |
| ----------------------------------------- | -------------------- |
| Voice STT + TTS loop (Groq)               | ✔                    |
| Intent → Task routing (Planner)           | ✔ (lookup table)     |
| Service agents (GMail / GCal / GTasks)    | ✔ (stub echo)        |
| MCP stub servers                          | ✔                    |
| Real Gmail / Calendar / Google Tasks APIs | ✖ (Phase 1)          |
| Morning digest scheduler                  | ✖ (Phase 1)          |

---

## 5 · Non-Functional Requirements

| Area          | Requirement                                                     |
| ------------- | --------------------------------------------------------------- |
| Latency       | ≤ 1.5 s voice round-trip (EU region)                            |
| Deployability | Single `docker-compose.yml`, builds on a 1 vCPU / 2 GB Vultr VM |
| Security      | Only 22, 80/443, 7000, 8000, 9101-9103 exposed                  |
| Observability | `/health` endpoint + Coral Studio dashboard                     |

---

## 6 · Risks & Mitigations

| Risk                          | Mitigation                                              |
| ----------------------------- | ------------------------------------------------------- |
| Docker image bloat            | All Python services inherit one `python:3.11-slim` base |
| Cross-container DNS flakiness | Use explicit service names & depends_on in compose      |
| Voice latency spike           | Keep LiveKit media on Hetzner (low-latency region pair) |
| Demo complexity               | One-take screencast script prepared (see _DEMO.md_)     |

---

## 7 · Milestones

| Date (CEST)     | Deliverable                                         |
| --------------- | --------------------------------------------------- |
| **Jul 6 03:00** | All containers build & start locally                |
| **Jul 6 12:00** | Vultr deployment green (health, Studio, voice echo) |
| **Jul 6 18:00** | Phase 0 demo video recorded                         |
| **Jul 7 00:00** | Merge `phase0` branch to `main`, tag `v0.1.0`       |

---

_End of PRD_
```

---

### **TRD.md**

````markdown
# Technical Requirements Document

**Project:** Voice Inbox Concierge
**Phase:** 0 – Stubbed Infrastructure
**Revision:** 1.0 (matches PRD v0.1)
**Date:** 5 Jul 2025

---

## 1 · System Architecture (Phase 0)

```mermaid
flowchart LR
    subgraph LiveKit (Hetzner)
        V(Voice room batcave-demo)
    end
    subgraph Vultr VM
        direction TB
        LS[coral-server (NATS)]
        STUDIO(coral-studio)
        GREETER(Edge Agent – GreeterA)
        PLANNER(Planner Agent)
        GMAILA(GMail Agent)
        GCALA(GCal Agent)
        GTASK(GTask Agent)
        GW(gmail-mcp stub)
        CW(gcal-mcp stub)
        RW(red-mcp stub)
        VW(voice-worker)
    end
    V -- WebRTC --> VW
    VW -- pub/sub --> LS
    GREETER -- pub/sub --> LS
    PLANNER -- pub/sub --> LS
    GMAILA -- pub/sub --> LS
    GCALA -- pub/sub --> LS
    GTASK -- pub/sub --> LS
    PLANNER -->|HTTP JSON| GMAILA
    PLANNER --> GCALA
    PLANNER --> GTASK
    GMAILA -->|HTTP JSON| GW
    GCALA --> CW
    GTASK  --> RW
    STUDIO --- LS
```
````

---

## 2 · Container Manifest

| Name            | Image / Build Dir                     | Ports          | Key Env Vars                      |
| --------------- | ------------------------------------- | -------------- | --------------------------------- |
| `coral-server`  | `coralprotocol/coral-server:latest`   | 7777           | –                                 |
| `coral-studio`  | `coralprotocol/coral-studio:latest`   | 7000           | `CORAL_BROKER_URL`                |
| `greeter-agent` | `./agents/greeter` (python 3.11-slim) | –              | `CORAL_BROKER_URL`                |
| `planner-agent` | `./agents/planner`                    | –              | `CORAL_BROKER_URL`, service URLs  |
| `gmail-agent`   | `./agents/gmail`                      | 9201           | `MCP_URL`                         |
| `gcal-agent`    | `./agents/gcal`                       | 9202           | `MCP_URL`                         |
| `gtask-agent`   | `./agents/gtask`                      | 9203           | `MCP_URL`                         |
| `gmail-mcp`     | `./stubs/gmail-mcp`                   | 9101           | –                                 |
| `gcal-mcp`      | `./stubs/gcal-mcp`                    | 9102           | –                                 |
| `red-mcp`       | `./stubs/red-mcp`                     | 9103           | –                                 |
| `voice-worker`  | `./voice_worker`                      | 8000 (/health) | `CORAL_BROKER_URL`, `LIVEKIT_URL` |

---

## 3 · Message Contracts

### 3.1 `IntentDetected`

```json
{
  "agent": "GreeterA",
  "timestamp": "ISO-8601",
  "intent": "archive | draft | schedule | todo | query",
  "raw": "user utterance text"
}
```

### 3.2 `Task.*` (planner ⇒ service agents)

```json
{
  "taskId": "stub-{uuid4}",
  "task": "archive | draft | create_event | list_today | create_todo",
  "payload": { "ts": "...", "meta": "..." }
}
```

### 3.3 `TaskCompleted`

```json
{
  "taskId": "stub-{uuid4}",
  "status": "ok",
  "result_digest": "(stub) mail done"
}
```

---

## 4 · HTTP Stub API

| Endpoint                       | Payload                                  | Response                                          |
| ------------------------------ | ---------------------------------------- | ------------------------------------------------- |
| `POST /invoke` (all MCP stubs) | `{ "task": "<type>", "payload": {...} }` | `{ "status":"ok", "result_digest":"(stub) ..." }` |

Latency target: ≤ 300 ms.

---

## 5 · Deployment Steps

1. `git clone … && cd infra-phase0`
2. `docker compose build && docker compose up -d`
3. Confirm:

   - Studio on `:7000` shows five green agents.
   - `/health` on `:8000` returns _200 ok_.
   - `curl localhost:9101/invoke -d '{"task":"archive"}'` echoes JSON.

---

## 6 · Definition of Done

| Criterion                         | Tool / Command                             |
| --------------------------------- | ------------------------------------------ |
| Voice echo ≤ 1.5 s                | Stopwatch on LiveKit room                  |
| Planner routes to correct service | Observe edge colours in Studio             |
| All stubs respond 200             | cURL each `/invoke`                        |
| Security                          | `nmap` externally shows only allowed ports |
| Tag `v0.1.0` pushed               | `git tag v0.1.0 && git push --tags`        |

---

## 7 · Future-Phase Hooks

- Replace each MCP stub with real Google integrations (Phase 1).
- Enable `$CORAL` micro-payments in service-agent replies (Phase 2).
- Swap regex Greeter for Llama-3 JSON classifier (Phase 2).

---

_End of TRD_

```

---

**How to use**

1. Copy each fenced block into its own file (`PRD.md`, `TRD.md`).
2. Commit to your `phase0` branch.
3. Update revision/date headers whenever specs evolve.
```
