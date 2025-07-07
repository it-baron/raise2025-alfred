# Coordinator Agent Specification

## Overview

The Coordinator Agent is a central orchestration service that implements the Agent2Agent (A2A) protocol to enable seamless communication and collaboration between AI agents in the Alfred voice assistant ecosystem. It acts as a registry, router, and task manager for distributed agent services.

## Architecture

### Core Components

1. **Agent Registry**: Maintains a catalog of available agents and their capabilities
2. **Task Manager**: Handles task lifecycle management and routing
3. **FastAPI Server**: Provides HTTP endpoints for client communication
4. **Docker Monitor**: Automatically discovers and registers containerized agents
5. **Streaming Engine**: Manages real-time response streaming using Server-Sent Events (SSE)

### Key Responsibilities

- **Agent Discovery**: Automatically detects and registers agents running in Docker containers
- **Capability Matching**: Routes incoming requests to agents with appropriate skills
- **Task Orchestration**: Manages the complete lifecycle of tasks from creation to completion
- **Real-time Communication**: Streams execution progress back to clients
- **Protocol Compliance**: Ensures all interactions follow the A2A v0.2.5 specification

## Agent Discovery Mechanism

### Docker-based Discovery

The coordinator continuously monitors Docker containers for agents:

1. **Container Detection**: Listens for containers with the label `agent=true`
2. **Agent Card Retrieval**: Fetches the Agent Card from `/.well-known/agent.json` endpoint
3. **Registry Update**: Adds discovered agents to the internal catalog

### Agent Card Structure

Following the A2A protocol, each agent must expose an Agent Card containing:

```json
{
  "name": "agent-name",
  "description": "Agent description",
  "provider": {
    "name": "Alfred System",
    "url": "https://alfred.example.com"
  },
  "url": "http://agent-service:port",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "authentication": {
    "schemes": ["Bearer", "ApiKey"]
  },
  "skills": [
    {
      "id": "skill-1",
      "name": "Email Management",
      "description": "Archive emails and create drafts",
      "inputModes": ["text"],
      "outputModes": ["text"],
      "examples": ["Archive promotional emails", "Draft reply to John"]
    }
  ]
}
```

## API Endpoints

### Message Endpoint

**POST** `/send-message`

Receives client messages and returns an async stream of execution chunks.

Request Body:

```json
{
  "role": "user",
  "parts": [
    {
      "kind": "text",
      "text": "Archive all promotional emails"
    }
  ],
  "messageId": "msg-123",
  "contextId": "ctx-abc", // Optional, for continuing conversations
  "sessionId": "session-456", // Optional, for implicit context continuation
  "referenceTaskIds": ["task-789"] // Optional, reference to previous tasks
}
```

Response Headers:

```
Content-Type: text/event-stream
X-Context-Id: ctx-abc123
X-Topic: Email Management
```

Response: SSE stream of task updates with contextId included

### Context Management Endpoints

**GET** `/contexts/{contextId}`

Retrieves full context information including conversation history.

Response:

```json
{
  "contextId": "ctx-abc123",
  "topic": "Email Management",
  "state": "active",
  "conversationHistory": [...],
  "relatedTasks": [...],
  "metadata": {...}
}
```

**POST** `/contexts/find`

Finds relevant context based on message content or session.

Request Body:

```json
{
  "message": "What about those emails we discussed?",
  "sessionId": "session-456",
  "userId": "user-123"
}
```

Response:

```json
{
  "contextId": "ctx-abc123",
  "confidence": 0.95,
  "topic": "Email Management"
}
```

### Health Check

**GET** `/health`

Returns the coordinator's health status and registered agent count.

## Task Routing Logic

### Context Resolution Flow

1. **Context Check**: Determine if message continues existing conversation

   - If contextId provided: Validate and load existing context
   - If no contextId: Check for implicit continuation via session/topic matching
   - If new conversation: Generate new contextId and detect topic

2. **Topic Detection**: Analyze message content to identify conversation topic

   - NLP-based topic classification
   - Entity extraction for context enrichment
   - Topic similarity scoring for continuation detection

3. **Context Creation/Update**:
   ```json
   {
     "contextId": "ctx-{uuid}",
     "topic": "Detected Topic",
     "topicConfidence": 0.85,
     "entities": ["email", "promotional", "archive"],
     "intent": "email_management"
   }
   ```

