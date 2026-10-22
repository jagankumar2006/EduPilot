# EduPilot — Design

## Architecture

```
student message
      │
      ▼
HackathonAgent.chat()          agent/agent.py
      │
      ▼
Strands Agent (LLM)            decider_kit.llm.agent_model()
      │  (before every tool call)
      ▼
AcademicActionSelector         agent/decision.py   ← Strands Decider 2B here
      │  Proceed / Guide
      ▼
@tool functions                agent/tools.py
      │
      ▼
StudyStore (in-memory)         agent/tools.py
      │
      ▼
reply + decisions dict         returned by chat()
```

## Layers

### 1. Data model — `StudyStore`, `Subject`, `Topic`, `QuizResult`

Pure Python dataclasses. No I/O. The module-level singleton `_STORE` is the live state;
`reset_store()` resets it to synthetic defaults (used by tests).

Each `Topic` has:
- `name: str` — canonical identifier used by all tool calls
- `strength: int` — 1 (very weak) to 5 (strong); set to the reported quiz score on `record_quiz_result`
- `last_quiz: str | None` — ISO datetime of the last recorded quiz

### 2. Planner — `plan_sessions()`, `_urgency()`

Pure function. Inputs: flat list of topic dicts + available hours + optional reference date.
Output: list of session dicts, sorted by urgency, capped at `MAX_SESSIONS` and `available_hours`.

Urgency formula: `days_to_exam − (5 − strength) × 0.8`
- Weak topics (strength 1) subtract up to 3.2 urgency-days → sort earlier.
- Near exams subtract fewer days → sort earlier.
- Stronger topics on far exams sort last.

This is all Python. The decider never sees raw numbers and is never asked to rank topics.

### 3. Tools — six `@tool` functions

| Tool | Purpose |
|---|---|
| `get_student_profile` | Return subjects, topic strengths, exam dates, quiz count |
| `assess_topic` | Return a quiz question for the topic; report current strength |
| `create_study_plan` | Run `plan_sessions()`; persist to `store.current_plan`; return text |
| `record_quiz_result` | Update `topic.strength` = score; append to quiz history; return delta + advice |
| `replan_study` | Re-run `plan_sessions()` with updated strengths; persist |
| `explain_recommendation` | Run urgency sort; return top topic + evidence list + explanation |

Each docstring is one sentence: the LLM and the tool-selector read it.

### 4. Decision — `AcademicActionSelector`

Strands `InterventionHandler`. Runs `before_tool_call` on every tool invocation.

State string sent to the decider:
```
--- STUDENT CONVERSATION (most recent first) ---
<last 8 turns rendered as ROLE: text>

--- STUDENT STUDY STATE ---
Student: Priya (ID: S001)
  Thermodynamics: exam 2026-10-30 (8 days) | topics: heat_transfer (2/5), enthalpy (3/5), entropy (1/5)
  Electronics: exam 2026-11-13 (22 days) | topics: diodes (4/5), transistors (3/5), amplifiers (2/5)
```

Single question: `action` (choice over 6 options). One decider call per tool call.

Low-confidence handling: if `action.confidence < 0.50`, return `Guide` asking the student to
clarify. Each tool name is guided at most once per turn (`_guided` set); the second attempt
proceeds to avoid an infinite loop.

### 5. Agent — `HackathonAgent`

Keeps one `(Agent, AcademicActionSelector)` pair per `session_id`. The system prompt is built
from `get_store().summary()` at session creation so dates are always accurate.

`chat()` returns the kit contract:
```python
{
    "reply": str,
    "decisions": list[dict],   # one entry per decider call this turn
    "model_id": str,
    "latency_ms": int,
    "agent": str,
    "eager": bool,
}
```

## Decision quality and low-confidence handling

The `decisions` list in every `chat()` response contains, per decider call:
- `action`: chosen option label
- `action_confidence`: 0..1
- `action_probabilities`: full distribution over all six options
- `decider_ms`: wall time
- `verdict`: "proceed" or "clarify"

When `verdict == "clarify"`, the LLM is sent back with a `Guide` prompt to ask the student
for more information before calling a tool. This is reported in the demo UI's decision panel.

## Files changed

| File | Role |
|---|---|
| `agent/tools.py` | StudyStore, planner, six @tool functions, synthetic data |
| `agent/decision.py` | AcademicActionSelector, QUESTIONS, PATTERN_TAG |
| `agent/agent.py` | HackathonAgent, system prompt builder |
| `agent/AGENT.md` | Use-case description |
| `agent/eval_cases.jsonl` | 24 labelled cases (12 tune, 12 test) |
| `agent/demo_script.yaml` | Video script |
| `agent/features.yaml` | AgentCore Memory + Gateway |
| `tests/test_edupilot.py` | 31 offline unit tests |
| `.kiro/specs/edupilot/` | This spec |
