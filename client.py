"""Client for connecting to the Incident Response Environment."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

try:
    from .models import IncidentAction, IncidentObservation, IncidentState
except ImportError:
    from models import IncidentAction, IncidentObservation, IncidentState


class IncidentEnv(
    EnvClient[IncidentAction, IncidentObservation, IncidentState]
):
    """
    Client for the Incident Response Environment.

    Maintains a persistent WebSocket connection to the environment server.

    Example:
        >>> with IncidentEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset(task_name="easy_config_error")
        ...     print(result.observation.alert_summary)
        ...
        ...     result = client.step(IncidentAction(
        ...         action_type="query_logs",
        ...         target="payment-service",
        ...         parameters={"filter": "error"}
        ...     ))
        ...     print(result.observation.last_action_result)
    """

    def _step_payload(self, action: IncidentAction) -> Dict:
        """Convert IncidentAction to JSON payload for step message."""
        return {
            "action_type": action.action_type,
            "target": action.target or "",
            "parameters": action.parameters or {},
        }

    def _parse_result(self, payload: Dict) -> StepResult[IncidentObservation]:
        """Parse server response into StepResult[IncidentObservation]."""
        obs_data = payload.get("observation", {})
        observation = IncidentObservation(
            alert_summary=obs_data.get("alert_summary", ""),
            severity=obs_data.get("severity", "P3"),
            task_description=obs_data.get("task_description", ""),
            current_findings=obs_data.get("current_findings", []),
            available_services=obs_data.get("available_services", []),
            available_actions=obs_data.get("available_actions", []),
            last_action_result=obs_data.get("last_action_result", ""),
            last_action_error=obs_data.get("last_action_error", False),
            time_elapsed_minutes=obs_data.get("time_elapsed_minutes", 0.0),
            step_number=obs_data.get("step_number", 0),
            max_steps=obs_data.get("max_steps", 15),
            done=payload.get("done", False),
            reward=payload.get("reward", 0.0),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> IncidentState:
        """Parse server response into IncidentState object."""
        return IncidentState(
            episode_id=payload.get("episode_id", ""),
            step_count=payload.get("step_count", 0),
            task_name=payload.get("task_name", ""),
            task_difficulty=payload.get("task_difficulty", ""),
            severity=payload.get("severity", "P3"),
            root_cause_identified=payload.get("root_cause_identified", False),
            incident_resolved=payload.get("incident_resolved", False),
            cum_reward=payload.get("cum_reward", 0.0),
            relevant_clues_found=payload.get("relevant_clues_found", 0),
            total_clues_available=payload.get("total_clues_available", 0),
            steps_used=payload.get("steps_used", 0),
            wrong_actions_taken=payload.get("wrong_actions_taken", 0),
        )
