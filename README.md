---
title: OpenEnv Email Triage
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
tags:
  - openenv
pinned: false
---

# 📧 openenv-email-triage

> **OpenEnv Email Triage Environment** — AI-Powered Email Triage Simulation

A production-ready, OpenEnv-compatible environment that simulates intelligent email triage workflows. AI agents learn to classify, prioritize, and handle emails just like a real professional.

**Repository:** [`openenv-email-triage`](https://huggingface.co/spaces/ayushjha85/openenv-email-triage)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-purple.svg)](https://github.com/openenv-community/openenv)

**Project ID:** `openenv-email-triage` | **Version:** 1.0.0 | **License:** MIT

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Tasks & Difficulty Levels](#tasks--difficulty-levels)
- [Action Space](#action-space)
- [Reward System](#reward-system)
- [AI Agent Integration](#ai-agent-integration)
- [Examples](#examples)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The **Email Triage Environment** is a reinforcement learning environment where AI agents learn to:

1. **Classify** emails into categories (work, personal, spam, urgent, etc.)
2. **Prioritize** emails by importance (critical, high, medium, low)
3. **Take actions** like escalating urgent issues, archiving spam, or deferring complex matters
4. **Optimize** their workflow to maximize accuracy and efficiency

### Why Email Triage?

- **Real-world relevance**: Email management is a universal professional task
- **Progressive difficulty**: From simple classification to complex multi-action workflows
- **Clear evaluation**: Objective ground truth for measuring performance
- **Partial rewards**: Agents get immediate feedback on each decision
- **Novel domain**: Underexplored in OpenEnv ecosystem

---

## ✨ Features

### 🎓 Three Difficulty Levels
- **Easy (Task 1)**: 5 emails, basic classification
- **Medium (Task 2)**: 10 emails, classification + prioritization
- **Hard (Task 3)**: 15 emails, full triage workflow with escalation/archiving

### 🎬 Six Action Types
- `CLASSIFY` - Categorize emails
- `PRIORITIZE` - Assign urgency levels
- `REPLY_PLAN` - Draft response strategies
- `ESCALATE` - Forward critical issues
- `ARCHIVE` - Remove low-value emails
- `DEFER` - Postpone complex items

### 🏆 Intelligent Scoring
- Step-by-step rewards (+0.02 for correct classification/priority)
- Penalty for errors (-0.01 to -0.05)
- Final score based on overall accuracy (0.0 to 1.0)

### 🔌 API Compatibility
- **OpenAI API** - Compatible with GPT-4, GPT-3.5, etc.
- **Hugging Face Inference** - Use open-source models (Llama, Mistral, Phi)
- **Custom endpoints** - Any OpenAI-compatible API

### 🐳 Production Ready
- Fully Dockerized
- FastAPI server with CORS support
- Health checks and monitoring
- Ready for Hugging Face Spaces deployment

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager
- (Optional) Docker for containerized deployment

### 1. Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd openenv-email-triage

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Start the FastAPI server
uvicorn src.server:app --host 0.0.0.0 --port 7860

# Server will be available at http://localhost:7860
```

### 3. Test the Environment

```bash
# Check health
curl http://localhost:7860/health

# List available tasks
curl http://localhost:7860/tasks

# Run manual test
python test_manual.py
```

### 4. Run AI Agent (Optional)

```bash
# Using Hugging Face Inference API
export API_PROVIDER=huggingface
export HF_TOKEN=your_hf_token_here
python inference_hf.py --task task1

# Or using OpenAI
export API_PROVIDER=openai
export OPENAI_API_KEY=your_openai_key_here
python inference.py --task task1
```

---

## 📦 Installation

### Standard Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation

```bash
# Build the Docker image
docker build -t email-triage-env .

# Run the container
docker run -p 7860:7860 email-triage-env

# With environment variables
docker run -p 7860:7860 \
  -e HF_TOKEN=your_token \
  email-triage-env
```

### Development Installation

```bash
# Install with development tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

---

## 💻 Usage

### Starting the Server

```bash
# Basic start
uvicorn src.server:app --port 7860

# With auto-reload (development)
uvicorn src.server:app --reload --port 7860

# With custom host
uvicorn src.server:app --host 0.0.0.0 --port 7860
```

### Running Inference

#### Required Environment Variables (OpenEnv Spec)

The following environment variables **MUST** be set for the inference script:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | The API endpoint for the LLM | `https://router.huggingface.co/v1` |
| `MODEL_NAME` | The model identifier to use | `Qwen/Qwen2.5-72B-Instruct` |
| `HF_TOKEN` | Your Hugging Face / API key | `hf_xxxxxxxxxxxxx` |
| `LOCAL_IMAGE_NAME` | Local image name when using docker-image based OpenEnv runners | `openenv-email-triage:latest` |

#### Standard Usage (OpenEnv Compliant)

```bash
# Configure required environment variables
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="hf_xxxxxxxxxxxxx"

# Run on all tasks (default)
python inference.py

# Run on specific task
python inference.py --task task1

# Quiet mode (structured logs only)
python inference.py --quiet
```

#### Example Output (Structured Logging)

The inference script emits structured logs in the required format:

```
[START] task=task1 env=email-triage model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=CLASSIFY('email_001','work') reward=0.02 done=false error=null
[STEP] step=2 action=PRIORITIZE('email_001','high') reward=0.02 done=false error=null
...
[END] success=true steps=9 score=1.00 rewards=0.02,0.02,0.02,...
```

Important: `inference.py` writes only these three line types to stdout (`[START]`, `[STEP]`, `[END]`) in that order for each run.

#### Alternative: With Direct HF Inference API

```bash
# For direct HuggingFace Inference API
export API_PROVIDER=huggingface
export HF_TOKEN=hf_xxxxxxxxxxxxx
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3

python inference_hf.py --task all
```

### Manual Testing

```python
import requests

# Reset environment
reset_response = requests.post(
    "http://localhost:7860/reset",
    json={"task_id": "task1"}
)

# Execute action
step_response = requests.post(
    "http://localhost:7860/step",
    json={
        "action": {
            "action_type": "CLASSIFY",
            "email_id": "email_001",
            "category": "work"
        }
    }
)

print(f"Reward: {step_response.json()['reward']}")
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:7860
```

### Endpoints

#### `GET /`
**Root endpoint** - Returns API information

**Response:**
```json
{
  "name": "Email Triage Environment",
  "version": "1.0.0",
  "description": "AI email triage environment for OpenEnv hackathon"
}
```

---

#### `GET /health`
**Health check** - Verify server is running

**Response:**
```json
{
  "status": "healthy"
}
```

---

#### `GET /tasks`
**List tasks** - Get all available tasks

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "task1",
      "name": "Basic Email Classification",
      "difficulty": "easy",
      "email_count": 5,
      "max_steps": 50
    }
  ],
  "total": 3
}
```

---

#### `POST /reset`
**Reset environment** - Start a new episode with specified task

**Request Body:**
```json
{
  "task_id": "task1"
}
```

**Response:**
```json
{
  "observation": {
    "emails": [...],
    "processed_count": 0,
    "total_count": 5,
    "current_task": "Classify 5 emails...",
    "message": "Environment reset..."
  },
  "info": {
    "task": {...}
  }
}
```

---

#### `POST /step`
**Execute action** - Perform an action in the environment

**Request Body:**
```json
{
  "action": {
    "action_type": "CLASSIFY",
    "email_id": "email_001",
    "category": "work",
    "reason": "Contains project discussion"
  }
}
```

**Response:**
```json
{
  "observation": {...},
  "reward": 0.02,
  "done": false,
  "info": {
    "action": "CLASSIFY",
    "step_reward": 0.02,
    "accumulated_reward": 0.02
  }
}
```

---

#### `GET /state`
**Get current state** - Retrieve environment state

**Response:**
```json
{
  "task_id": "task1",
  "observation": {...},
  "reward": 0.08,
  "done": false,
  "info": {
    "step_count": 4,
    "max_steps": 50,
    "processed_emails": 2
  }
}
```

---

## 📊 Tasks & Difficulty Levels

### Task 1: Basic Email Classification (Easy)
**Goal:** Classify 5 emails into correct categories

| Metric | Value |
|--------|-------|
| Emails | 5 |
| Max Steps | 50 |
| Target Score | 0.8 - 1.0 |
| Required Actions | CLASSIFY only |

**Sample Emails:**
- Boss request (work)
- Newsletter (newsletter)
- Family invitation (personal)
- Prize scam (spam)
- Server emergency (urgent)

---

### Task 2: Classification & Prioritization (Medium)
**Goal:** Classify AND prioritize 10 emails

| Metric | Value |
|--------|-------|
| Emails | 10 |
| Max Steps | 100 |
| Target Score | 0.6 - 0.8 |
| Required Actions | CLASSIFY + PRIORITIZE |

**Adds:**
- Support tickets (support)
- Sales offers (sales)
- Internal memos (internal)
- Client communications (work)

---

### Task 3: Full Email Triage (Hard)
**Goal:** Complete triage workflow for 15 emails

| Metric | Value |
|--------|-------|
| Emails | 15 |
| Max Steps | 150 |
| Target Score | 0.4 - 0.65 |
| Required Actions | All actions available |

**Adds:**
- Security alerts (urgent → ESCALATE)
- Marketing spam (spam → ARCHIVE)
- Strategic planning (work → DEFER)
- Angry customers (support → ESCALATE)

---

## 🎮 Action Space

### CLASSIFY
**Assign a category to an email**

**Fields:**
- `action_type`: `"CLASSIFY"`
- `email_id`: Target email ID (required)
- `category`: One of the categories below (required)
- `reason`: Brief explanation (optional)

**Categories:**
- `work` - Work-related correspondence
- `personal` - Personal messages
- `spam` - Unwanted/promotional
- `newsletter` - Subscribed updates
- `urgent` - Time-critical issues
- `support` - Customer service requests
- `sales` - Sales inquiries
- `internal` - Company-internal communications

**Example:**
```json
{
  "action_type": "CLASSIFY",
  "email_id": "email_001",
  "category": "work",
  "reason": "Contains Q3 report discussion"
}
```

**Reward:** +0.02 (correct), -0.01 (incorrect)

---

### PRIORITIZE
**Assign priority level to an email**

**Fields:**
- `action_type`: `"PRIORITIZE"`
- `email_id`: Target email ID (required)
- `priority`: One of the priorities below (required)
- `reason`: Brief explanation (optional)

**Priorities:**
- `critical` - Immediate action required
- `high` - Important, address soon
- `medium` - Normal priority
- `low` - Can wait

**Example:**
```json
{
  "action_type": "PRIORITIZE",
  "email_id": "email_005",
  "priority": "critical",
  "reason": "Production server is down"
}
```

**Reward:** +0.02 (correct), -0.01 (incorrect)

---

### REPLY_PLAN
**Create a reply strategy**

**Fields:**
- `action_type`: `"REPLY_PLAN"`
- `email_id`: Target email ID (required)
- `reply_plan`: Draft response strategy (required)

**Example:**
```json
{
  "action_type": "REPLY_PLAN",
  "email_id": "email_009",
  "reply_plan": "Schedule call for next week to discuss contract renewal terms"
}
```

**Reward:** +0.01

---

### ESCALATE
**Forward to supervisor/specialist**

**Fields:**
- `action_type`: `"ESCALATE"`
- `email_id`: Target email ID (required)
- `reason`: Why escalating (optional)

**Example:**
```json
{
  "action_type": "ESCALATE",
  "email_id": "email_011",
  "reason": "Security threat requires immediate attention"
}
```

**Reward:** +0.01 (appropriate), -0.02 (inappropriate)

---

### ARCHIVE
**Remove email from active inbox**

**Fields:**
- `action_type`: `"ARCHIVE"`
- `email_id`: Target email ID (required)

**Example:**
```json
{
  "action_type": "ARCHIVE",
  "email_id": "email_012"
}
```

**Reward:** +0.01 (appropriate), -0.02 (inappropriate)

---

### DEFER
**Postpone handling**

**Fields:**
- `action_type`: `"DEFER"`
- `email_id`: Target email ID (required)

**Example:**
```json
{
  "action_type": "DEFER",
  "email_id": "email_013"
}
```

**Reward:** +0.01 (appropriate), -0.01 (inappropriate)

---

### DONE
**Complete the episode**

**Fields:**
- `action_type`: `"DONE"`

**Example:**
```json
{
  "action_type": "DONE"
}
```

**Reward:** Final score (0.0 - 1.0) based on overall accuracy

---

## 🏆 Reward System

### Step Rewards

| Action | Correct | Incorrect | Invalid |
|--------|---------|-----------|---------|
| CLASSIFY | +0.02 | -0.01 | -0.05 |
| PRIORITIZE | +0.02 | -0.01 | -0.05 |
| ESCALATE | +0.01 | -0.02 | -0.05 |
| ARCHIVE | +0.01 | -0.02 | -0.05 |
| DEFER | +0.01 | -0.01 | -0.05 |
| REPLY_PLAN | +0.01 | - | -0.05 |

### Final Score Calculation

**Task 1 (Easy):**
```
score = correct_classifications / total_emails
```

**Task 2 (Medium):**
```
score = (correct_classifications + correct_priorities) / (2 * total_emails)
```

**Task 3 (Hard):**
```
score = (category_score * 0.4) + (priority_score * 0.3) + (action_score * 0.3)
```

### Target Scores

| Difficulty | Minimum | Good | Excellent |
|------------|---------|------|-----------|
| Easy | 0.60 | 0.80 | 0.95+ |
| Medium | 0.40 | 0.65 | 0.85+ |
| Hard | 0.30 | 0.50 | 0.70+ |

---

## 🤖 AI Agent Integration

### Supported APIs

#### 1. OpenAI (GPT-4, GPT-3.5, etc.)

```bash
# Setup
export API_PROVIDER=openai
export OPENAI_API_KEY=sk-xxxxx
export OPENAI_MODEL=gpt-4

# Run
python inference.py --task task1
```

#### 2. Hugging Face Inference API

```bash
# Setup
export API_PROVIDER=huggingface
export HF_TOKEN=hf_xxxxx
export HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# Run
python inference_hf.py --task task1
```

**Supported Models:**
- `mistralai/Mistral-7B-Instruct-v0.3`
- `meta-llama/Llama-3.2-3B-Instruct`
- `microsoft/Phi-3-mini-4k-instruct`
- Any instruction-tuned model on HF

#### 3. Custom Endpoints

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-custom-api.com/v1",
    api_key="your-key"
)
```

---

## 📋 Examples

### Example 1: Complete Task 1 Workflow

```python
import requests

BASE_URL = "http://localhost:7860"

# 1. Reset environment
reset_resp = requests.post(f"{BASE_URL}/reset", json={"task_id": "task1"})
emails = reset_resp.json()["observation"]["emails"]

# 2. Process each email
for email in emails[:5]:
    # Classify
    requests.post(f"{BASE_URL}/step", json={
        "action": {
            "action_type": "CLASSIFY",
            "email_id": email["id"],
            "category": determine_category(email)  # Your logic
        }
    })

# 3. Complete task
done_resp = requests.post(f"{BASE_URL}/step", json={
    "action": {"action_type": "DONE"}
})

print(f"Final Score: {done_resp.json()['info']['final_score']}")
```

### Example 2: Task 2 with Priority

```python
for email in emails:
    # Classify
    requests.post(f"{BASE_URL}/step", json={
        "action": {
            "action_type": "CLASSIFY",
            "email_id": email["id"],
            "category": "work"
        }
    })
    
    # Prioritize
    requests.post(f"{BASE_URL}/step", json={
        "action": {
            "action_type": "PRIORITIZE",
            "email_id": email["id"],
            "priority": "high"
        }
    })
```

### Example 3: Task 3 with Escalation

```python
for email in emails:
    if is_critical(email):
        # Escalate urgent issues
        requests.post(f"{BASE_URL}/step", json={
            "action": {
                "action_type": "ESCALATE",
                "email_id": email["id"]
            }
        })
    elif is_spam(email):
        # Archive spam
        requests.post(f"{BASE_URL}/step", json={
            "action": {
                "action_type": "ARCHIVE",
                "email_id": email["id"]
            }
        })
```

---

## 🚀 Deployment

### Hugging Face Spaces
---
title: OpenEnv Email Triage
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
tags:
  - openenv
pinned: false
---

# 📧 openenv-email-triage

> **OpenEnv Email Triage Environment** — AI-Powered Email Triage Simulation

A production-ready, OpenEnv-compatible environment that simulates intelligent email triage workflows. AI agents learn to classify, prioritize, and handle emails just like a real professional.

**Repository:** [`openenv-email-triage`](https://huggingface.co/spaces/ayushjha85/openenv-email-triage)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-purple.svg)](https://github.com/openenv-community/openenv)

**Project ID:** `openenv-email-triage` | **Version:** 1.0.0 | **License:** MIT

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Tasks & Difficulty Levels](#tasks--difficulty-levels)
- [Action Space](#action-space)
- [Reward System](#reward-system)
- [AI Agent Integration](#ai-agent-integration)
- [Examples](#examples)
- [Deployment](#deployment)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

The **Email Triage Environment** is a reinforcement learning environment where AI agents learn to:

1. **Classify** emails into categories (work, personal, spam, urgent, etc.)
2. **Prioritize** emails by importance (critical, high, medium, low)
3. **Take actions** like escalating urgent issues, archiving spam, or deferring complex matters
4. **Optimize** their workflow to maximize accuracy and efficiency

### Why Email Triage?

- **Real-world relevance**: Email management is a universal professional task
- **Progressive difficulty**: From simple classification to complex multi-action workflows
- **Clear evaluation**: Objective ground truth for measuring performance
- **Partial rewards**: Agents get immediate feedback on each decision
- **Novel domain**: Underexplored in OpenEnv ecosystem

---

## ✨ Features

### 🎓 Three Difficulty Levels
- **Easy (Task 1)**: 5 emails, basic classification
- **Medium (Task 2)**: 10 emails, classification + prioritization
- **Hard (Task 3)**: 15 emails, full triage workflow with escalation/archiving

### 🎬 Six Action Types
- `CLASSIFY` - Categorize emails
- `PRIORITIZE` - Assign urgency levels
- `REPLY_PLAN` - Draft response strategies
- `ESCALATE` - Forward critical issues
- `ARCHIVE` - Remove low-value emails
- `DEFER` - Postpone complex items

### 🏆 Intelligent Scoring
- Step-by-step rewards (+0.02 for correct classification/priority)
- Penalty for errors (-0.01 to -0.05)
- Final score based on overall accuracy (0.0 to 1.0)

### 🔌 API Compatibility
- **OpenAI API** - Compatible with GPT-4, GPT-3.5, etc.
- **Hugging Face Inference** - Use open-source models (Llama, Mistral, Phi)
- **Custom endpoints** - Any OpenAI-compatible API

### 🐳 Production Ready
- Fully Dockerized
- FastAPI server with CORS support
- Health checks and monitoring
- Ready for Hugging Face Spaces deployment

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip package manager
- (Optional) Docker for containerized deployment

### 1. Clone & Install

```bash
# Clone the repository
git clone <your-repo-url>
cd openenv-email-triage

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Start the FastAPI server
uvicorn src.server:app --host 0.0.0.0 --port 7860

# Server will be available at http://localhost:7860
```

### 3. Test the Environment

```bash
# Check health
curl http://localhost:7860/health

# List available tasks
curl http://localhost:7860/tasks

# Run manual test
python test_manual.py
```

### 4. Run AI Agent (Optional)

```bash
# Using Hugging Face Inference API
export API_PROVIDER=huggingface
export HF_TOKEN=your_hf_token_here
python inference_hf.py --task task1

# Or using OpenAI
export API_PROVIDER=openai
export OPENAI_API_KEY=your_openai_key_here
python inference.py --task task1
```

---

## 📦 Installation

### Standard Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation

```bash
# Build the Docker image
docker build -t email-triage-env .

# Run the container
docker run -p 7860:7860 email-triage-env

# With environment variables
docker run -p 7860:7860 \
  -e HF_TOKEN=your_token \
  email-triage-env
```

### Development Installation

```bash
# Install with development tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

---

## 💻 Usage

### Starting the Server

```bash
# Basic start
uvicorn src.server:app --port 7860

# With auto-reload (development)
uvicorn src.server:app --reload --port 7860

# With custom host
uvicorn src.server:app --host 0.0.0.0 --port 7860
```

### Running Inference

#### Required Environment Variables (OpenEnv Spec)

The following environment variables **MUST** be set for the inference script:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_BASE_URL` | The API endpoint for the LLM | `https://router.huggingface.co/v1` |
| `MODEL_NAME` | The model identifier to use | `Qwen/Qwen2.5-72B-Instruct` |
| `HF_TOKEN` | Your Hugging Face / API key | `hf_xxxxxxxxxxxxx` |

#### Standard Usage (OpenEnv Compliant)

```bash
# Configure required environment variables
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="hf_xxxxxxxxxxxxx"

# Run on all tasks (default)
python inference.py

# Run on specific task
python inference.py --task task1

# Quiet mode (structured logs only)
python inference.py --quiet
```

#### Example Output (Structured Logging)

The inference script emits structured logs in the required format:

```
[START] task=task1 env=email-triage model=Qwen/Qwen2.5-72B-Instruct
[STEP] step=1 action=CLASSIFY('email_001','work') reward=0.02 done=false error=null
[STEP] step=2 action=PRIORITIZE('email_001','high') reward=0.02 done=false error=null
...
[END] success=true steps=9 score=1.00 rewards=0.02,0.02,0.02,...
```

#### Alternative: With Direct HF Inference API

```bash
# For direct HuggingFace Inference API
export API_PROVIDER=huggingface
export HF_TOKEN=hf_xxxxxxxxxxxxx
export MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3

python inference_hf.py --task all
```

### Manual Testing

```python
import requests

# Reset environment
reset_response = requests.post(
    "http://localhost:7860/reset",
    json={"task_id": "task1"}
)

# Execute action
step_response = requests.post(
    "http://localhost:7860/step",
    json={
        "action": {
            "action_type": "CLASSIFY",
            "email_id": "email_001",
            "category": "work"
        }
    }
)

print(f"Reward: {step_response.json()['reward']}")
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:7860
```

### Endpoints

#### `GET /`
**Root endpoint** - Returns API information

**Response:**
```json
{
  "name": "Email Triage Environment",
  "version": "1.0.0",
  "description": "AI email triage environment for OpenEnv hackathon"
}
```

---

#### `GET /health`
**Health check** - Verify server is running

**Response:**
```json
{
  "status": "healthy"
}
```

---

#### `GET /tasks`
**List tasks** - Get all available tasks

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "task1",
      "name": "Basic Email Classification",
      "difficulty": "easy",
      "email_count": 5,
      "max_steps": 50
    }
  ],
  "total": 3
}
```

---

#### `POST /reset`
**Reset environment** - Start a new episode with specified task

**Request Body:**
```json
{
  "task_id": "task1"
}
```

**Response:**
```json
{
  "observation": {
    "emails": [...],
    "processed_count": 0,
    "total_count": 5,
    "current_task": "Classify 5 emails...",
    "message": "Environment reset..."
  },
  "info": {
    "task": {...}
  }
}
```

---

#### `POST /step`
**Execute action** - Perform an action in the environment

**Request Body:**
```json
{
  "action": {
    "action_type": "CLASSIFY",
    "email_id": "email_001",
    "category": "work",
    "reason": "Contains project discussion"
  }
}
```

**Response:**
```json
{
  "observation": {...},
  "reward": 0.02,
  "done": false,
  "info": {
    "action": "CLASSIFY",
    "step_reward": 0.02,
    "accumulated_reward": 0.02
  }
}
```

---

#### `GET /state`
**Get current state** - Retrieve environment state

**Response:**
```json
{
  "task_id": "task1",
  "observation": {...},
  "reward": 0.08,
  "done": false,
  "info": {
    "step_count": 4,
    "max_steps": 50,
    "processed_emails": 2
  }
}
```

---

## 📊 Tasks & Difficulty Levels

### Task 1: Basic Email Classification (Easy)
**Goal:** Classify 5 emails into correct categories

| Metric | Value |
|--------|-------|
| Emails | 5 |
| Max Steps | 50 |
| Target Score | 0.8 - 1.0 |
| Required Actions | CLASSIFY only |

**Sample Emails:**
- Boss request (work)
- Newsletter (newsletter)
- Family invitation (personal)
- Prize scam (spam)
- Server emergency (urgent)

---

### Task 2: Classification & Prioritization (Medium)
**Goal:** Classify AND prioritize 10 emails

| Metric | Value |
|--------|-------|
| Emails | 10 |
| Max Steps | 100 |
| Target Score | 0.6 - 0.8 |
| Required Actions | CLASSIFY + PRIORITIZE |

**Adds:**
- Support tickets (support)
- Sales offers (sales)
- Internal memos (internal)
- Client communications (work)

---

### Task 3: Full Email Triage (Hard)
**Goal:** Complete triage workflow for 15 emails

| Metric | Value |
|--------|-------|
| Emails | 15 |
| Max Steps | 150 |
| Target Score | 0.4 - 0.65 |
| Required Actions | All actions available |

**Adds:**
- Security alerts (urgent → ESCALATE)
- Marketing spam (spam → ARCHIVE)
- Strategic planning (work → DEFER)
- Angry customers (support → ESCALATE)

---

## 🎮 Action Space

### CLASSIFY
**Assign a category to an email**

**Fields:**
- `action_type`: `"CLASSIFY"`
- `email_id`: Target email ID (required)
- `category`: One of the categories below (required)
- `reason`: Brief explanation (optional)

**Categories:**
- `work` - Work-related correspondence
- `personal` - Personal messages
- `spam` - Unwanted/promotional
- `newsletter` - Subscribed updates
- `urgent` - Time-critical issues
- `support` - Customer service requests
- `sales` - Sales inquiries
- `internal` - Company-internal communications

**Example:**
```json
{
  "action_type": "CLASSIFY",
  "email_id": "email_001",
  "category": "work",
  "reason": "Contains Q3 report discussion"
}
```

**Reward:** +0.02 (correct), -0.01 (incorrect)

---

### PRIORITIZE
**Assign priority level to an email**

**Fields:**
- `action_type`: `"PRIORITIZE"`
- `email_id`: Target email ID (required)
- `priority`: One of the priorities below (required)
- `reason`: Brief explanation (optional)

**Priorities:**
- `critical` - Immediate action required
- `high` - Important, address soon
- `medium` - Normal priority
- `low` - Can wait

**Example:**
```json
{
  "action_type": "PRIORITIZE",
  "email_id": "email_005",
  "priority": "critical",
  "reason": "Production server is down"
}
```

**Reward:** +0.02 (correct), -0.01 (incorrect)

---

### REPLY_PLAN
**Create a reply strategy**

**Fields:**
- `action_type`: `"REPLY_PLAN"`
- `email_id`: Target email ID (required)
- `reply_plan`: Draft response strategy (required)

**Example:**
```json
{
  "action_type": "REPLY_PLAN",
  "email_id": "email_009",
  "reply_plan": "Schedule call for next week to discuss contract renewal terms"
}
```

**Reward:** +0.01

---

### ESCALATE
**Forward to supervisor/specialist**

**Fields:**
- `action_type`: `"ESCALATE"`
- `email_id`: Target email ID (required)
- `reason`: Why escalating (optional)

**Example:**
```json
{
  "action_type": "ESCALATE",
  "email_id": "email_011",
  "reason": "Security threat requires immediate attention"
}
```

**Reward:** +0.01 (appropriate), -0.02 (inappropriate)

---

### ARCHIVE
**Remove email from active inbox**

**Fields:**
- `action_type`: `"ARCHIVE"`
- `email_id`: Target email ID (required)

**Example:**
```json
{
  "action_type": "ARCHIVE",
  "email_id": "email_012"
}
```

**Reward:** +0.01 (appropriate), -0.02 (inappropriate)

---

### DEFER
**Postpone handling**

**Fields:**
- `action_type`: `"DEFER"`
- `email_id`: Target email ID (required)

**Example:**
```json
{
  "action_type": "DEFER",
  "email_id": "email_013"
}
```

**Reward:** +0.01 (appropriate), -0.01 (inappropriate)

---

### DONE
**Complete the episode**

**Fields:**
- `action_type`: `"DONE"`

**Example:**
```json
{
  "action_type": "DONE"
}
```

**Reward:** Final score (0.0 - 1.0) based on overall accuracy

---

## 🏆 Reward System

### Step Rewards

| Action | Correct | Incorrect | Invalid |
|--------|---------|-----------|---------|
| CLASSIFY | +0.02 | -0.01 | -0.05 |
| PRIORITIZE | +0.02 | -0.01 | -0.05 |
| ESCALATE | +0.01 | -0.02 | -0.05 |
| ARCHIVE | +0.01 | -0.02 | -0.05 |
| DEFER | +0.01 | -0.01 | -0.05 |
| REPLY_PLAN | +0.01 | - | -0.05 |

### Final Score Calculation

**Task 1 (Easy):**
```
score = correct_classifications / total_emails
```

**Task 2 (Medium):**
```
score = (correct_classifications + correct_priorities) / (2 * total_emails)
```

**Task 3 (Hard):**
```
score = (category_score * 0.4) + (priority_score * 0.3) + (action_score * 0.3)
```

### Target Scores

| Difficulty | Minimum | Good | Excellent |
|------------|---------|------|-----------|
| Easy | 0.60 | 0.80 | 0.95+ |
| Medium | 0.40 | 0.65 | 0.85+ |
| Hard | 0.30 | 0.50 | 0.70+ |

---

## 🤖 AI Agent Integration

### Supported APIs

#### 1. OpenAI (GPT-4, GPT-3.5, etc.)

```bash
# Setup
export API_PROVIDER=openai
export OPENAI_API_KEY=sk-xxxxx
export OPENAI_MODEL=gpt-4

# Run
python inference.py --task task1
```

#### 2. Hugging Face Inference API

```bash
# Setup
export API_PROVIDER=huggingface
export HF_TOKEN=hf_xxxxx
export HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# Run
python inference_hf.py --task task1
```

**Supported Models:**
- `mistralai/Mistral-7B-Instruct-v0.3`
- `meta-llama/Llama-3.2-3B-Instruct`
- `microsoft/Phi-3-mini-4k-instruct`
- Any instruction-tuned model on HF

#### 3. Custom Endpoints

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-custom-api.com/v1",
    api_key="your-key"
)
```

---

## 📋 Examples

### Example 1: Complete Task 1 Workflow

```python
import requests

BASE_URL = "http://localhost:7860"

# 1. Reset environment
reset_resp = requests.post(f"{BASE_URL}/reset", json={"task_id": "task1"})
emails = reset_resp.json()["observation"]["emails"]

# 2. Process each email
for email in emails[:5]:
    # Classify
    requests.post(f"{BASE_URL}/step", json={
        "action": {
            "action_type": "CLASSIFY",
            "email_id": email["id"],
            "category": determine_category(email)  # Your logic
        }
    })

# 3. Complete task
done_resp = requests.post(f"{BASE_URL}/step", json={
    "action": {"action_type": "DONE"}
})

print(f"Final Score: {done_resp.json()['info']['final_score']}")
```

### Example 2: Task 2 with Priority

```python
for email in emails:
    # Classify
    requests.post(f"{BASE_URL}/step", json={
        "action": {
            "action_type": "CLASSIFY",
            "email_id": email["id"],
            "category": "work"
        }
    })
    
    # Prioritize
    requests.post(f"{BASE_URL}/step", json={
        "action": {
            "action_type": "PRIORITIZE",
            "email_id": email["id"],
            "priority": "high"
        }
    })
```

### Example 3: Task 3 with Escalation

```python
for email in emails:
    if is_critical(email):
        # Escalate urgent issues
        requests.post(f"{BASE_URL}/step", json={
            "action": {
                "action_type": "ESCALATE",
                "email_id": email["id"]
            }
        })
    elif is_spam(email):
        # Archive spam
        requests.post(f"{BASE_URL}/step", json={
            "action": {
                "action_type": "ARCHIVE",
                "email_id": email["id"]
            }
        })
```

---

## 🚀 Deployment

### Hugging Face Spaces

#### 1. Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Select **Docker** as the SDK
4. Choose a name (e.g., `email-triage-env`)

#### 2. Push Your Code

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
cd email-triage-env

# Copy project files
cp -r /path/to/openenv-email-triage/* .

# Add and commit
git add .
git commit -m "Initial deployment"
git push
```

#### 3. Configure Secrets

In your Space settings, add:
- `HF_TOKEN` (for inference)
- `OPENAI_API_KEY` (if using OpenAI)

#### 4. Verify Deployment

Your Space will be available at:
```
https://YOUR_USERNAME-email-triage-env.hf.space
```

### AWS/GCP/Azure

```bash
# Build Docker image
docker build -t email-triage-env .

# Tag for registry
docker tag email-triage-env:latest your-registry/email-triage-env:latest

# Push to registry
docker push your-registry/email-triage-env:latest

# Deploy (example for Cloud Run)
gcloud run deploy email-triage-env \
  --image your-registry/email-triage-env:latest \
  --platform managed \
  --port 7860
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────┐
│                 AI Agent                         │
│  (OpenAI / Hugging Face / Custom)               │
└───────────────────┬─────────────────────────────┘
                    │ HTTP Requests
                    ▼
┌─────────────────────────────────────────────────┐
│            FastAPI Server (server.py)            │
│  Endpoints: /reset, /step, /state, /tasks       │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│        EmailTriageEnv (environment.py)           │
│  - State management                              │
│  - Reward calculation                            │
│  - Action validation                             │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Tasks       │        │   Models     │
│  (tasks.py)  │        │ (models.py)  │
│              │        │              │
│ - Task1      │        │ - Email      │
│ - Task2      │        │ - Action     │
│ - Task3      │        │ - State      │
│ - Graders    │        │ - etc.       │
└──────────────┘        └──────────────┘
```

### Data Flow

1. **Agent** sends action via POST /step
2. **Server** validates request schema
3. **Environment** processes action and updates state
4. **Grader** calculates reward
5. **Server** returns observation + reward + done
6. **Agent** decides next action

### File Structure

```
src/
├── __init__.py       # Package exports
├── models.py         # Pydantic data models
├── environment.py    # Core RL environment logic
├── tasks.py          # Task definitions & graders
└── server.py         # FastAPI endpoints

inference.py          # OpenAI agent runner
inference_hf.py       # HF Inference API runner
openenv.yaml          # Environment metadata
Dockerfile            # Container definition
requirements.txt      # Python dependencies
```

---

## 🔧 Troubleshooting

### Server won't start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Port already in use

**Problem:** `Address already in use: ('0.0.0.0', 7860)`

**Solution:**
```bash
# Find process
lsof -i :7860

# Kill process
kill <PID>

# Or use different port
uvicorn src.server:app --port 8000
```

---

### HF Inference API returns 410

**Problem:** `410 Client Error: Gone`

**Solution:** Model may be deprecated. Try alternative:
```bash
export HF_MODEL=microsoft/Phi-3-mini-4k-instruct
# or
export HF_MODEL=google/gemma-2b-it
```

---

### Agent gives invalid JSON

**Problem:** Agent response cannot be parsed

**Solution:** Check system prompt and temperature:
```python
# Lower temperature for more structured output
client.chat(messages, temperature=0.1)
```

---

### Docker build fails

**Problem:** Build errors on dependencies

**Solution:**
```bash
# Use --no-cache
docker build --no-cache -t email-triage-env .

# Or update base image
# In Dockerfile: FROM python:3.11-slim
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Development Setup

```bash
# Clone repo
git clone <repo-url>
cd openenv-email-triage

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black src/
flake8 src/
```

### Adding New Tasks

1. Define emails in `src/tasks.py`:
```python
TASK4_EMAILS = [
    create_email(
        id="email_016",
        sender="...",
        subject="...",
        body="...",
        category=EmailCategory.WORK,
        priority=Priority.HIGH
    ),
    # ...
]
```

2. Create grader function:
```python
def task4_grader(emails):
    # Your grading logic
    return score
```

3. Register task:
```python
Task4 = Task(
    task_id="task4",
    name="Your Task Name",
    description="...",
    difficulty="medium",
    emails=TASK4_EMAILS,
    grader=task4_grader,
    max_steps=100
)

TASKS["task4"] = Task4
```

### Submitting Changes

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 OpenEnv Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

- **Issues**: [GitHub Issues](<your-repo>/issues)
- **Discussions**: [GitHub Discussions](<your-repo>/discussions)
- **Email**: support@yourdomain.com

---

## 🙏 Acknowledgments

- Built for the **OpenEnv Hackathon Challenge**
- Inspired by real-world email triage workflows
- Thanks to the FastAPI and Pydantic communities

---

**Happy Hacking! 🚀**

#### 1. Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Select **Docker** as the SDK
4. Choose a name (e.g., `email-triage-env`)

#### 2. Push Your Code

```bash
# Clone your Space
git clone https://huggingface.co/spaces/YOUR_USERNAME/email-triage-env
cd email-triage-env

# Copy project files
cp -r /path/to/openenv-email-triage/* .

# Add and commit
git add .
git commit -m "Initial deployment"
git push
```

#### 3. Configure Secrets

In your Space settings, add:
- `HF_TOKEN` (for inference)
- `OPENAI_API_KEY` (if using OpenAI)

#### 4. Verify Deployment

Your Space will be available at:
```
https://YOUR_USERNAME-email-triage-env.hf.space
```

### AWS/GCP/Azure

```bash
# Build Docker image
docker build -t email-triage-env .

# Tag for registry
docker tag email-triage-env:latest your-registry/email-triage-env:latest

# Push to registry
docker push your-registry/email-triage-env:latest

# Deploy (example for Cloud Run)
gcloud run deploy email-triage-env \
  --image your-registry/email-triage-env:latest \
  --platform managed \
  --port 7860
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────┐
│                 AI Agent                         │
│  (OpenAI / Hugging Face / Custom)               │
└───────────────────┬─────────────────────────────┘
                    │ HTTP Requests
                    ▼
┌─────────────────────────────────────────────────┐
│            FastAPI Server (server.py)            │
│  Endpoints: /reset, /step, /state, /tasks       │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│        EmailTriageEnv (environment.py)           │
│  - State management                              │
│  - Reward calculation                            │
│  - Action validation                             │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Tasks       │        │   Models     │
│  (tasks.py)  │        │ (models.py)  │
│              │        │              │
│ - Task1      │        │ - Email      │
│ - Task2      │        │ - Action     │
│ - Task3      │        │ - State      │
│ - Graders    │        │ - etc.       │
└──────────────┘        └──────────────┘
```

### Data Flow

1. **Agent** sends action via POST /step
2. **Server** validates request schema
3. **Environment** processes action and updates state
4. **Grader** calculates reward
5. **Server** returns observation + reward + done
6. **Agent** decides next action

### File Structure

```
src/
├── __init__.py       # Package exports
├── models.py         # Pydantic data models
├── environment.py    # Core RL environment logic
├── tasks.py          # Task definitions & graders
└── server.py         # FastAPI endpoints

inference.py          # OpenAI agent runner
inference_hf.py       # HF Inference API runner
openenv.yaml          # Environment metadata
Dockerfile            # Container definition
requirements.txt      # Python dependencies
```

---

## 🔧 Troubleshooting

### Server won't start

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Port already in use

**Problem:** `Address already in use: ('0.0.0.0', 7860)`

**Solution:**
```bash
# Find process
lsof -i :7860

# Kill process
kill <PID>

# Or use different port
uvicorn src.server:app --port 8000
```

---

### HF Inference API returns 410

**Problem:** `410 Client Error: Gone`

**Solution:** Model may be deprecated. Try alternative:
```bash
export HF_MODEL=microsoft/Phi-3-mini-4k-instruct
# or
export HF_MODEL=google/gemma-2b-it
```

---

### Agent gives invalid JSON

**Problem:** Agent response cannot be parsed

**Solution:** Check system prompt and temperature:
```python
# Lower temperature for more structured output
client.chat(messages, temperature=0.1)
```

---

### Docker build fails

**Problem:** Build errors on dependencies

**Solution:**
```bash
# Use --no-cache
docker build --no-cache -t email-triage-env .

# Or update base image
# In Dockerfile: FROM python:3.11-slim
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Development Setup

```bash
# Clone repo
git clone <repo-url>
cd openenv-email-triage

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black src/
flake8 src/
```

### Adding New Tasks

1. Define emails in `src/tasks.py`:
```python
TASK4_EMAILS = [
    create_email(
        id="email_016",
        sender="...",
        subject="...",
        body="...",
        category=EmailCategory.WORK,
        priority=Priority.HIGH
    ),
    # ...
]
```

2. Create grader function:
```python
def task4_grader(emails):
    # Your grading logic
    return score
```

3. Register task:
```python
Task4 = Task(
    task_id="task4",
    name="Your Task Name",
    description="...",
    difficulty="medium",
    emails=TASK4_EMAILS,
    grader=task4_grader,
    max_steps=100
)

TASKS["task4"] = Task4
```

### Submitting Changes

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 OpenEnv Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

- **Issues**: [GitHub Issues](<your-repo>/issues)
- **Discussions**: [GitHub Discussions](<your-repo>/discussions)
- **Email**: support@yourdomain.com

---

## 🙏 Acknowledgments

- Built for the **OpenEnv Hackathon Challenge**
- Inspired by real-world email triage workflows
- Thanks to the FastAPI and Pydantic communities

---

**Happy Hacking! 🚀**
