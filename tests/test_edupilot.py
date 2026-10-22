"""Offline unit tests for EduPilot (no network, no LLM, no decider API calls).

Uses FakeDecider from fakes.py and the kit's hermetic_env fixture (conftest.py).
Run with:  python -m pytest tests/test_edupilot.py -v
"""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from typing import Any

import pytest

from fakes import FakeDecider

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fresh_store():
    from agent.tools import reset_store
    return reset_store()


def _fake_tool_event(tool_name: str, tool_input: dict[str, Any] = None, messages: list = None):
    """Minimal Strands tool-call event for testing InterventionHandler."""
    return SimpleNamespace(
        tool_use={"name": tool_name, "input": tool_input or {}},
        agent=SimpleNamespace(messages=messages or []),
    )


# ---------------------------------------------------------------------------
# StudyStore and plan_sessions (pure logic, no I/O)
# ---------------------------------------------------------------------------

class TestStudyStore:
    def test_days_until_exam_correct(self):
        from agent.tools import Subject
        s = Subject(name="X", exam_date="2026-12-01")
        d = s.days_until_exam(today=date(2026, 11, 21))
        assert d == 10

    def test_all_topics_returns_flat_list(self):
        store = _fresh_store()
        topics = store.all_topics()
        assert len(topics) == 6
        names = {t["name"] for t in topics}
        assert "entropy" in names and "amplifiers" in names

    def test_summary_contains_student_name(self):
        store = _fresh_store()
        assert "Priya" in store.summary()

    def test_topic_lookup_hit_and_miss(self):
        store = _fresh_store()
        assert store.topic("Thermodynamics", "entropy") is not None
        assert store.topic("Thermodynamics", "nonexistent") is None
        assert store.topic("Nonexistent", "entropy") is None


class TestPlanSessions:
    def test_respects_available_hours(self):
        from agent.tools import plan_sessions
        store = _fresh_store()
        sessions = plan_sessions(store.all_topics(), available_hours=3.0,
                                 today=date(2026, 10, 22))
        total = sum(s["hours"] for s in sessions)
        assert total <= 3.0 + 1e-6

    def test_weakest_topic_comes_first(self):
        from agent.tools import plan_sessions
        store = _fresh_store()
        sessions = plan_sessions(store.all_topics(), available_hours=20.0,
                                 today=date(2026, 10, 22))
        assert sessions, "plan should not be empty"
        # entropy has strength 1 and Thermodynamics is closer — must be first
        assert sessions[0]["topic"] == "entropy"

    def test_full_strength_topics_excluded(self):
        from agent.tools import plan_sessions, reset_store
        store = reset_store()
        # Boost all strengths to 5
        for subj in store.subjects:
            for t in subj.topics:
                t.strength = 5
        sessions = plan_sessions(store.all_topics(), available_hours=20.0)
        assert sessions == []

    def test_pure_function_same_inputs_same_output(self):
        from agent.tools import plan_sessions
        store = _fresh_store()
        today = date(2026, 10, 22)
        s1 = plan_sessions(store.all_topics(), 20.0, today)
        s2 = plan_sessions(store.all_topics(), 20.0, today)
        assert s1 == s2


# ---------------------------------------------------------------------------
# Tool functions (via the @tool wrappers)
# ---------------------------------------------------------------------------

class TestGetStudentProfile:
    def test_returns_all_subjects(self):
        _fresh_store()
        from agent.tools import get_student_profile
        result = get_student_profile("S001")
        assert "error" not in result
        assert len(result["subjects"]) == 2

    def test_unknown_student(self):
        _fresh_store()
        from agent.tools import get_student_profile
        result = get_student_profile("UNKNOWN")
        assert "error" in result


class TestAssessTopic:
    def test_returns_question_for_known_topic(self):
        _fresh_store()
        from agent.tools import assess_topic
        result = assess_topic("S001", "Thermodynamics", "entropy")
        assert "error" not in result
        assert "question" in result
        assert result["current_strength"] == 1   # synthetic default

    def test_unknown_subject_returns_error(self):
        _fresh_store()
        from agent.tools import assess_topic
        result = assess_topic("S001", "Astrology", "horoscopes")
        assert "error" in result

    def test_unknown_topic_returns_error(self):
        _fresh_store()
        from agent.tools import assess_topic
        result = assess_topic("S001", "Thermodynamics", "quantum_entanglement")
        assert "error" in result


