"""FastAPI server for the Incident Response Environment."""

try:
    from openenv.core.env_server.http_server import create_app
    from openenv.core.env_server.mcp_types import CallToolAction, CallToolObservation
    from .incident_environment import IncidentEnvironment
    from .scenarios import list_tasks as get_available_tasks
except ImportError:
    from openenv.core.env_server.http_server import create_app
    from openenv.core.env_server.mcp_types import CallToolAction, CallToolObservation
    from server.incident_environment import IncidentEnvironment
    from server.scenarios import list_tasks as get_available_tasks

app = create_app(
    IncidentEnvironment,
    CallToolAction,
    CallToolObservation,
    env_name="incident_env",
)


@app.get("/tasks")
async def tasks():
    """Return available task names for this environment."""
    return {"tasks": get_available_tasks()}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
