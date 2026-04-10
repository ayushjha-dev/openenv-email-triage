#!/usr/bin/env python3
"""
OpenEnv-compliant inference script for openenv-email-triage.

Stdout contract (strict):
- [START] once at episode start
- [STEP] once after each /step call returns
- [END] once at the end, always emitted
"""

import argparse
import json
import os
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI


# Required by submission requirements.
# Defaults are provided only for API_BASE_URL and MODEL_NAME.
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")

# Environment runtime settings.
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860").rstrip("/")
TASK_NAME = os.getenv("TASK_NAME", "task1")
BENCHMARK = os.getenv("BENCHMARK", "email-triage")
MAX_STEPS = int(os.getenv("MAX_STEPS", "100"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))


SYSTEM_PROMPT = """You are an AI email triage agent.
Return exactly one JSON object with an action.

Valid action_type values:
CLASSIFY, PRIORITIZE, REPLY_PLAN, ESCALATE, ARCHIVE, DEFER, DONE

Expected shape:
{
  "action_type": "CLASSIFY|PRIORITIZE|REPLY_PLAN|ESCALATE|ARCHIVE|DEFER|DONE",
  "email_id": "email_XXX",
  "category": "work|personal|spam|newsletter|urgent|support|sales|internal",
  "priority": "critical|high|medium|low",
  "reply_plan": "optional",
  "reason": "brief optional rationale"
}

Only include fields required for your action.
"""


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def get_client() -> OpenAI:
    return OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)


def reset_environment(task_id: str) -> Dict[str, Any]:
    response = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
    response.raise_for_status()
    return response.json()


def step_environment(action: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(f"{ENV_URL}/step", json={"action": action}, timeout=30)
    response.raise_for_status()
    return response.json()


def close_environment() -> None:
    # Best-effort close to honor the requirement of ending after a close attempt.
    try:
        requests.post(f"{ENV_URL}/close", timeout=10)
    except Exception:
        return


def format_observation(observation: Dict[str, Any]) -> str:
    emails = observation.get("emails", [])
    current_task = observation.get("current_task", "")
    message = observation.get("message", "")
    processed = observation.get("processed_count", 0)
    total = observation.get("total_count", 0)

    lines = [
        f"Task: {current_task}",
        f"Status: {processed}/{total} processed",
        f"Message: {message}",
        "Inbox:",
    ]

    for email in emails:
        lines.append(
            " | ".join(
                [
                    f"id={email.get('id', '')}",
                    f"from={email.get('sender', '')}",
                    f"subject={email.get('subject', '')}",
                    f"body={email.get('body', '')}",
                    f"predicted_category={email.get('predicted_category', '')}",
                    f"predicted_priority={email.get('predicted_priority', '')}",
                    f"processed={email.get('is_processed', False)}",
                ]
            )
        )

    return "\n".join(lines)


def parse_action(text: str) -> Optional[Dict[str, Any]]:
    raw = text.strip()

    if "```json" in raw:
        start = raw.find("```json") + len("```json")
        end = raw.find("```", start)
        raw = raw[start:end].strip() if end != -1 else raw[start:].strip()
    elif "```" in raw:
        start = raw.find("```") + len("```")
        end = raw.find("```", start)
        raw = raw[start:end].strip() if end != -1 else raw[start:].strip()

    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def action_to_log_str(action: Dict[str, Any]) -> str:
    action_type = str(action.get("action_type", "UNKNOWN"))
    email_id = str(action.get("email_id", ""))

    if action_type == "CLASSIFY":
        return f"CLASSIFY('{email_id}','{action.get('category', '?')}')"
    if action_type == "PRIORITIZE":
        return f"PRIORITIZE('{email_id}','{action.get('priority', '?')}')"
    if action_type == "REPLY_PLAN":
        return f"REPLY_PLAN('{email_id}')"
    if action_type == "ESCALATE":
        return f"ESCALATE('{email_id}')"
    if action_type == "ARCHIVE":
        return f"ARCHIVE('{email_id}')"
    if action_type == "DEFER":
        return f"DEFER('{email_id}')"
    if action_type == "DONE":
        return "DONE()"
    return f"{action_type}('{email_id}')"


def get_model_action(
    client: OpenAI,
    observation: Dict[str, Any],
    history: List[Dict[str, str]],
) -> Dict[str, Any]:
    user_prompt = format_observation(observation)

    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_prompt})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = (completion.choices[0].message.content or "").strip()
    except Exception:
        return {"action_type": "DONE", "reason": "model_error"}

    parsed = parse_action(content)
    if not parsed:
        return {"action_type": "DONE", "reason": "invalid_json"}

    if "action_type" not in parsed:
        return {"action_type": "DONE", "reason": "missing_action_type"}

    return parsed


def run_episode(task_id: str) -> None:
    client: Optional[OpenAI] = None

    rewards: List[float] = []
    steps_taken = 0
    score = 0.01
    success = False
    done = False

    history: List[Dict[str, str]] = []
    observation: Dict[str, Any] = {}

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        if not HF_TOKEN:
            raise RuntimeError("HF_TOKEN (or API_KEY/OPENAI_API_KEY) is not set")

        client = get_client()
        reset_resp = reset_environment(task_id)
        observation = reset_resp.get("observation", {})

        for step in range(1, MAX_STEPS + 1):
            action_obj = get_model_action(client, observation, history)
            action_str = action_to_log_str(action_obj)

            reward = 0.0
            step_error: Optional[str] = None

            try:
                step_resp = step_environment(action_obj)
                observation = step_resp.get("observation", {})
                reward = float(step_resp.get("reward", 0.0) or 0.0)
                done = bool(step_resp.get("done", False))
                info = step_resp.get("info", {}) or {}
                step_error = info.get("error")

                if done:
                    score = float(info.get("final_score", score) or score)
            except Exception as exc:
                done = True
                step_error = str(exc)

            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=action_str,
                reward=reward,
                done=done,
                error=step_error,
            )

            history.append({"role": "assistant", "content": json.dumps(action_obj)})
            history.append({"role": "user", "content": f"reward={reward:.2f} done={str(done).lower()}"})

            if done:
                break

        if not done and steps_taken > 0:
            # Episode capped by max steps; keep score in range.
            score = min(max(score, 0.01), 0.99)

        score = min(max(score, 0.01), 0.99)
        success = done and score > 0.01

    except Exception:
        success = False
        score = 0.01

    finally:
        close_environment()
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one OpenEnv email-triage episode")
    parser.add_argument("--task", type=str, default=TASK_NAME, help="Task id (default from TASK_NAME)")
    args = parser.parse_args()
    run_episode(args.task)


if __name__ == "__main__":
    main()
