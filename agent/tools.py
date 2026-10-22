"""EduPilot tools: academic actions (assess, plan, record, replan, explain) with synthetic data.

All scheduling arithmetic is in pure Python (StudyStore + plan_sessions); Strands Decider 2B
handles the language-based action-routing decision in decision.py.  Synthetic data means the
demo and tests run anywhere with no external dependencies.

Keep each @tool docstring to one clear line: the LLM and the tool-selection pattern read it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from strands import tool

# ---------------------------------------------------------------------------
# Data model (pure Python, no I/O, easy to test)
# ---------------------------------------------------------------------------

@dataclass
class Topic:
    name: str
    strength: int          # 1 (very weak) … 5 (strong)
    last_quiz: str | None = None   # ISO date string of last recorded quiz


@dataclass
class Subject:
    name: str
    exam_date: str         # "YYYY-MM-DD"
    topics: list[Topic] = field(default_factory=list)

    def days_until_exam(self, today: date | None = None) -> int:
        d = (today or date.today())
        return (date.fromisoformat(self.exam_date) - d).days


@dataclass
class QuizResult:
    subject: str
    topic: str
    score: int             # 1–5
    recorded_at: str       # ISO datetime


@dataclass
class StudyStore:
    """In-memory state for one student.  Mutated only by record_quiz_result_pure()."""
    student_id: str
    name: str
    subjects: list[Subject] = field(default_factory=list)
    quiz_history: list[QuizResult] = field(default_factory=list)
    current_plan: list[dict[str, Any]] = field(default_factory=list)

    # -- look-ups ----------------------------------------------------------

    def subject(self, name: str) -> Subject | None:
        return next((s for s in self.subjects if s.name == name), None)

    def topic(self, subject_name: str, topic_name: str) -> Topic | None:
        s = self.subject(subject_name)
        return next((t for t in s.topics if t.name == topic_name), None) if s else None

    def all_topics(self) -> list[dict[str, Any]]:
        """Flat list of topic dicts with subject context, sorted weakest-first within subject."""
        rows: list[dict[str, Any]] = []
        today = date.today()
        for subj in self.subjects:
            dte = subj.days_until_exam(today)
            for t in subj.topics:
                rows.append({
                    "name": t.name,
                    "subject": subj.name,
                    "exam_date": subj.exam_date,
                    "days_to_exam": dte,
                    "strength": t.strength,
                    "last_quiz": t.last_quiz,
                })
        return rows

    def summary(self) -> str:
        """One-paragraph text used in the agent system prompt and decision state."""
        today = date.today()
        lines = [f"Student: {self.name} (ID: {self.student_id})"]
        for subj in self.subjects:
            dte = subj.days_until_exam(today)
            tline = ", ".join(f"{t.name} ({t.strength}/5)" for t in subj.topics)
            lines.append(f"  {subj.name}: exam {subj.exam_date} ({dte} days) | topics: {tline}")
        if self.quiz_history:
            last = self.quiz_history[-1]
            lines.append(f"  Last quiz: {last.topic} ({last.subject}) scored {last.score}/5 on {last.recorded_at[:10]}")
        if self.current_plan:
            lines.append(f"  Current plan: {len(self.current_plan)} sessions scheduled")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Deterministic planner (pure function — no side-effects, easy to test)
# ---------------------------------------------------------------------------

HOURS_PER_SESSION = 1.5
MAX_SESSIONS = 8

def _urgency(days_to_exam: int, strength: int) -> float:
    """Lower score = more urgent.  Weak topics on near exams sort first."""
    # weakness contributes up to 4 extra "urgency days"
    return days_to_exam - (5 - strength) * 0.8


def plan_sessions(
    topics: list[dict[str, Any]],
    available_hours: float,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Return a list of session dicts, sorted by urgency.

    Pure function: same inputs → same outputs.  No datetime.now() inside.
    Each dict has: day_offset, topic, subject, strength, hours, exam_date, days_to_exam.
    """
    today = today or date.today()
    # Filter topics worth scheduling (strength < 5 and exam not yet past)
    schedulable = [t for t in topics if t["strength"] < 5 and t["days_to_exam"] >= 0]
    # Sort: most urgent first
    schedulable.sort(key=lambda t: _urgency(t["days_to_exam"], t["strength"]))

    sessions: list[dict[str, Any]] = []
    hours_used = 0.0
    session_num = 0
    for t in schedulable:
        if hours_used + HOURS_PER_SESSION > available_hours + 1e-9:
            break
        if session_num >= MAX_SESSIONS:
            break
        day_offset = session_num // 3 + 1          # 3 sessions per day
        sessions.append({
            "session": session_num + 1,
            "day_offset": day_offset,
            "topic": t["name"],
            "subject": t["subject"],
            "strength": t["strength"],
            "hours": HOURS_PER_SESSION,
            "exam_date": t["exam_date"],
            "days_to_exam": t["days_to_exam"],
        })
        hours_used += HOURS_PER_SESSION
        session_num += 1
    return sessions