class TestRecordQuizResult:
    def test_records_score_and_updates_strength(self):
        store = _fresh_store()
        from agent.tools import record_quiz_result
        result = record_quiz_result("S001", "Thermodynamics", "entropy", 4)
        assert result["new_strength"] == 4
        assert result["old_strength"] == 1
        # Confirm the store was mutated
        t = store.topic("Thermodynamics", "entropy")
        assert t.strength == 4
        assert t.last_quiz is not None

    def test_score_out_of_range_returns_error(self):
        _fresh_store()
        from agent.tools import record_quiz_result
        assert "error" in record_quiz_result("S001", "Thermodynamics", "entropy", 0)
        assert "error" in record_quiz_result("S001", "Thermodynamics", "entropy", 6)

    def test_quiz_added_to_history(self):
        store = _fresh_store()
        from agent.tools import record_quiz_result
        record_quiz_result("S001", "Electronics", "diodes", 5)
        assert any(q.topic == "diodes" for q in store.quiz_history)

    def test_suggest_replan_when_score_changes(self):
        _fresh_store()
        from agent.tools import record_quiz_result
        r = record_quiz_result("S001", "Thermodynamics", "entropy", 3)
        assert r["suggest_replan"] is True

    def test_no_suggest_replan_when_score_unchanged(self):
        _fresh_store()
        from agent.tools import record_quiz_result
        # entropy starts at 1; record 1 again
        r = record_quiz_result("S001", "Thermodynamics", "entropy", 1)
        assert r["suggest_replan"] is False


class TestCreateStudyPlan:
    def test_plan_text_contains_entropy(self):
        _fresh_store()
        from agent.tools import create_study_plan
        result = create_study_plan("S001", available_hours=10.0)
        assert "entropy" in result["plan"]

    def test_sessions_count_within_available_hours(self):
        _fresh_store()
        from agent.tools import create_study_plan, HOURS_PER_SESSION
        result = create_study_plan("S001", available_hours=4.5)
        assert result["total_hours"] <= 4.5 + 1e-6

    def test_plan_stored_in_store(self):
        store = _fresh_store()
        from agent.tools import create_study_plan
        create_study_plan("S001", available_hours=20.0)
        assert len(store.current_plan) > 0


class TestReplanStudy:
    def test_replan_after_score_change(self):
        store = _fresh_store()
        from agent.tools import record_quiz_result, replan_study
        # Improve entropy: was 1, now 5
        record_quiz_result("S001", "Thermodynamics", "entropy", 5)
        result = replan_study("S001", available_hours=20.0, reason="improved entropy")
        assert "error" not in result
        # entropy (now strength 5) should no longer be first
        if store.current_plan:
            assert store.current_plan[0]["topic"] != "entropy"


class TestExplainRecommendation:
    def test_returns_top_priority_topic(self):
        _fresh_store()
        from agent.tools import explain_recommendation
        result = explain_recommendation("S001")
        assert "error" not in result
        assert result["top_priority"] == "entropy"   # strength 1, nearest exam
        assert "evidence" in result
        assert len(result["evidence"]) >= 1

    def test_explanation_mentions_strength_and_days(self):
        _fresh_store()
        from agent.tools import explain_recommendation
        result = explain_recommendation("S001")
        exp = result["explanation"]
        assert "1/5" in exp or "strength" in exp.lower()


# ---------------------------------------------------------------------------
# AcademicActionSelector (wired decision; offline using FakeDecider)
# ---------------------------------------------------------------------------

