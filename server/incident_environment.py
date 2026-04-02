"""Incident Response MCP Environment."""

import json
from typing import Any, Optional
from uuid import uuid4

from fastmcp import FastMCP

try:
    from openenv.core.env_server.mcp_environment import MCPEnvironment
    from openenv.core.env_server.types import Action, Observation, State
    from openenv.core.env_server.mcp_types import CallToolAction, CallToolObservation
except ImportError:
    from openenv.core.env_server.mcp_environment import MCPEnvironment
    from openenv.core.env_server.types import Action, Observation, State
    from openenv.core.env_server.mcp_types import CallToolAction, CallToolObservation

from .graders import (
    EpisodeHistory,
    check_remedy,
    check_root_cause,
    grade_episode,
    get_grade_breakdown,
)
from .scenarios import Scenario, get_scenario, list_tasks


class IncidentEnvironment(MCPEnvironment):
    """On-call incident response environment with 3 difficulty levels."""

    VALID_ACTIONS = [
        "query_logs", "check_metrics", "read_runbook",
        "identify_root_cause", "execute_remedy", "escalate",
        "get_status",
    ]

    DESTRUCTIVE_ACTIONS = {
        "drop_database", "delete_data", "format_disk",
        "shutdown_service", "terminate_all",
    }

    def __init__(self):
        mcp = FastMCP("incident_env")
        env = self

        @mcp.tool
        def query_logs(service: str, filter: str = "") -> str:
            """Query logs for a service. Use filter to search for specific terms."""
            return env._handle_query_logs(service, filter)

        @mcp.tool
        def check_metrics(service: str) -> str:
            """Check current metrics (CPU, memory, error rate, latency) for a service."""
            return env._handle_check_metrics(service)

        @mcp.tool
        def read_runbook(service: str) -> str:
            """Read the operational runbook with troubleshooting procedures."""
            return env._handle_read_runbook(service)

        @mcp.tool
        def identify_root_cause(cause: str) -> str:
            """Declare the root cause of the incident."""
            return env._handle_identify_root_cause(cause)

        @mcp.tool
        def execute_remedy(service: str, remedy: str) -> str:
            """Execute a remediation action on a service."""
            return env._handle_execute_remedy(service, remedy)

        @mcp.tool
        def escalate(reason: str) -> str:
            """Escalate the incident to senior on-call (reduces score)."""
            return env._handle_escalate(reason)

        @mcp.tool
        def get_status() -> str:
            """Get current investigation status summary."""
            return env._handle_get_status()

        super().__init__(mcp)
        self._scenario: Optional[Scenario] = None
        self._history: Optional[EpisodeHistory] = None
        self._findings: list = []
        self._done: bool = False
        self._step_count: int = 0
        self._time_elapsed: float = 0.0
        self._prev_clue_count: int = 0
        self._prev_root_cause_state: bool = False
        self._prev_wrong_remedies: int = 0
        self._prev_destructive: int = 0
        self._prev_escalations: int = 0
        self._state = State(episode_id=str(uuid4()), step_count=0)

    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> Observation:
        task_name = kwargs.get("task_name", "easy_config_error")

        self._scenario = get_scenario(task_name, seed=seed or 42)
        self._history = EpisodeHistory()
        self._findings = []
        self._done = False
        self._step_count = 0
        self._time_elapsed = 0.0
        self._prev_clue_count = 0
        self._prev_root_cause_state = False
        self._prev_wrong_remedies = 0
        self._prev_destructive = 0
        self._prev_escalations = 0

        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )

        return Observation(
            done=False,
            reward=0.0,
            metadata={},
        )

    # -- Tool handlers --

    def _handle_query_logs(self, service: str, filter_text: str = "") -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        service_lower = service.lower().strip()
        service_info = self._scenario.services.get(service_lower)

        if not service_info:
            for name, info in self._scenario.services.items():
                if service_lower in name or name in service_lower:
                    service_info = info
                    break

        if not service_info:
            available = ", ".join(self._scenario.services.keys())
            return f"Error: Unknown service '{service}'. Available: {available}"

        self._history.services_queried_logs.add(service_info.name)

        logs = service_info.log_lines
        if filter_text:
            logs = [line for line in logs if filter_text.lower() in line.lower()]

        if not logs:
            return f"No log entries found for {service_info.name}" + (
                f" matching filter '{filter_text}'" if filter_text else ""
            )

        if service_info.is_relevant and service_info.name not in self._history.services_queried_logs - {service_info.name}:
            self._history.relevant_clues_found = min(
                self._history.relevant_clues_found + 1,
                self._scenario.total_clues,
            )

        result = f"=== Logs for {service_info.name} ===\n" + "\n".join(logs)
        self._findings.append(f"Queried logs for {service_info.name}")
        return result

    def _handle_check_metrics(self, service: str) -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        service_lower = service.lower().strip()
        service_info = self._scenario.services.get(service_lower)

        if not service_info:
            for name, info in self._scenario.services.items():
                if service_lower in name or name in service_lower:
                    service_info = info
                    break

        if not service_info:
            available = ", ".join(self._scenario.services.keys())
            return f"Error: Unknown service '{service}'. Available: {available}"

        self._history.services_queried_metrics.add(service_info.name)

        if service_info.is_relevant:
            self._history.relevant_clues_found = min(
                self._history.relevant_clues_found + 1,
                self._scenario.total_clues,
            )

        result = f"=== Metrics for {service_info.name} ===\n{json.dumps(service_info.metrics, indent=2)}"
        self._findings.append(f"Checked metrics for {service_info.name}")
        return result

    def _handle_read_runbook(self, service: str) -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        service_lower = service.lower().strip()
        service_info = self._scenario.services.get(service_lower)

        if not service_info:
            for name, info in self._scenario.services.items():
                if service_lower in name or name in service_lower:
                    service_info = info
                    break

        if not service_info:
            available = ", ".join(self._scenario.services.keys())
            return f"Error: Unknown service '{service}'. Available: {available}"

        self._history.services_queried_runbook.add(service_info.name)

        if service_info.is_relevant:
            self._history.relevant_clues_found = min(
                self._history.relevant_clues_found + 1,
                self._scenario.total_clues,
            )

        if not service_info.runbook_entry:
            return f"No runbook entry found for {service_info.name}"

        self._findings.append(f"Read runbook for {service_info.name}")
        return service_info.runbook_entry

    def _handle_identify_root_cause(self, cause: str) -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        self._history.root_cause_declared = cause
        exact, partial = check_root_cause(cause, self._scenario)
        self._history.root_cause_correct = exact
        self._history.root_cause_partial = partial

        if exact:
            return "✅ Root cause correctly identified! Now apply the appropriate remedy."
        elif partial:
            return "⚠️ You're on the right track, but not complete. Gather more evidence."
        else:
            return "❌ Incorrect root cause. Continue investigating logs, metrics, and runbooks."

    def _handle_execute_remedy(self, service: str, remedy: str) -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        attempt = {"service": service.lower().strip(), "remedy": remedy.lower().strip()}
        self._history.remedies_attempted.append(attempt)

        if remedy.lower().strip() in self.DESTRUCTIVE_ACTIONS:
            self._history.destructive_actions += 1
            return f"⛔ DESTRUCTIVE ACTION BLOCKED: '{remedy}' on {service}. Penalty applied."

        is_correct = check_remedy([attempt], self._scenario)
        if is_correct:
            self._history.remedy_correct = True
            self._done = True
            return f"✅ Remedy '{remedy}' applied to {service}. Incident resolved!"
        else:
            self._history.wrong_remedies += 1
            return f"❌ Remedy '{remedy}' on {service} failed. Check the runbook for the correct procedure."

    def _handle_escalate(self, reason: str) -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        self._history.unnecessary_escalations += 1
        self._done = True
        return f"📞 Escalated to senior on-call. Reason: {reason}. Resolving without escalation earns higher scores."

    def _handle_get_status(self) -> str:
        if not self._scenario:
            return "Error: Environment not initialized. Call reset() first."

        status = {
            "alert": self._scenario.alert_summary,
            "severity": self._scenario.severity,
            "time_elapsed_minutes": self._time_elapsed,
            "steps_used": self._step_count,
            "max_steps": self._scenario.max_steps,
            "steps_remaining": self._scenario.max_steps - self._step_count,
            "findings_count": len(self._findings),
            "recent_findings": self._findings[-5:] if self._findings else [],
            "root_cause_declared": self._history.root_cause_declared is not None,
            "incident_resolved": self._history.remedy_correct,
            "available_services": list(self._scenario.services.keys()),
        }
        return json.dumps(status, indent=2)

    # -- Incremental reward --

    def _compute_step_reward(self) -> float:
        """Per-step shaping reward."""
        if not self._history:
            return 0.0

        reward = 0.0

        new_clues = self._history.relevant_clues_found - self._prev_clue_count
        if new_clues > 0:
            reward += 0.02 * new_clues
            self._prev_clue_count = self._history.relevant_clues_found

        if self._history.root_cause_correct and not self._prev_root_cause_state:
            reward += 0.05
            self._prev_root_cause_state = True

        new_wrong = self._history.wrong_remedies - self._prev_wrong_remedies
        if new_wrong > 0:
            reward -= 0.03 * new_wrong
            self._prev_wrong_remedies = self._history.wrong_remedies

        new_destructive = self._history.destructive_actions - self._prev_destructive
        if new_destructive > 0:
            reward -= 0.05 * new_destructive
            self._prev_destructive = self._history.destructive_actions

        new_escalations = self._history.unnecessary_escalations - self._prev_escalations
        if new_escalations > 0:
            reward -= 0.02 * new_escalations
            self._prev_escalations = self._history.unnecessary_escalations

        return round(reward, 4)

    # -- Step: let base class handle MCP, then enrich with reward/done --

    def _step_impl(self, action: Action, timeout_s: Optional[float] = None, **kwargs: Any) -> Observation:
        return Observation(
            done=False, reward=0.0,
            metadata={"error": f"Unknown action type: {type(action).__name__}. Use MCP tools."},
        )

    def _enrich_observation(self, obs: Any) -> Any:
        """Add reward and done to observation returned by base MCPEnvironment."""
        self._step_count += 1
        self._state.step_count = self._step_count
        self._time_elapsed += 2.0

        if self._history:
            self._history.steps_used = self._step_count

        if self._scenario and self._history:
            is_done = self._done or self._step_count >= self._scenario.max_steps
            reward = grade_episode(self._scenario, self._history) if is_done else self._compute_step_reward()

            # Mutate the observation's reward and done in-place
            # CallToolObservation inherits from Observation which has these fields
            try:
                obs.reward = reward
                obs.done = is_done
            except (AttributeError, TypeError):
                pass

        return obs

    def step(self, action: Action, timeout_s: Optional[float] = None, **kwargs: Any) -> Observation:
        # Let the base MCPEnvironment handle the tool call natively
        # This returns CallToolObservation with tool_name + result (containing text)
        obs = super().step(action, timeout_s=timeout_s, **kwargs)
        return self._enrich_observation(obs)

    async def step_async(self, action: Action, timeout_s: Optional[float] = None, **kwargs: Any) -> Observation:
        obs = await super().step_async(action, timeout_s=timeout_s, **kwargs)
        return self._enrich_observation(obs)

    @property
    def state(self) -> State:
        return self._state