def sessions_to_text(sessions: list[dict[str, Any]], student_name: str, available_hours: float) -> str:
    lines = [f"Study plan for {student_name}  ({available_hours:.0f} h available)"]
    for s in sessions:
        lines.append(
            f"  Day {s['day_offset']}, session {s['session']}: "
            f"{s['topic']} ({s['subject']}) — strength {s['strength']}/5, "
            f"exam in {s['days_to_exam']} days  [{s['hours']:.1f} h]"
        )
    return "\n".join(lines) if sessions else "No topics left to schedule."


# ---------------------------------------------------------------------------
# Synthetic student database  (module-level singleton, reset-able for tests)
# ---------------------------------------------------------------------------

def _make_default_store() -> StudyStore:
    return StudyStore(
        student_id="S001",
        name="Priya",
        subjects=[
            Subject(
                name="Thermodynamics",
                exam_date="2026-10-30",
                topics=[
                    Topic("heat_transfer", strength=2),
                    Topic("enthalpy",      strength=3),
                    Topic("entropy",       strength=1),
                ],
            ),
            Subject(
                name="Electronics",
                exam_date="2026-11-13",
                topics=[
                    Topic("diodes",       strength=4),
                    Topic("transistors",  strength=3),
                    Topic("amplifiers",   strength=2),
                ],
            ),
        ],
    )


# Mutable singleton — tools read/write this; tests can call reset_store()
_STORE = _make_default_store()


def get_store() -> StudyStore:
    return _STORE


def reset_store() -> StudyStore:
    """Reset to the synthetic defaults.  Called by tests."""
    global _STORE
    _STORE = _make_default_store()
    return _STORE


# One canonical assessment question per topic (for the demo; in production this would be a quiz bank)
_ASSESSMENT_QUESTIONS: dict[str, str] = {
    "heat_transfer": "Explain the difference between conduction and convection in heat transfer.",
    "enthalpy":      "How does enthalpy change in an isobaric (constant-pressure) process?",
    "entropy":       "State the second law of thermodynamics using entropy.",
    "diodes":        "What happens to a diode when reverse-biased beyond its breakdown voltage?",
    "transistors":   "Describe how a BJT transistor operates in saturation mode.",
    "amplifiers":    "How does negative feedback affect the gain and bandwidth of an amplifier?",
}


# ---------------------------------------------------------------------------
# @tool functions  (one-line docstrings: read by the LLM and the selector)
# ---------------------------------------------------------------------------

@tool
def get_student_profile(student_id: str) -> dict[str, Any]:
    """Return the student's subjects, topics, topic strengths, exam dates, and study history."""
    store = get_store()
    if store.student_id != student_id:
        return {"error": f"Student {student_id} not found"}
    return {
        "student_id": store.student_id,
        "name": store.name,
        "subjects": [
            {
                "name": subj.name,
                "exam_date": subj.exam_date,
                "days_to_exam": subj.days_until_exam(),
                "topics": [
                    {
                        "name": t.name,
                        "strength": t.strength,
                        "last_quiz": t.last_quiz,
                    }
                    for t in subj.topics
                ],
            }
            for subj in store.subjects
        ],
        "quiz_history_count": len(store.quiz_history),
        "last_quiz": (
            {
                "topic": store.quiz_history[-1].topic,
                "subject": store.quiz_history[-1].subject,
                "score": store.quiz_history[-1].score,
                "recorded_at": store.quiz_history[-1].recorded_at,
            }
            if store.quiz_history else None
        ),
        "current_plan_sessions": len(store.current_plan),
    }


@tool
def assess_topic(student_id: str, subject: str, topic: str) -> dict[str, Any]:
    """Ask the student a quiz question on a specific topic to assess their current understanding."""
    store = get_store()
    if store.student_id != student_id:
        return {"error": f"Student {student_id} not found"}
    t = store.topic(subject, topic)
    if t is None:
        subj = store.subject(subject)
        if subj is None:
            return {"error": f"Subject '{subject}' not found. Available: {[s.name for s in store.subjects]}"}
        return {"error": f"Topic '{topic}' not found in {subject}. Available: {[tp.name for tp in subj.topics]}"}

    question = _ASSESSMENT_QUESTIONS.get(topic, f"Explain the key concepts of {topic}.")
    return {
        "student_id": student_id,
        "subject": subject,
        "topic": topic,
        "current_strength": t.strength,
        "last_quiz": t.last_quiz,
        "question": question,
        "instruction": "Answer in the next message. Then call record_quiz_result with your score (1–5).",
    }


@tool
def create_study_plan(student_id: str, available_hours: float = 20.0) -> dict[str, Any]:
    """Build a prioritised study plan: assign topics to sessions by exam urgency and topic weakness."""
    store = get_store()
    if store.student_id != student_id:
        return {"error": f"Student {student_id} not found"}
    if available_hours <= 0:
        return {"error": "available_hours must be positive"}

    sessions = plan_sessions(store.all_topics(), available_hours)
    store.current_plan = sessions           # persist for replan / explain
    plan_text = sessions_to_text(sessions, store.name, available_hours)

    return {
        "student_id": student_id,
        "plan": plan_text,
        "sessions": len(sessions),
        "total_hours": round(len(sessions) * HOURS_PER_SESSION, 1),
        "available_hours": available_hours,
    }