class TestAcademicActionSelector:
    def _make_selector(self, action_choice: str = "assess", confidence: float = 0.85):
        def rule(state: str, name: str, q: dict) -> Any:
            if name == "action":
                return action_choice
            return action_choice

        return FakeDecider(rule)

    def test_proceeds_when_confident(self):
        from strands.interventions import Proceed
        from agent.decision import AcademicActionSelector

        sel = AcademicActionSelector(self._make_selector("assess", 0.85), confidence_threshold=0.50)
        event = _fake_tool_event("assess_topic")
        sel.before_invocation(event)
        result = sel.before_tool_call(event)
        assert isinstance(result, Proceed)

    def test_log_populated_after_tool_call(self):
        from agent.decision import AcademicActionSelector

        sel = AcademicActionSelector(self._make_selector("plan"))
        event = _fake_tool_event("create_study_plan", {"student_id": "S001", "available_hours": 20})
        sel.before_invocation(event)
        sel.before_tool_call(event)
        assert len(sel.log) == 1
        assert sel.log[0]["action"] == "plan"
        assert "action_confidence" in sel.log[0]
        assert "decider_ms" in sel.log[0]

    def test_guided_when_confidence_below_threshold(self):
        """Low-confidence rule: FakeDecider returns low confidence for clarify."""
        from strands.interventions import Guide
        from agent.decision import AcademicActionSelector

        # Make FakeDecider return "clarify" with low confidence (0.15)
        def low_conf_rule(state: str, name: str, q: dict) -> Any:
            return "clarify"

        fake = FakeDecider(low_conf_rule)
        # The fake returns confidence=0.85 for choice; override the probability to be below threshold
        # by patching the Decision directly via a custom fake
        class LowConfFake:
            last_latency_ms = 5.0
            calls = []
            def ask(self, state, questions, images=None):
                from decider_kit.client import Decision
                self.calls.append((state, questions))
                opts = list(questions["action"]["criteria"])
                probs = {o: (1 / len(opts)) for o in opts}   # uniform = low confidence
                return {"action": Decision.parse({
                    "type": "choice", "choice": "clarify",
                    "probabilities": probs, "confidence": 1 / len(opts)
                })}

        sel = AcademicActionSelector(LowConfFake(), confidence_threshold=0.50)
        event = _fake_tool_event("assess_topic")
        sel.before_invocation(event)
        result = sel.before_tool_call(event)
        assert isinstance(result, Guide)
        assert sel.log[0]["verdict"] == "clarify"

    def test_guided_only_once_per_turn(self):
        """Second call for the same tool within a turn proceeds (not infinite loop)."""
        from strands.interventions import Guide, Proceed
        from agent.decision import AcademicActionSelector

        class LowConfFake:
            last_latency_ms = 5.0
            calls = []
            def ask(self, state, questions, images=None):
                from decider_kit.client import Decision
                self.calls.append(1)
                opts = list(questions["action"]["criteria"])
                probs = {o: 1 / len(opts) for o in opts}
                return {"action": Decision.parse({
                    "type": "choice", "choice": "clarify",
                    "probabilities": probs, "confidence": 1 / len(opts)
                })}

        sel = AcademicActionSelector(LowConfFake(), confidence_threshold=0.50)
        event = _fake_tool_event("assess_topic")
        sel.before_invocation(event)
        first = sel.before_tool_call(event)
        second = sel.before_tool_call(event)
        assert isinstance(first, Guide)
        assert isinstance(second, Proceed)   # guided once, second call proceeds

    def test_before_invocation_resets_guided_set(self):
        from strands.interventions import Guide
        from agent.decision import AcademicActionSelector

        class LowConfFake:
            last_latency_ms = 5.0
            def ask(self, state, questions, images=None):
                from decider_kit.client import Decision
                opts = list(questions["action"]["criteria"])
                probs = {o: 1 / len(opts) for o in opts}
                return {"action": Decision.parse({
                    "type": "choice", "choice": "clarify",
                    "probabilities": probs, "confidence": 1 / len(opts)
                })}

        sel = AcademicActionSelector(LowConfFake(), confidence_threshold=0.50)
        event = _fake_tool_event("assess_topic")
        sel.before_invocation(event)
        sel.before_tool_call(event)       # guided
        sel.before_invocation(event)      # new turn → reset
        result = sel.before_tool_call(event)
        assert isinstance(result, Guide)  # fresh turn → guides again


# ---------------------------------------------------------------------------
# HackathonAgent contract (offline: FakeDecider, no real LLM)
# ---------------------------------------------------------------------------

class TestHackathonAgentContract:
    def test_chat_returns_required_fields(self, monkeypatch):
        """chat() always returns reply, decisions, model_id, latency_ms, agent, eager."""
        # Stub out the Strands Agent call so no LLM is needed
        import agent.agent as mod
        from agent.agent import HackathonAgent

        class _FakeAgent:
            messages = []
            def __call__(self, msg, **kw):
                return type("R", (), {"__str__": lambda self: "Here is your study plan.", "metrics": type("M", (), {"accumulated_usage": {}})()})()

        original_session = HackathonAgent._session

        def _patched_session(self, session_id):
            from agent.decision import AcademicActionSelector
            selector = AcademicActionSelector(FakeDecider())
            return _FakeAgent(), selector

        monkeypatch.setattr(HackathonAgent, "_session", _patched_session)

        a = HackathonAgent(decider=FakeDecider(), model_id="us.amazon.nova-lite-v1:0")
        out = a.chat("What should I study?")
        assert "reply" in out
        assert "decisions" in out
        assert "model_id" in out
        assert "latency_ms" in out
        assert "agent" in out
        assert "eager" in out

    def test_agent_name_is_edupilot(self):
        from agent.agent import NAME
        assert "EduPilot" in NAME
