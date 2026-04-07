"""FastAPI server for the Incident Response Environment."""

import os

try:
    from openenv.core.env_server.http_server import create_app
    from ..models import IncidentAction, IncidentObservation
    from .incident_environment import IncidentEnvironment
    from .scenarios import list_tasks as get_available_tasks
except ImportError:
    from openenv.core.env_server.http_server import create_app
    from models import IncidentAction, IncidentObservation
    from server.incident_environment import IncidentEnvironment
    from server.scenarios import list_tasks as get_available_tasks

app = create_app(
    IncidentEnvironment,
    IncidentAction,
    IncidentObservation,
    env_name="incident_env",
    max_concurrent_envs=int(os.environ.get("MAX_ENVS", "4")),
)


@app.get("/tasks")
async def tasks():
    """Return available task names for this environment."""
    return {"tasks": get_available_tasks()}


@app.get("/healthz")
async def healthz():
    """Quick health check."""
    try:
        env = IncidentEnvironment()
        obs = env.reset()
        return {"status": "ok", "alert": obs.alert_summary}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