@tool
def record_quiz_result(student_id: str, subject: str, topic: str, score: int) -> dict[str, Any]:
    """Record a quiz score (1–5) on a topic, update topic strength, and return progress feedback."""
    store = get_store()
    if store.student_id != student_id:
        return {"error": f"Student {student_id} not found"}
    if not 1 <= score <= 5:
        return {"error": f"Score must be between 1 and 5, got {score}"}
    t = store.topic(subject, topic)
    if t is None:
        subj = store.subject(subject)
        if subj is None:
            return {"error": f"Subject '{subject}' not found"}
        return {"error": f"Topic '{topic}' not found in {subject}"}

    old_strength = t.strength
    # Replace strength with the new score (don't average — the latest quiz is ground truth).
    t.strength = score
    now = datetime.now().isoformat(timespec="seconds")
    t.last_quiz = now
    store.quiz_history.append(
        QuizResult(subject=subject, topic=topic, score=score, recorded_at=now)
    )

    delta = score - old_strength
    if delta > 0:
        trend = f"▲ up {delta} point{'s' if delta != 1 else ''}"
    elif delta < 0:
        trend = f"▼ down {abs(delta)} point{'s' if abs(delta) != 1 else ''}"
    else:
        trend = "→ unchanged"

    if score >= 4:
        advice = f"{topic} is solid ({score}/5). You can shift time to weaker topics."
    elif score == 3:
        advice = f"{topic} is okay ({score}/5). One more practice session should make it solid."
    else:
        advice = f"{topic} needs more work ({score}/5). Prioritise it in your next session."

    return {
        "student_id": student_id,
        "subject": subject,
        "topic": topic,
        "score": score,
        "old_strength": old_strength,
        "new_strength": score,
        "trend": trend,
        "advice": advice,
        "suggest_replan": score != old_strength,   # flag so the LLM can prompt a replan
    }


@tool
def replan_study(student_id: str, available_hours: float = 20.0, reason: str = "") -> dict[str, Any]:
    """Rebuild the study plan using the latest quiz results; call after recording a score or a date change."""
    store = get_store()
    if store.student_id != student_id:
        return {"error": f"Student {student_id} not found"}

    sessions = plan_sessions(store.all_topics(), available_hours)
    store.current_plan = sessions
    plan_text = sessions_to_text(sessions, store.name, available_hours)
    msg = "Plan updated"
    if reason:
        msg += f" ({reason})"
    msg += f". {len(sessions)} session(s) scheduled, {round(len(sessions) * HOURS_PER_SESSION, 1)} h total."

    return {
        "student_id": student_id,
        "plan": plan_text,
        "sessions": len(sessions),
        "total_hours": round(len(sessions) * HOURS_PER_SESSION, 1),
        "message": msg,
    }


@tool
def explain_recommendation(student_id: str) -> dict[str, Any]:
    """Explain the top study priority: which topic is most urgent, why, and what to do next."""
    store = get_store()
    if store.student_id != student_id:
        return {"error": f"Student {student_id} not found"}

    topics = store.all_topics()
    if not topics:
        return {"explanation": "No topics found. Start by adding your subjects."}

    # Sort by urgency to find the #1 priority
    topics_with_u = sorted(
        [t for t in topics if t["days_to_exam"] >= 0 and t["strength"] < 5],
        key=lambda t: _urgency(t["days_to_exam"], t["strength"]),
    )

    if not topics_with_u:
        return {
            "explanation": "All topics are at full strength. Keep reviewing to maintain them.",
            "top_priority": None,
        }

    top = topics_with_u[0]
    evidence = [
        f"strength {top['strength']}/5 (target 5/5)",
        f"exam in {top['days_to_exam']} days ({top['exam_date']})",
        f"urgency rank 1 of {len(topics_with_u)} remaining topics",
    ]
    explanation = (
        f"Top priority: {top['name']} ({top['subject']}). "
        f"It scores {top['strength']}/5 and the exam is in {top['days_to_exam']} days — "
        f"the combination of weakness and proximity makes it the most urgent topic."
    )
    if len(topics_with_u) > 1:
        second = topics_with_u[1]
        explanation += (
            f" After that, focus on {second['name']} ({second['subject']}) "
            f"at {second['strength']}/5 with {second['days_to_exam']} days to go."
        )
    if store.current_plan:
        plan_topic = store.current_plan[0]
        explanation += f"\n\nCurrent plan starts with: {plan_topic['topic']} ({plan_topic['subject']}) — session 1 of {len(store.current_plan)}."

    return {
        "student_id": student_id,
        "top_priority": top["name"],
        "subject": top["subject"],
        "strength": top["strength"],
        "days_to_exam": top["days_to_exam"],
        "evidence": evidence,
        "explanation": explanation,
    }


# Exported list consumed by agent.py
TOOLS = [
    get_student_profile,
    assess_topic,
    create_study_plan,
    record_quiz_result,
    replan_study,
    explain_recommendation,
]
