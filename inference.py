"""Baseline inference script for the Incident Response Environment."""

import json
import os
import re
import sys
import textwrap
from typing import Dict, List, Optional

from openai import OpenAI

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.3-70B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
MAX_STEPS_PER_TASK = 20
TEMPERATURE = 0.1
MAX_TOKENS = 300
ENV_NAME = "incident_env"

TASKS = ["easy_config_error", "medium_cascading_db", "hard_intermittent_auth"]

TASK_CONTEXT = {
    "easy_config_error": {
        "services": ["payment-service", "api-gateway", "database"],
        "hint": "Start with payment-service — it's mentioned in the alert.",
    },
    "medium_cascading_db": {
        "services": ["api-gateway", "user-service", "order-service", "db-primary", "cache-redis"],
        "hint": "Multiple services are affected. Trace the dependency chain — check db-primary.",
    },
    "hard_intermittent_auth": {
        "services": ["auth-service", "token-cache", "key-rotation-service", "session-store", "api-gateway", "load-balancer", "user-db"],
        "hint": "Errors are intermittent. Check auth-service first, then correlate with key-rotation-service and token-cache.",
    },
}


def get_system_prompt(task_name: str) -> str:
    ctx = TASK_CONTEXT.get(task_name, {"services": [], "hint": ""})
    services_str = ", ".join(f"'{s}'" for s in ctx["services"])

    return textwrap.dedent(f"""\
        You are an expert on-call engineer responding to a production incident.

        AVAILABLE SERVICES: {services_str}
        IMPORTANT: You MUST use ONLY these exact service names when calling tools.

        AVAILABLE TOOLS (call exactly one per turn as JSON):
        1. query_logs(service, filter) — Check logs. Example: {{"tool":"query_logs","args":{{"service":"{ctx['services'][0]}","filter":"error"}}}}
        2. check_metrics(service) — Check metrics.
        3. read_runbook(service) — Read operational runbook with known fixes.
        4. identify_root_cause(cause) — Declare the root cause after gathering evidence.
        5. execute_remedy(service, remedy) — Apply a fix. Use the exact remedy name from the runbook.
        6. escalate(reason) — Escalate to senior on-call (LAST RESORT, reduces score).
        7. get_status() — Check investigation progress.

        STRATEGY:
        - {ctx['hint']}
        - Check logs first (with filter="error"), then metrics, then runbook
        - Read the runbook to find the specific remedy command
        - Identify root cause BEFORE applying remedy
        - Use the EXACT remedy name from the runbook

        RESPOND WITH EXACTLY ONE JSON OBJECT PER TURN. Nothing else.
        Format: {{"tool": "tool_name", "args": {{"param": "value"}}}}
    """)


def parse_tool_call(response_text: str) -> Optional[Dict]:
    """Extract a JSON tool call from LLM output."""
    json_pattern = re.compile(r'\{[^{}]*"tool"[^{}]*\}', re.DOTALL)
    matches = json_pattern.findall(response_text)

    for match in matches:
        try:
            parsed = json.loads(match)
            if "tool" in parsed:
                return parsed
        except json.JSONDecodeError:
            continue

    try:
        brace_count = 0
        start = response_text.find('{')
        if start >= 0:
            for i in range(start, len(response_text)):
                if response_text[i] == '{':
                    brace_count += 1
                elif response_text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        parsed = json.loads(response_text[start:i+1])
                        if "tool" in parsed:
                            return parsed
                        break
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def extract_tool_result(result) -> str:
    """Extract text content from an environment observation."""
    if result is None:
        return "No output"
    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        if 'content' in result:
            content = result['content']
            if isinstance(content, list):
                texts = []
                for item in content:
                    if isinstance(item, dict) and 'text' in item:
                        texts.append(item['text'])
                    elif hasattr(item, 'text'):
                        texts.append(item.text)
                    else:
                        texts.append(str(item))
                return "\n".join(texts) if texts else json.dumps(result)
            return str(content)
        if 'metadata' in result:
            meta = result['metadata']
            if isinstance(meta, dict) and 'tool_result' in meta:
                return meta['tool_result']
            return json.dumps(meta, indent=2)
        return json.dumps(result, indent=2)

    try:
        if hasattr(result, 'metadata') and result.metadata:
            meta = result.metadata
            if isinstance(meta, dict) and 'tool_result' in meta:
                return meta['tool_result']
            return json.dumps(meta, indent=2)
    except Exception:
        pass

    try:
        if hasattr(result, 'content'):
            contents = result.content
            if isinstance(contents, list):
                texts = [item.text if hasattr(item, 'text') else str(item) for item in contents]
                if texts:
                    return "\n".join(texts)
    except Exception:
        pass

    return str(result)


