"""REUSABLE DECISION PATTERN: academic action selector (#tool-selection)

EduPilot: AI Academic Decision Agent for College Students
AWS User Group Madurai Strands Decider hackathon kit

What it does
    Reads a student's natural-language request and their current study context (subjects,
    exams, topics, quiz history, and the current study plan). Strands Decider 2B selects the
    academic action best suited to that request: assess a topic, create a study plan, record a
    quiz result, replan the remaining sessions, explain an existing recommendation, or ask a
    clarifying question.

    This is a tool-selection pattern: before any tool runs, the decider narrows the agent's
    intent to the one action that matches the student's words and study state.  If confidence
    is below the threshold the agent is sent back to ask for clarification instead of guessing.

Typed questions and options
    action (choice): which academic action fits the request?
        assess  — student asks to be quizzed on a topic
        plan    — student asks for a new study schedule
        record  — student is reporting a quiz score they just got
        replan  — student's circumstances changed (date, availability, new result) and the
                  existing plan needs rebuilding
        explain — student wants to understand their priorities or the reasoning behind a recommendation
        clarify — the request is too vague to act on; the agent should ask a follow-up question

Wiring
    `AcademicActionSelector` is a Strands `InterventionHandler`; agent.py passes it to Agent:
        Agent(..., interventions=[AcademicActionSelector(decider)])

    `before_invocation` resets the guided-call tracker for each new student turn.
    `before_tool_call` builds a state string (conversation + study snapshot), asks the decider,
    and returns Guide (ask for clarification) when confidence is low, or Proceed otherwise.

How to reuse it
    Copy this file, replace ACTIONS with your domain's tool options (one short sentence each),
    and keep the wiring unchanged.  This pattern suits any domain where a request must be
    routed to one of N tools based on natural language and rich context — customer support,
    medical triage, content moderation, HR helpdesks.
"""

from __future__ import annotations

from typing import Any

from strands.interventions import Guide, InterventionHandler, Proceed

from decider_kit import Decider

PATTERN_TAG = "#tool-selection"

# Six academic actions.  Descriptions are the option signal the decider reads — keep them sharp.
ACTIONS: dict[str, str] = {
    "assess":  "The student asks to be quizzed or tested on a topic to check their understanding.",
    "plan":    "The student asks for a study schedule, timetable, or study plan.",
    "record":  "The student is reporting a quiz score, test result, or self-assessment they just completed.",
    "replan":  "The student's situation changed (exam date moved, new exam, time changed) and the plan needs rebuilding.",
    "explain": "The student wants to understand their priorities, why a topic is urgent, or what the recommendation is based on.",
    "clarify": "The request is too vague or ambiguous to act on; ask a clarifying question first.",
}

QUESTIONS: dict[str, dict[str, Any]] = {
    "action": Decider.choice(
        "Which academic action is most suited to the student's request and current study state?",
        ACTIONS,
    ),
}

# Confidence threshold below which the agent asks for clarification instead of acting.
_DEFAULT_CONFIDENCE_THRESHOLD = 0.50


def _render_messages(messages: list[Any], last: int = 8) -> str:
    """Convert Strands message objects to plain text the decider can read."""
    lines: list[str] = []
    for m in messages[-last:]:
        # Strands messages are dicts or objects with .role / .content
        if isinstance(m, dict):
            role = str(m.get("role", "?")).upper()
            content = m.get("content", "")
        else:
            role = str(getattr(m, "role", "?")).upper()
            content = getattr(m, "content", "")
        # content can be a list of blocks or a plain string
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict):
                    parts.append(block.get("text", ""))
                else:
                    parts.append(str(block))
            text = " ".join(p for p in parts if p).strip()
        else:
            text = str(content).strip()
        if text:
            lines.append(f"{role}: {text[:200]}")
    return "\n".join(lines) if lines else "(conversation not started yet)"


class AcademicActionSelector(InterventionHandler):
    """Before every tool call, ask Strands Decider 2B which academic action fits this request."""

    name = "academic-action-selector"

    def __init__(self, decider: Decider, confidence_threshold: float = _DEFAULT_CONFIDENCE_THRESHOLD):
        self.decider = decider
        self.confidence_threshold = confidence_threshold
        self.log: list[dict[str, Any]] = []
        self._guided: set[str] = set()   # tool names guided this turn; reset per invocation

    # -- InterventionHandler hooks ----------------------------------------

    def before_invocation(self, event: Any, **kwargs: Any) -> Any:
        """New student turn: reset the guided-call tracker."""
        self._guided.clear()
        return Proceed()

    def before_tool_call(self, event: Any, **kwargs: Any) -> Any:
        """Ask the decider which action fits; guide or proceed accordingly."""
        tool_name: str = event.tool_use.get("name", "unknown")
        tool_input: dict[str, Any] = event.tool_use.get("input", {})

        state = self._build_state(event)
        answers = self.decider.ask(state, QUESTIONS)
        a = answers["action"]

        rec: dict[str, Any] = {
            "pattern": PATTERN_TAG,
            "action": a.label,
            "action_confidence": round(a.confidence or 0.0, 3),
            "action_probabilities": {k: round(v, 3) for k, v in (a.probabilities or {}).items()},
            "decider_ms": round(self.decider.last_latency_ms or 0),
            "tool_called": tool_name,
        }
        self.log.append(rec)

        conf = a.confidence or 0.0
        if conf < self.confidence_threshold and tool_name not in self._guided:
            self._guided.add(tool_name)
            rec["verdict"] = "clarify"
            return Guide(
                feedback=(
                    "The student's intent is unclear. Ask a short clarifying question before "
                    "calling a tool.  Options: quiz on a topic, build a study plan, record a "
                    "quiz score, replan the schedule, or explain the current recommendation."
                )
            )

        rec["verdict"] = "proceed"
        return Proceed()

    # -- helpers ----------------------------------------------------------

    def _build_state(self, event: Any) -> str:
        """State string for the decider: last few conversation turns + student study snapshot."""
        # Import here to avoid circular import at module level
        from .tools import get_store

        messages = []
        if hasattr(event, "agent") and hasattr(event.agent, "messages"):
            messages = list(event.agent.messages or [])

        conversation = _render_messages(messages)
        student_snapshot = get_store().summary()

        return "\n".join([
            "--- STUDENT CONVERSATION (most recent first) ---",
            conversation,
            "",
            "--- STUDENT STUDY STATE ---",
            student_snapshot,
        ])
