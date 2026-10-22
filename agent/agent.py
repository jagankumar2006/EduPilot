"""EduPilot: AI Academic Decision Agent for College Students

Strands Agents SDK + Strands Decider 2B (#tool-selection).

The decider picks the right academic action (assess / plan / record / replan / explain)
before each tool call.  The LLM handles conversation and tool arguments.  The synthetic
student profile in tools.py means the demo runs anywhere with no external services.

    from agent.agent import HackathonAgent
    out = HackathonAgent().chat("I have Thermodynamics in 5 days. What should I study first?")
    out["reply"], out["decisions"]
"""

from __future__ import annotations

import os
import time
from typing import Any

from strands import Agent

from decider_kit import Decider
from decider_kit.llm import agent_model, default_model_id, image_blocks, strip_thinking

from .decision import AcademicActionSelector
from .tools import TOOLS, get_store

NAME = "EduPilot: AI Academic Decision Agent"


def _system_prompt(eager: bool) -> str:
    """Build the system prompt with the live student profile so dates are always accurate."""
    profile = get_store().summary()

    if eager:
        return (
            "You are EduPilot, an AI study coach for college students.\n"
            "Act immediately: assess, plan, record, replan, or explain without asking first.\n\n"
            "Use student_id='S001' for all tool calls.\n\n"
            f"{profile}"
        )

    return (
        "You are EduPilot, an AI study coach for college students.\n"
        "Help the student decide what to study next.\n\n"
        "You can:\n"
        "  • get_student_profile — inspect subjects, topic strengths, and exam dates\n"
        "  • assess_topic        — quiz the student on a specific topic\n"
        "  • create_study_plan   — build a prioritised study schedule\n"
        "  • record_quiz_result  — record a quiz score and update mastery\n"
        "  • replan_study        — rebuild the plan after a score change or date change\n"
        "  • explain_recommendation — explain why a topic is the top priority\n\n"
        "Rules:\n"
        "  - Always use student_id='S001' when calling tools.\n"
        "  - Never invent exam dates, topic strengths, or quiz scores.\n"
        "  - If the student's intent is unclear, ask one focused clarifying question.\n"
        "  - After recording a quiz result, offer to replan if the score changed the ranking.\n"
        "  - Be concise and explain your reasoning.\n\n"
        f"{profile}"
    )


class HackathonAgent:
    """One Strands agent per session, with the academic-action selector wired in."""

    def __init__(
        self,
        decider: Decider | None = None,
        model_id: str | None = None,
        eager: bool | None = None,
    ) -> None:
        self.decider = decider or Decider()
        self.eager = eager if eager is not None else os.environ.get("DEMO_EAGER") == "1"
        self.model_id = model_id or default_model_id()
        self.sessions: dict[str, tuple[Agent, AcademicActionSelector]] = {}

    def _session(self, session_id: str) -> tuple[Agent, AcademicActionSelector]:
        if session_id not in self.sessions:
            selector = AcademicActionSelector(self.decider)
            agent = Agent(
                model=agent_model(self.model_id),
                system_prompt=_system_prompt(self.eager),
                tools=TOOLS,
                interventions=[selector],
                callback_handler=None,
            )
            self.sessions[session_id] = (agent, selector)
        return self.sessions[session_id]

    def chat(
        self,
        message: str,
        session_id: str = "default",
        images: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Send one message; return reply, decisions, model_id, and latency_ms."""
        agent, selector = self._session(session_id)
        before = len(selector.log)
        t0 = time.perf_counter()
        result = agent(
            [*image_blocks(images), {"text": message}] if images else message,
            invocation_state={"images": list(images or [])},
        )
        reply = strip_thinking(str(result))
        return {
            "reply": reply,
            "decisions": selector.log[before:],
            "model_id": self.model_id,
            "latency_ms": round((time.perf_counter() - t0) * 1000),
            "agent": NAME,
            "eager": self.eager,
        }


if __name__ == "__main__":
    import json
    import sys

    a = HackathonAgent()
    for msg in sys.argv[1:] or [
        "I have Thermodynamics in 5 days. What should I study first?",
        "Okay, assess me on heat transfer.",
    ]:
        print(json.dumps(a.chat(msg), indent=1))