### Skill Matching Algorithm

1. **Intent Extraction**: Analyzes incoming message to identify required skills
2. **Context-Aware Selection**: Considers conversation history when matching agents
3. **Agent Selection**: Queries registry for agents with matching capabilities
4. **Availability Check**: Selects first available agent with required skill
5. **Fallback Strategy**: Returns appropriate error if no matching agent found

### Task Creation

When a suitable agent is found:

1. **Task Object Creation**:

   ```json
   {
     "id": "task-{uuid}",
     "contextId": "ctx-{uuid}",
     "status": {
       "state": "submitted"
     },
     "assignedAgent": "agent-name",
     "createdAt": "ISO-8601-timestamp"
   }
   ```

2. **Message Forwarding**: Sends task to selected agent via A2A protocol

## Streaming Response Architecture

### Server-Sent Events (SSE) Implementation

The coordinator implements real-time streaming as per A2A specification:

1. **Connection Setup**: Returns `Content-Type: text/event-stream`
2. **Event Format**: Each SSE event contains JSON-RPC 2.0 response
3. **Event Types**:
   - `Task`: Initial task creation notification
   - `TaskStatusUpdateEvent`: Status changes and progress updates
   - `TaskArtifactUpdateEvent`: Incremental result delivery

### Stream Event Structure

```
event: context-created
data: {
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "kind": "contextUpdate",
    "contextId": "ctx-abc123",
    "topic": "Email Management",
    "isNew": true
  }
}

event: task-update
data: {
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "kind": "taskStatusUpdate",
    "taskId": "task-123",
    "contextId": "ctx-abc123",
    "state": "working",
    "message": "Processing email archive request...",
    "progress": 0.3,
    "final": false
  }
}

event: task-update
data: {
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "kind": "taskStatusUpdate",
    "taskId": "task-123",
    "contextId": "ctx-abc123",
    "state": "completed",
    "message": "Archived 15 promotional emails",
    "final": true,
    "suggestedFollowUp": "Would you like me to draft replies to urgent emails?"
  }
}
```

## Task Lifecycle Management

### Task States

Following A2A protocol, tasks progress through these states:

1. **submitted**: Initial state when task is created
2. **working**: Agent is actively processing the task
3. **input-required**: Agent needs additional information
4. **auth-required**: Authentication needed for external service
5. **completed**: Task finished successfully
6. **failed**: Task encountered an error
7. **cancelled**: Task was cancelled by client
8. **rejected**: Agent declined to process the task

### State Transition Rules

- Tasks can only move forward in the lifecycle
- Terminal states: `completed`, `failed`, `cancelled`, `rejected`
- Interrupted states: `input-required`, `auth-required`
- Tasks in terminal states cannot be restarted

## Context Management

### Context Persistence

The coordinator maintains context across multiple tasks and conversations:

- **contextId**: Unique identifier that groups related tasks, messages, and conversation topics
- **Context Storage**: Persistent storage with in-memory caching for fast retrieval
- **Context Sharing**: Passes context between agents for continuity
- **Context Expiration**: Configurable TTL for inactive contexts

### Conversation Topic Management

The coordinator tracks and manages conversation topics:

1. **Topic Detection**: Automatically identifies conversation topics from message content
2. **Topic Continuity**: Links related messages under the same contextId
3. **Topic Switching**: Detects topic changes and creates new contexts when appropriate
4. **Topic History**: Maintains conversation history for context-aware responses

### Context Lifecycle

```json
{
  "contextId": "ctx-abc123",
  "topic": "Email Management",
  "createdAt": "2025-01-05T10:00:00Z",
  "lastActiveAt": "2025-01-05T10:15:00Z",
  "state": "active",
  "metadata": {
    "userId": "user-123",
    "sessionId": "session-456",
    "tags": ["email", "archive", "urgent"]
  },
  "conversationHistory": [
    {
      "messageId": "msg-001",
      "role": "user",
      "content": "Archive all promotional emails",
      "timestamp": "2025-01-05T10:00:00Z"
    },
    {
      "messageId": "msg-002",
      "role": "agent",
      "content": "Archived 15 promotional emails",
      "timestamp": "2025-01-05T10:00:30Z"
    }
  ],
  "relatedTasks": ["task-123", "task-456"]
}
```

