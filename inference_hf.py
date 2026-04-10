#!/usr/bin/env python3
"""
Inference Script for Email Triage Environment with Hugging Face Support.

Supports both OpenAI and Hugging Face Inference APIs.

Structured logging format (REQUIRED):
[START] task=<task> env=<env> model=<model>
[STEP] step=<n> action=<action> reward=<r> done=<bool> error=<err>
[END] success=<bool> steps=<n> score=<s> rewards=<r1>,<r2>,...
"""

import os
import json
import requests
import time
from typing import Dict, Any, Optional, List


# Configuration from environment variables (OpenEnv spec compliance)
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or ""
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
BENCHMARK = "email-triage"

# Legacy support for direct HF Inference API
API_PROVIDER = os.getenv("API_PROVIDER", "openai")  # "openai" (HF router) or "huggingface" (direct)
HF_API_URL = "https://api-inference.huggingface.co/models/"


# ============================================================================
# Structured Logging Functions (OpenEnv Spec Required)
# ============================================================================

def log_start(task: str, env: str, model: str) -> None:
    """Log episode start in required format."""
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str] = None) -> None:
    """Log step in required format."""
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    """Log episode end in required format."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def format_action_str(action: Dict[str, Any]) -> str:
    """Format action for logging."""
    action_type = action.get("action_type", "UNKNOWN")
    email_id = action.get("email_id", "")
    
    if action_type == "CLASSIFY":
        category = action.get("category", "?")
        return f"CLASSIFY('{email_id}','{category}')"
    elif action_type == "PRIORITIZE":
        priority = action.get("priority", "?")
        return f"PRIORITIZE('{email_id}','{priority}')"
    elif action_type == "ESCALATE":
        return f"ESCALATE('{email_id}')"
    elif action_type == "ARCHIVE":
        return f"ARCHIVE('{email_id}')"
    elif action_type == "DEFER":
        return f"DEFER('{email_id}')"
    elif action_type == "REPLY_PLAN":
        return f"REPLY_PLAN('{email_id}')"
    elif action_type == "DONE":
        return "DONE()"
    else:
        return f"{action_type}('{email_id}')"


class LLMClient:
    """Unified client for OpenAI and Hugging Face APIs."""
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.model_name = MODEL_NAME
        
        if provider == "openai":
            # Uses HF Router or OpenAI-compatible endpoint
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)
            except ImportError:
                raise ImportError("OpenAI package not installed. Run: pip install openai")
        elif provider == "huggingface":
            # Direct HF Inference API
            if not HF_TOKEN:
                raise ValueError("HF_TOKEN environment variable is required for Hugging Face API")
            self.hf_headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'huggingface'")
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 500) -> str:
        """Send chat completion request."""
        if self.provider == "openai":
            return self._openai_chat(messages, temperature, max_tokens)
        else:
            return self._hf_chat(messages, temperature, max_tokens)
    
    def _openai_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        """OpenAI chat completion."""
        response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def _hf_chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> str:
        """Hugging Face Inference API chat."""
        # Format messages for instruction-tuned models
        prompt = self._format_messages_for_hf(messages)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "return_full_text": False,
                "do_sample": True,
                "top_p": 0.95
            }
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{HF_API_URL}{MODEL_NAME}",
                    headers=self.hf_headers,
                    json=payload,
                    timeout=120
                )
                
                if response.status_code == 503:
                    # Model is loading
                    wait_time = 20 * (attempt + 1)
                    print(f"Model is loading, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        return result["generated_text"]
                    elif "error" in result:
                        print(f"HF API Error: {result['error']}")
                        if attempt < max_retries - 1:
                            time.sleep(5)
                            continue
                
                return str(result)
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error: {e}, retrying...")
                    time.sleep(5)
                else:
                    raise
        
        raise Exception("Max retries exceeded")
    
    def _format_messages_for_hf(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages for Mistral instruction format."""
        formatted = ""
        system_msg = ""
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_msg = content
            elif role == "user":
                if system_msg and not formatted:
                    # First user message, include system
                    formatted += f"[INST] {system_msg}\n\n{content} [/INST]"
                    system_msg = ""
                else:
                    formatted += f"[INST] {content} [/INST]"
            elif role == "assistant":
                formatted += f" {content} "
        
        return formatted


