# EduPilot Local Deployment Guide

This agent can run **locally** or **on AWS**. Choose based on your needs.

## Local Deployment (Recommended for Testing)

EduPilot runs fully locally using the Strands Agents SDK and a local LLM (Ollama or cloud-hosted via AWS UG Madurai).

### Prerequisites
- Python 3.10+
- Dependencies installed: `pip install -r requirements.txt`
- Optional: Ollama for local LLM (see `.env`)

### Step 1: Set Up Environment

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` to choose where your LLM runs:

**Option A: AWS UG Madurai Cloud (No Local Setup)**
```
LLM_PROVIDER=ugmdu
LLM_MODEL_ID=qwen3.5-4b
DECIDER_MODE=ugmdu
DECIDER_URL=https://da25tnxy06gjk.cloudfront.net
DECIDER_API_KEY=dcd_live_[key]
```

**Option B: Local Ollama**
```
LLM_PROVIDER=local
LLM_MODEL_ID=qwen:7b  # or another model
# Start Ollama: ollama serve
```

**Option C: Amazon Bedrock (AWS Account Required)**
```
LLM_PROVIDER=bedrock
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
AWS_PROFILE=default
AWS_REGION=us-east-1
```

### Step 2: Run the Demo

**Start the web UI:**
```bash
./kit demo-bg
```
Open http://localhost:8501 in your browser.

**Or chat directly in the terminal:**
```bash
.venv/Scripts/python -c "
from agent.agent import HackathonAgent
a = HackathonAgent(eager=True)
print(a.chat('I have Thermodynamics in 5 days. What should I study first?')['reply'])
"
```

### Step 3: Run Tests

```bash
./kit test
```

Expected: **69/69 tests pass**

### Step 4: View Benchmarks

Real benchmark results (test split, 18 held-out cases):

```bash
cat submission/bench/results.md
```

**Key metrics:**
- Decider accuracy: 100%
- Decider latency p50: 2,438 ms
- Speedup vs LLM: **6.0×**
- Low-confidence cases: 3/18 routed to human for clarification

---

## AWS Deployment (Production)

To deploy EduPilot to **Amazon Bedrock AgentCore Runtime**:

### Prerequisites
- AWS account with Amazon Bedrock access
- AWS credentials configured: `./kit aws-login`
- Node 20+

### Steps

1. **Enable Bedrock models:**
   - AWS Console → Bedrock → Model access
   - Ensure Amazon Nova Pro is available

2. **Deploy:**
   ```bash
   ./kit deploy
   ```
   Wait 2–5 minutes.

3. **Invoke:**
   ```bash
   ./kit invoke "I have Thermodynamics in 5 days. What should I study first?"
   ```

4. **Clean up after submission:**
   ```bash
   ./kit destroy
   ```

---

## Strands Decider 2B Integration

The agent passes every request through Strands Decider 2B before calling a tool. See `agent/decision.py` for the reusable pattern.

**Decision:** which academic action fits the student's request?
- `assess` — quiz on a topic
- `plan` — generate a study schedule
- `record` — record a quiz score
- `replan` — rebuild the schedule after changes
- `explain` — explain priorities
- `clarify` — ask for clarification (low confidence)

**Confidence threshold:** 0.7. Below that, agent asks the student instead of guessing.

---

## Architecture

```
EduPilot (Strands Agents + Bedrock/Ollama)
    ↓
Strands Decider 2B (route to the right tool)
    ↓
Tools (assess, plan, record, replan, explain)
    ↓
Bedrock / Ollama (conversation + planning)
```

---

## Built with the AWS User Group Madurai Strands Decider Hackathon Kit

- Kit: https://github.com/Vivek0712/decider-hackathon-kit
- Decider: https://huggingface.co/StrandsAgents/strands-decider-2B-qwen3.5-v1-2610
- License: Apache-2.0