### Context Continuation Strategies

1. **Explicit Continuation**: Client provides contextId in request
2. **Implicit Continuation**: Coordinator infers context from:
   - User session
   - Topic similarity
   - Temporal proximity
   - Referenced entities

### Multi-Task Workflows

Supports complex workflows through:

1. **Task Dependencies**: Tracks relationships between tasks within a context
2. **Parallel Execution**: Routes independent tasks simultaneously
3. **Sequential Processing**: Ensures dependent tasks wait for prerequisites
4. **Context-Aware Routing**: Considers conversation history when selecting agents

## Error Handling

### Agent Communication Failures

- **Retry Logic**: Implements exponential backoff for transient failures
- **Circuit Breaker**: Temporarily removes failing agents from registry
- **Fallback Agents**: Routes to alternative agents when primary fails

### Client Disconnection

- **Stream Cleanup**: Properly closes SSE connections
- **Task Persistence**: Maintains task state for reconnection
- **Resubscription Support**: Allows clients to resume interrupted streams

## Security Considerations

### Authentication

- **Client Authentication**: Validates Bearer tokens or API keys
- **Agent Authentication**: Verifies agent identity during registration
- **Token Propagation**: Passes client credentials to downstream agents

### Authorization

- **Skill-based Access**: Restricts agent access based on client permissions
- **Rate Limiting**: Prevents abuse through request throttling
- **Audit Logging**: Tracks all task assignments and completions

## Configuration

### Environment Variables

```bash
# Coordinator settings
COORDINATOR_PORT=8080
COORDINATOR_HOST=0.0.0.0

# Docker settings
DOCKER_SOCKET=/var/run/docker.sock
AGENT_LABEL_KEY=agent
AGENT_LABEL_VALUE=true

# A2A settings
A2A_VERSION=0.2.5
AGENT_CARD_PATH=/.well-known/agent.json

# Context management settings
CONTEXT_TTL_SECONDS=3600
CONTEXT_STORAGE_BACKEND=redis
CONTEXT_SIMILARITY_THRESHOLD=0.75
MAX_CONTEXT_HISTORY_SIZE=100
ENABLE_TOPIC_DETECTION=true
TOPIC_CLASSIFIER_MODEL=bert-base-uncased

# Streaming settings
SSE_KEEPALIVE_INTERVAL=30
MAX_CONCURRENT_STREAMS=1000

# Security settings
AUTH_ENABLED=true
JWT_SECRET=your-secret-key
API_KEY_HEADER=X-API-Key
```

## Deployment

### Docker Compose Integration

```yaml
services:
  coordinator:
    build: ./agents/coordinator
    ports:
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - DOCKER_SOCKET=/var/run/docker.sock
    depends_on:
      - redis # For distributed state
    networks:
      - alfred-network
```

### Scaling Considerations

- **Horizontal Scaling**: Multiple coordinator instances with shared state
- **Load Balancing**: Distribute client connections across instances
- **State Management**: Use Redis/etcd for distributed registry

## Monitoring and Observability

### Metrics

- **Agent Health**: Track agent availability and response times
- **Task Metrics**: Monitor task completion rates and durations
- **Stream Metrics**: Count active connections and data throughput

### Logging

- **Structured Logging**: JSON format for easy parsing
- **Correlation IDs**: Track requests across agent boundaries
- **Debug Mode**: Verbose logging for troubleshooting

## Future Enhancements

### Planned Features

1. **Push Notifications**: Webhook support for long-running tasks
2. **Agent Capabilities Negotiation**: Dynamic skill adaptation
3. **Multi-Modal Support**: Audio/video streaming capabilities
4. **Advanced Routing**: ML-based agent selection
5. **Task Prioritization**: Queue management for resource optimization

### Protocol Extensions

- **Custom A2A Extensions**: Domain-specific protocol additions
- **Version Negotiation**: Support multiple A2A protocol versions
- **Federation**: Connect to external coordinator networks

## References