def get_client() -> LLMClient:
    """Get LLM client configured for the API."""
    return LLMClient(provider=API_PROVIDER)


def reset_environment(task_id: str = "task1") -> Dict[str, Any]:
    """Reset the environment with a specified task."""
    response = requests.post(
        f"{ENV_URL}/reset",
        json={"task_id": task_id},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def step_environment(action: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an action in the environment."""
    response = requests.post(
        f"{ENV_URL}/step",
        json={"action": action},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def get_environment_state() -> Dict[str, Any]:
    """Get current environment state."""
    response = requests.get(f"{ENV_URL}/state", timeout=30)
    response.raise_for_status()
    return response.json()


def format_observation_for_agent(observation: Dict[str, Any]) -> str:
    """Format observation as a prompt for the agent."""
    emails = observation.get("emails", [])
    task = observation.get("current_task", "")
    message = observation.get("message", "")
    processed = observation.get("processed_count", 0)
    total = observation.get("total_count", 0)
    
    prompt = f"""## Current Task
{task}

## Status
Processed: {processed}/{total} emails
Message: {message}

## Inbox
"""
    
    for email in emails:
        status_flags = []
        if email.get("is_processed"):
            status_flags.append("PROCESSED")
        if email.get("is_escalated"):
            status_flags.append("ESCALATED")
        if email.get("is_archived"):
            status_flags.append("ARCHIVED")
        if email.get("is_deferred"):
            status_flags.append("DEFERRED")
        
        status = f" [{', '.join(status_flags)}]" if status_flags else ""
        category = f" | Category: {email.get('predicted_category')}" if email.get('predicted_category') else ""
        priority = f" | Priority: {email.get('predicted_priority')}" if email.get('predicted_priority') else ""
        
        prompt += f"""
### Email ID: {email['id']}{status}
From: {email['sender']}
Subject: {email['subject']}
Time: {email['timestamp']}{category}{priority}

{email['body']}
---
"""
    
    return prompt


def parse_agent_response(response_text: str) -> Optional[Dict[str, Any]]:
    """Parse agent response to extract action."""
    # Try to find JSON in the response
    try:
        # Look for JSON block
        if "```json" in response_text:
            json_start = response_text.index("```json") + 7
            json_end = response_text.index("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.index("```") + 3
            json_end = response_text.index("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        elif "{" in response_text and "}" in response_text:
            # Try to extract JSON object
            json_start = response_text.index("{")
            json_end = response_text.rindex("}") + 1
            json_str = response_text[json_start:json_end].strip()
        else:
            # Try to parse the whole response as JSON
            json_str = response_text.strip()
        
        return json.loads(json_str)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Response was: {response_text[:200]}")
        return None


SYSTEM_PROMPT = """You are an AI email triage agent. Your task is to process emails in an inbox by:
1. CLASSIFY: Assign a category (work, personal, spam, newsletter, urgent, support, sales, internal)
2. PRIORITIZE: Assign a priority level (critical, high, medium, low)
3. Take appropriate actions: ESCALATE (urgent/critical issues), ARCHIVE (spam/low priority), DEFER (need more time)
4. When finished processing all emails, use DONE

Respond ONLY with a JSON action in this exact format:
```json
{
    "action_type": "CLASSIFY",
    "email_id": "email_001",
    "category": "work",
    "reason": "Brief explanation"
}
```

Action types and required fields:
- CLASSIFY: action_type, email_id, category
- PRIORITIZE: action_type, email_id, priority
- REPLY_PLAN: action_type, email_id, reply_plan
- ESCALATE: action_type, email_id
- ARCHIVE: action_type, email_id
- DEFER: action_type, email_id
- DONE: action_type

Process each email systematically. First classify, then prioritize, then take final action if needed.
"""


def run_agent(task_id: str = "task1", max_iterations: int = 100, verbose: bool = True) -> Dict[str, Any]:
    """
    Run the agent on a task.
    
    Args:
        task_id: Task to run (task1, task2, task3)
        max_iterations: Maximum number of iterations
        verbose: Whether to print progress
        
    Returns:
        Results dictionary with final score and history
    """
    client = get_client()
    rewards_list: List[float] = []
    
    # Reset environment
    reset_response = reset_environment(task_id)
    observation = reset_response["observation"]
    
    # [START] log - Required structured logging
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    
    if verbose:
        print(f"# Provider: {API_PROVIDER}", flush=True)
        print(f"# Task: {reset_response['info']['task']['name']}", flush=True)
        print(f"# Emails to process: {observation['total_count']}", flush=True)
    
    # Conversation history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    history = []
    total_reward = 0.0
    done = False
    step_num = 0
    parse_failures = 0
    max_parse_failures = 5
    
    while not done and step_num < max_iterations and parse_failures < max_parse_failures:
        # Format observation for agent
        observation_prompt = format_observation_for_agent(observation)
        messages.append({"role": "user", "content": observation_prompt})
        
        # Get agent response
        try:
            agent_response = client.chat(messages, temperature=0.2, max_tokens=500)
            messages.append({"role": "assistant", "content": agent_response})
        except Exception as e:
            log_step(step=step_num + 1, action="ERROR", reward=0.0, done=True, error=str(e))
            break
        
        # Parse action
        action = parse_agent_response(agent_response)
        
        if action is None:
            parse_failures += 1
            messages.append({
                "role": "user",
                "content": "Please respond with a valid JSON action as specified in the format above."
            })
            continue
        
        step_num += 1
        
        # Execute action
        try:
            step_response = step_environment(action)
            observation = step_response["observation"]
            reward = step_response["reward"]
            done = step_response["done"]
            info = step_response["info"]
        except Exception as e:
            log_step(step=step_num, action=format_action_str(action), reward=0.0, done=True, error=str(e))
            break
        
        total_reward += reward
        rewards_list.append(reward)
        
        # [STEP] log - Required structured logging
        log_step(
            step=step_num,
            action=format_action_str(action),
            reward=reward,
            done=done,
            error=None
        )
        
        history.append({
            "iteration": step_num,
            "action": action,
            "reward": reward,
            "done": done,
            "info": info
        })
        
        # Add feedback to conversation
        feedback = f"Action executed. Reward: {reward:.3f}. {observation.get('message', '')}"
        if done:
            feedback += f" Episode complete. Final score: {info.get('final_score', 'N/A')}"
        messages.append({"role": "user", "content": feedback})
    
    # Calculate final score
    raw_final_score = history[-1]["info"].get("final_score", 0.01) if history else 0.01
    final_score = min(max(raw_final_score, 0.01), 0.99)
    success = done and final_score > 0.01
    
    # [END] log - Required structured logging
    log_end(success=success, steps=step_num, score=final_score, rewards=rewards_list)
    
    results = {
        "task_id": task_id,
        "iterations": step_num,
        "total_reward": total_reward,
        "final_score": final_score,
        "done": done,
        "history": history
    }
    
    return results


def run_all_tasks(verbose: bool = True) -> Dict[str, Any]:
    """Run agent on all tasks and report results."""
    results = {}
    
    for task_id in ["task1", "task2", "task3"]:
        try:
            results[task_id] = run_agent(task_id, verbose=verbose)
        except Exception as e:
            print(f"# Error running {task_id}: {e}", flush=True)
            results[task_id] = {"error": str(e)}
    
    # Print summary (non-structured, for human readability)
    if verbose:
        print(f"\n# SUMMARY", flush=True)
        for task_id, result in results.items():
            if "error" in result:
                print(f"# {task_id}: ERROR - {result['error']}", flush=True)
            else:
                print(f"# {task_id}: Score = {result['final_score']:.3f}", flush=True)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Email Triage Agent")
    parser.add_argument("--task", type=str, default="all", 
                        choices=["task1", "task2", "task3", "all"],
                        help="Task to run (default: all)")
    parser.add_argument("--provider", type=str, 
                        choices=["openai", "huggingface"],
                        help="API provider (default: from API_PROVIDER env var)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress verbose output")
    
    args = parser.parse_args()
    
    if args.provider:
        API_PROVIDER = args.provider
    
    if args.task == "all":
        run_all_tasks(verbose=not args.quiet)
    else:
        run_agent(args.task, verbose=not args.quiet)
