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


@app.get("/api_info")
async def root():
    """API information page."""
    return {
        "name": "Incident Response Environment",
        "description": "On-call incident response RL environment for training AI agents",
        "endpoints": {
            "POST /reset": "Reset environment (accepts task_name parameter)",
            "POST /step": "Execute an action (accepts IncidentAction)",
            "GET /state": "Get current environment state",
            "GET /schema": "Get action/observation JSON schemas",
            "GET /tasks": "List available tasks",
            "WS /ws": "WebSocket endpoint for persistent sessions",
        },
        "tasks": get_available_tasks(),
    }


@app.get("/")
async def index():
    """Root endpoint with environment metadata."""
    return await root()


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


@app.get("/health")
async def health():
    """Compatibility health endpoint used by container healthcheck."""
    return await healthz()


def main():
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