- [A2A Protocol Specification v0.2.5](https://a2aproject.github.io/A2A/v0.2.5/)
- [Agent Discovery in A2A](https://a2aproject.github.io/A2A/v0.2.5/topics/agent-discovery/)
- [Life of a Task](https://a2aproject.github.io/A2A/v0.2.5/topics/life-of-a-task/)
- [Streaming & Async Operations](https://a2aproject.github.io/A2A/v0.2.5/topics/streaming-and-async/)

## Conversation Continuation Patterns

### Explicit Continuation

When clients provide a contextId:

```python
# Client request with explicit context
{
  "messageId": "msg-456",
  "contextId": "ctx-abc123",
  "parts": [{"kind": "text", "text": "What about the urgent ones?"}]
}

# Coordinator loads context and understands "urgent ones" refers to emails
```

### Implicit Continuation

When contextId is not provided:

1. **Session-based**: Match by sessionId within time window
2. **Topic-based**: Detect similar topic using NLP
3. **Entity-based**: Match mentioned entities to previous contexts
4. **Temporal**: Recent contexts from same user

### Context Switching

Coordinator detects topic changes:

```python
# Previous context: Email Management
User: "Archive promotional emails"
Context: ctx-abc123

# Topic switch detected
User: "Schedule a meeting with John tomorrow"
# New context created: ctx-def456 (Calendar Management)

# Reference to previous context
User: "After archiving those emails, remind me to check calendar"
# Links contexts: ctx-abc123 → ctx-def456
```

### Multi-Context Workflows

Support for complex scenarios:

```json
{
  "primaryContext": "ctx-abc123",
  "relatedContexts": [
    {
      "contextId": "ctx-def456",
      "relationship": "prerequisite",
      "topic": "Email Cleanup"
    },
    {
      "contextId": "ctx-ghi789",
      "relationship": "parallel",
      "topic": "Calendar Scheduling"
    }
  ]
}
```

## Implementation Plan

### Phase 1: Simple Coordinator (Current Focus)

**Goal**: Basic coordinator with Docker discovery and skill mapping

#### Core Endpoints

1. **Agent Card Endpoint**

   - `GET /.well-known/agent.json`
   - Exposes coordinator's own A2A agent card
   - Identifies coordinator as a routing/orchestration agent

2. **Skills Registry Endpoint**

   - `GET /skills`
   - Returns complete skill-to-agent mapping
   - Example response:

   ```json
   {
     "skills": {
       "archive_emails": {
         "agentName": "gmail-agent",
         "agentUrl": "http://gmail-agent:8001",
         "description": "Archive promotional emails"
       },
       "create_event": {
         "agentName": "gcal-agent",
         "agentUrl": "http://gcal-agent:8002",
         "description": "Create calendar events"
       }
     },
     "totalAgents": 2,
     "lastUpdated": "2025-01-05T10:30:00Z"
   }
   ```

3. **Message Endpoint**

   - `POST /send-message`
   - Simple message routing to appropriate agent
   - Returns synchronous response (no SSE yet)

4. **Health Check**
   - `GET /health`
   - Returns coordinator status and agent count

#### Docker Discovery

- Monitor containers with label `agent=true`
- Fetch agent card from `http://{container}:port/.well-known/agent.json`
- Update registry when containers start/stop

### Phase 2: Simple Test Agent

**Goal**: Create minimal Gmail agent for testing

- Expose `/.well-known/agent.json` with one skill
- Implement `/message/send` endpoint (A2A RPC)
- Return stubbed responses
- Docker container with `agent=true` label

### Phase 3: Console Test Application

**Goal**: Validate coordinator functionality

- Python script to send test messages
- Test skill discovery via `/skills`
- Test message routing
- Verify agent registration

### Phase 4: Migration Path

Once basic functionality is proven:

- [ ] Add SSE streaming support
- [ ] Implement context management
- [ ] Add conversation continuation
- [ ] Migrate remaining agents
- [ ] Remove Coral Protocol dependencies
- [ ] Production hardening

## Implementation Status

**Current Phase**: Phase 1 - Simple Coordinator

- [ ] Basic FastAPI server
- [ ] Docker container monitoring
- [ ] Agent registry (in-memory)
- [ ] `/.well-known/agent.json` endpoint
- [ ] `/skills` endpoint
- [ ] `/send-message` endpoint
- [ ] `/health` endpoint
- [ ] Docker-based agent discovery
- [ ] Skill extraction from agent cards
- [ ] Basic message routing

**Next Steps**:

1. Implement minimal coordinator with above endpoints
2. Create simple Gmail test agent
3. Build console test app
4. Validate Docker discovery works
5. Test message routing
