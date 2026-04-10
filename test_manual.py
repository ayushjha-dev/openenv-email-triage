#!/usr/bin/env python3
"""Manual test without AI - demonstrates the environment works."""

import requests
import json

ENV_URL = "http://localhost:7860"

# Reset with task1
print("1. Resetting environment...")
reset_resp = requests.post(f"{ENV_URL}/reset", json={"task_id": "task1"}).json()
print(f"   Loaded {reset_resp['observation']['total_count']} emails\n")

# Get first 3 emails
emails = reset_resp['observation']['emails'][:3]

actions = [
    {"action_type": "CLASSIFY", "email_id": "email_001", "category": "work"},
    {"action_type": "PRIORITIZE", "email_id": "email_001", "priority": "high"},
    {"action_type": "CLASSIFY", "email_id": "email_002", "category": "newsletter"},
    {"action_type": "PRIORITIZE", "email_id": "email_002", "priority": "low"},
    {"action_type": "CLASSIFY", "email_id": "email_003", "category": "personal"},
    {"action_type": "PRIORITIZE", "email_id": "email_003", "priority": "medium"},
    {"action_type": "CLASSIFY", "email_id": "email_004", "category": "spam"},
    {"action_type": "CLASSIFY", "email_id": "email_005", "category": "urgent"},
    {"action_type": "DONE"}
]

total_reward = 0
for i, action in enumerate(actions, 1):
    print(f"{i}. {action['action_type']}: {action.get('email_id', 'N/A')}")
    resp = requests.post(f"{ENV_URL}/step", json={"action": action}).json()
    reward = resp['reward']
    total_reward += reward
    print(f"   Reward: {reward:+.3f} | Total: {total_reward:.3f}")
    print(f"   {resp['observation']['message']}\n")
    
    if resp['done']:
        print(f"✅ FINAL SCORE: {resp['info'].get('final_score', 0):.2%}")
        break
