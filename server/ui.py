import json
import uuid
from typing import Dict, Any

import gradio as gr
from .incident_environment import IncidentEnvironment
from .scenarios import list_tasks

try:
    from ..models import IncidentAction
except ImportError:
    from models import IncidentAction

# Maintain state independently per session
sessions: Dict[str, IncidentEnvironment] = {}


def get_env(session_id: str) -> IncidentEnvironment:
    if session_id not in sessions:
        sessions[session_id] = IncidentEnvironment()
    return sessions[session_id]


def reset_env(session_id: str, task_name: str):
    env = get_env(session_id)
    try:
        obs = env.reset(task_name=task_name)
    except Exception as e:
        return f"🚨 Error resetting: {str(e)}", "", f"Score: 0.00 | Steps: 0", "Ready"

    alert_text = (
        f"**Severity:** {obs.severity}  \n"
        f"**Alert:** {obs.alert_summary}  \n"
        f"**Affected Services:** {', '.join(obs.available_services) if obs.available_services else 'Unknown'}  \n"
        f"**Available Actions:** {', '.join(obs.available_actions) if obs.available_actions else 'Unknown'}  \n"
        f"**Goal:** {obs.task_description}"
    )

    score_text = f"🎯 Score: {obs.reward:.2f} | 👟 Steps: {obs.step_number}/{obs.max_steps}"
    return alert_text, "Environment Reset. Awaiting your first command. Console ready.", score_text, f"{task_name} Started"


def step_env(session_id: str, action_type: str, target: str, params_str: str, current_console: str):
    env = get_env(session_id)

    # Parse params
    params = {}
    if params_str.strip():
        try:
            params = json.loads(params_str)
        except json.JSONDecodeError:
            error_msg = f"❌ Invalid JSON in parameters: {params_str}\n\n" + current_console
            return error_msg, f"🎯 Score: {env.state.cum_reward:.2f} | 👟 Steps: {env.state.steps_used}/{env._scenario.max_steps}", "Error"

    action = IncidentAction(action_type=action_type, target=target, parameters=params)
    
    try:
        obs = env.step(action)
    except Exception as e:
        error_msg = f"❌ Environment Error: {str(e)}\n\n" + current_console
        return error_msg, "Error", "Error"

    # Formatting output for the beautiful console
    new_result = ""
    new_result += f"**> {action_type}** {target} {params if params else ''}\n"
    new_result += "-" * 50 + "\n"
    new_result += str(obs.last_action_result) + "\n"
    new_result += "=" * 50 + "\n\n"

    updated_console = new_result + current_console

    score_text = f"🎯 Score: {obs.reward:.2f} | 👟 Steps: {obs.step_number}/{obs.max_steps}"
    
    status_text = "Incident Resolved ✅" if obs.done and obs.reward > 0.8 else "Investigating 🔍"
    if obs.done and obs.reward <= 0.8:
        status_text = "Episode Ended 🛑"

    return updated_console, score_text, status_text


css = """
.console-box textarea {
    font-family: 'Courier New', Courier, monospace !important;
    background-color: #1e1e1e !important;
    color: #00ff00 !important;
    padding: 10px;
}
.alert-box {
    border-left: 4px solid #ff4d4f;
    padding: 10px;
    background-color: rgba(255, 77, 79, 0.1);
    margin-bottom: 15px;
}
"""

with gr.Blocks(theme=gr.themes.Monochrome(), css=css) as demo:
    session_id = gr.State(lambda: str(uuid.uuid4()))

    gr.Markdown("# 🚨 Incident Response Action Center", elem_classes=["header"])
    gr.Markdown("Play the role of the on-call engineer. Select an incident, investigate logs and metrics, identify the root cause, and execute the remedy.")

    with gr.Row():
        with gr.Column(scale=2):
            task_dropdown = gr.Dropdown(choices=list_tasks(), value=list_tasks()[0], label="Select Incident Scenario")
        with gr.Column(scale=1):
            reset_btn = gr.Button("🔔 Acknowledge & Start Investigation", variant="primary")

    alert_display = gr.Markdown("Please acknowledge an alert to begin...", elem_classes=["alert-box"])

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Scoreboard")
            score_display = gr.Markdown("🎯 Score: 0.00 | 👟 Steps: 0/0")
            status_display = gr.Markdown("Status: 🔴 Offline")

            gr.Markdown("### Action Control")
            action_dropdown = gr.Dropdown(
                choices=["query_logs", "check_metrics", "read_runbook", "identify_root_cause", "execute_remedy"],
                value="query_logs",
                label="Action"
            )
            target_input = gr.Textbox(label="Target Service (e.g. payment-service)")
            params_input = gr.Textbox(label="Parameters (JSON)", value='{"filter": "error"}', lines=3)
            
            step_btn = gr.Button("🚀 Execute Action")
            
        with gr.Column(scale=2):
            gr.Markdown("### Investigation Terminal")
            terminal_output = gr.Textbox(
                label="Console Output",
                lines=20,
                interactive=False,
                elem_classes=["console-box"],
                value="System online. Awaiting commands..."
            )

    # Wire up the events
    reset_btn.click(
        fn=reset_env,
        inputs=[session_id, task_dropdown],
        outputs=[alert_display, terminal_output, score_display, status_display]
    )

    step_btn.click(
        fn=step_env,
        inputs=[session_id, action_dropdown, target_input, params_input, terminal_output],
        outputs=[terminal_output, score_display, status_display]
    )
