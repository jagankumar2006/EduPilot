# EduPilot — Tasks

## Status: COMPLETE

All tasks were implemented and verified. `python -m pytest tests/` passes 52/52.

---

## Task list

- [x] **T1** Define `StudyStore`, `Subject`, `Topic`, `QuizResult` dataclasses (`agent/tools.py`)
- [x] **T2** Implement `plan_sessions()` pure function with `_urgency()` formula
- [x] **T3** Implement `get_student_profile` tool
- [x] **T4** Implement `assess_topic` tool with per-topic quiz questions
- [x] **T5** Implement `create_study_plan` tool (calls `plan_sessions`, persists to store)
- [x] **T6** Implement `record_quiz_result` tool (replaces strength, appends history, `suggest_replan` flag)
- [x] **T7** Implement `replan_study` tool (re-runs planner with updated strengths)
- [x] **T8** Implement `explain_recommendation` tool (urgency sort, evidence list, explanation text)
- [x] **T9** Implement `AcademicActionSelector` with single `action` question (`agent/decision.py`)
- [x] **T10** Fix `_render_messages()` to handle dict and object Strands message formats
- [x] **T11** Build decision state from live `get_store().summary()` so dates are always accurate
- [x] **T12** Guide-once-per-turn logic (no infinite loops)
- [x] **T13** Update `agent/agent.py`: dynamic system prompt from `get_store().summary()`
- [x] **T14** Write 24 eval cases in `agent/eval_cases.jsonl` (12 tune, 12 test)
- [x] **T15** Write 31 offline unit tests in `tests/test_edupilot.py`
- [x] **T16** Write spec files (requirements, design, tasks) in `.kiro/specs/edupilot/`

## Verification

```
python -m pytest tests/ --ignore=tests/test_llm_providers.py \
                        --ignore=tests/test_agentcore_and_models.py
# 52 passed
```