def format_action_str(tool_name: str, tool_args: Dict) -> str:
    args_parts = [f"'{v}'" if isinstance(v, str) else str(v) for v in tool_args.values()]
    return f"{tool_name}({','.join(args_parts)})"


def run_task(client: OpenAI, env, task_name: str) -> tuple:
    """Run a single task. Returns (success, steps, rewards_list)."""
    rewards: List[float] = []
    step_count = 0
    success = False

    print(f"[START] task={task_name} env={ENV_NAME} model={MODEL_NAME}")

    try:
        env.reset(task_name=task_name)
        env.list_tools()

        system_prompt = get_system_prompt(task_name)
        ctx = TASK_CONTEXT.get(task_name, {"services": [], "hint": ""})
        services_str = ", ".join(ctx["services"])

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    f"An incident alert has fired. Available services: {services_str}. "
                    f"Begin investigating. What is your first tool call?"
                ),
            },
        ]

        for step_idx in range(MAX_STEPS_PER_TASK):
            step_count = step_idx + 1
            action_str = "noop()"
            reward = 0.0
            done = False
            error_str = "null"

            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                llm_output = response.choices[0].message.content or ""

                tool_call = parse_tool_call(llm_output)
                if not tool_call:
                    action_str = "parse_error()"
                    error_str = "Could not parse tool call from LLM output"
                    messages.append({"role": "assistant", "content": llm_output})
                    messages.append({
                        "role": "user",
                        "content": (
                            'Respond with ONLY a JSON object. Example: '
                            f'{{"tool": "query_logs", "args": {{"service": "{ctx["services"][0]}", "filter": "error"}}}}'
                        ),
                    })
                    rewards.append(reward)
                    print(f"[STEP]  step={step_count} action={action_str} reward={reward:.2f} done=false error={error_str}")
                    continue

                tool_name = tool_call.get("tool", "noop")
                tool_args = tool_call.get("args", {})
                action_str = format_action_str(tool_name, tool_args)

                raw_result = env.call_tool(tool_name, **tool_args)
                result_str = extract_tool_result(raw_result)

                if hasattr(raw_result, 'reward'):
                    reward = raw_result.reward or 0.0
                elif isinstance(raw_result, dict) and 'reward' in raw_result:
                    reward = raw_result['reward'] or 0.0

                error_str = "null"

                if "✅" in result_str and "resolved" in result_str.lower():
                    done = True
                    success = True
                elif "📞" in result_str and "escalated" in result_str.lower():
                    done = True
                elif "⛔" in result_str or "DESTRUCTIVE" in result_str:
                    error_str = "destructive action blocked"
                elif "❌" in result_str and "remedy" in result_str.lower():
                    error_str = "incorrect remedy"

            except Exception as e:
                error_str = str(e).replace("\n", " ")[:200]

            rewards.append(reward)
            done_str = "true" if done else "false"
            print(f"[STEP]  step={step_count} action={action_str} reward={reward:.2f} done={done_str} error={error_str}")

            if done:
                break

            messages.append({"role": "assistant", "content": llm_output})
            truncated = result_str[:1500] if len(result_str) > 1500 else result_str
            messages.append({
                "role": "user",
                "content": f"Tool result:\n{truncated}\n\nWhat is your next tool call? Respond with JSON only.",
            })

    except Exception as e:
        if step_count == 0:
            step_count = 1
            rewards.append(0.0)
            print(f"[STEP]  step=1 action=noop() reward=0.00 done=false error={str(e)[:200]}")

    return success, step_count, rewards


def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from client import IncidentEnv

    with IncidentEnv(base_url=ENV_BASE_URL).sync() as env:
        for task in TASKS:
            success, steps, rewards = run_task(client, env, task)
            rewards_str = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
            success_str = "true" if success else "false"
            print(f"[END]   success={success_str} steps={steps} rewards={rewards_str}")


if __name__ == "__main__":
    main()
