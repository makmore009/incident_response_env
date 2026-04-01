"""
Incident Response Environment — Train AI agents to investigate and resolve production incidents.

An OpenEnv environment where an AI agent acts as an on-call engineer.
The agent receives alerts, investigates logs/metrics/runbooks, identifies
root causes, and applies remediation actions.

Example:
    >>> from incident_env import IncidentEnv
    >>>
    >>> with IncidentEnv(base_url="http://localhost:8000") as env:
    ...     env.reset(task_name="easy_config_error")
    ...     tools = env.list_tools()
    ...     result = env.call_tool("query_logs", service="payment-service")
    ...     print(result)
"""

from openenv.core.env_server.mcp_types import CallToolAction, ListToolsAction

from .client import IncidentEnv

__all__ = ["IncidentEnv", "CallToolAction", "ListToolsAction"]
