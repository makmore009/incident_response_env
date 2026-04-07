---
title: Incident Response Environment
emoji: 🚨
colorFrom: red
colorTo: blue
sdk: docker
app_port: 8000
tags:
  - openenv
  - reinforcement-learning
  - incident-response
---


An OpenEnv environment for training AI agents to investigate and resolve production incidents. The agent acts as an on-call engineer who receives alerts, queries logs and metrics, reads runbooks, identifies root causes, and applies remediation actions.

## Why This Environment?

Every tech company — from startups to Meta — runs on-call rotations. When production breaks, engineers must:
1. **Receive an alert** → understand the problem scope
2. **Investigate** → query logs, check metrics, read runbooks
3. **Identify root cause** → correlate signals across services
4. **Remediate** → apply the correct fix from operational procedures
5. **Verify** → confirm the incident is resolved

This is a **multi-step sequential decision problem** — perfect for training RL agents. Yet no RL environment existed for this critical real-world task.

## Tasks

| Task | Difficulty | Scenario | Max Steps |
|------|-----------|----------|-----------|
| `easy_config_error` | ⭐ Easy | Payment service returning 500s due to misconfigured API key | 10 |
| `medium_cascading_db` | ⭐⭐ Medium | Cascading failure from a long-running database query exhausting connection pools | 15 |
| `hard_intermittent_auth` | ⭐⭐⭐ Hard | Intermittent 401 errors caused by a race condition between JWT key rotation and token cache invalidation | 20 |

## Action Space

The agent interacts via 7 tools:

| Tool | Parameters | Description |
|------|-----------|-------------|
| `query_logs` | `service`, `filter` | Query log output for a service |
| `check_metrics` | `service` | Check CPU, memory, error rate, latency, etc. |
| `read_runbook` | `service` | Read operational procedures and known fixes |
| `identify_root_cause` | `cause` | Declare the root cause of the incident |
| `execute_remedy` | `service`, `remedy` | Apply a remediation action |
| `escalate` | `reason` | Escalate to senior on-call (penalty) |
| `get_status` | — | Get current investigation summary |

## Observation Space

After each action, the agent receives:
- **Alert summary**: The initial alert text
- **Severity**: P1 (critical), P2 (high), P3 (medium)
- **Current findings**: List of discoveries made so far
- **Available services**: Services that can be queried
- **Last action result**: Output of the previous tool call
- **Time elapsed**: Simulated minutes since alert fired
- **Step count**: Current step / max steps

## Reward Function

Scores are 0.0–1.0, composed of:

| Component | Max Score | Description |
|-----------|-----------|-------------|
| Root cause identification | 0.30 | Correct (0.30) or partial (0.10) |
| Correct remedy | 0.35 | Applied the right fix from the runbook |
| Efficiency | 0.15 | Fewer steps = higher score |
| Clue discovery | 0.20 | Proportion of relevant evidence found |
| **Penalties** | | |
| Wrong remedy | -0.15 | Per incorrect remedy attempt |
| Destructive action | -0.30 | Blocked dangerous operations |
| Unnecessary escalation | -0.10 | Should have resolved independently |

## Setup

### Prerequisites
- Python 3.10+
- `pip install openenv-core[core]`

### Local Development
```bash
cd incident_env

# Install dependencies
pip install -e .

# Start the server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# In another terminal, run the baseline agent
export HF_TOKEN=your_token
export MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
python inference.py
```

### Docker
```bash
docker build -t incident-env:latest -f server/Dockerfile .
docker run -p 8000:8000 incident-env:latest
```

## 🎮 Human Review & Interactive Testing

This repository includes a fully featured **Interactive Dashboard** (built natively on top of the API without disrupting automated grading). The dashboard allows human engineers to assume the role of an on-call responder.

**To test the UI:**
1. Navigate to the Hugging Face Space URL. The UI will automatically load by default.
2. Select an incident (e.g., `easy_config_error`) and click **"🔔 Acknowledge & Start Investigation"**.
3. Use the **Action Control** panel to investigate.
    - Example 1: Set Action to `query_logs`, target to `payment-service`, and params to `{"filter": "error"}`, then click **Execute Action**.
    - Example 2: Notice your score dynamically updates! Read the logs in the console to find the error.
    - Example 3: Set Action to `read_runbook` for `payment-service` (params empty) to find the solution.
4. Conclude the simulation by executing the correct `execute_remedy` action. The Grader rigorously enforces penalties for dangerous actions and rewards efficiency!

### HuggingFace Space
```bash
openenv push --repo-id makrand098/incident-env
```

## Baseline Scores

| Task | Baseline Score (max reward per step) |
|------|--------------------------------------|
| easy_config_error | 0.24 |
| medium_cascading_db | 0.09 |
| hard_intermittent_auth | 0.24 |

## Architecture

```
incident_env/
├── models.py              # Action, Observation, State Pydantic models
├── client.py              # Standard OpenEnv HTTP Client
├── inference.py           # Baseline LLM agent
├── openenv.yaml           # Environment manifest
├── pyproject.toml         # Dependencies
└── server/
    ├── app.py             # FastAPI server
    ├── incident_environment.py  # Core environment logic
    ├── scenarios.py       # 3 incident scenario definitions
    ├── graders.py         # Scoring logic (0.0–1.0)
    └── Dockerfile         # Container definition
```

## License

This project was created for the Meta x Scaler OpenEnv AI Hackathon 2026.
