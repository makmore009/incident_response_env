"""
Incident Response Environment — Train AI agents to investigate and resolve production incidents.

An OpenEnv environment where an AI agent acts as an on-call engineer.
The agent receives alerts, investigates logs/metrics/runbooks, identifies
root causes, and applies remediation actions.

Example:
    >>> from incident_env import IncidentEnv, IncidentAction
    >>>
    >>> with IncidentEnv(base_url="http://localhost:8000") as env:
    ...     result = env.reset(task_name="easy_config_error")
    ...     print(result.observation.alert_summary)
    ...
    ...     result = env.step(IncidentAction(
    ...         action_type="query_logs",
    ...         target="payment-service",
    ...         parameters={"filter": "error"}
    ...     ))
    ...     print(result.observation.last_action_result)
"""

from .client import IncidentEnv
from .models import IncidentAction, IncidentObservation, IncidentState

__all__ = ["IncidentEnv", "IncidentAction", "IncidentObservation", "IncidentState"]
