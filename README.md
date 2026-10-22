# EduPilot: AI Academic Decision Agent

**An AI study coach that helps students choose what to study next—by assessing topics, building study plans, recording quiz results, and adapting recommendations in real time.**

An agent on AWS that hands one decision to **Strands Decider 2B** and the conversation to **Amazon Bedrock**. Decision pattern: `#tool-selection`. Tags: `#strands-decider-2b` `#tool-selection`.

- Video: (add the YouTube/Vimeo link)
- Article: (add the AWS Builder Center link)
- Deployed: run `./kit deploy`

## The project

## Use case

- **Pitch:** An AI study coach that helps students choose what to study next—by assessing topics, building study plans, recording quiz results, and adapting recommendations in real time.

- **Who it is for:** College students with multiple subjects, variable topic mastery, uneven exam schedules, and limited study hours who need to optimize their preparation.

- **Example interaction:**
  - Student: "I have an exam on Thermodynamics in 5 days and Electronics in 2 weeks. I'm strong in circuits but weak in heat transfer. What should I study next?"
  - EduPilot: "Quiz on heat transfer first—it's weak and closer. I'll create a 5-day plan. Want to assess heat transfer fundamentals first?"

- **Features:**
  - **Topic assessment:** ask students about their understanding and recent practice; record their answers.
  - **Study plan generation:** build realistic plans based on exam dates, topic strength, and available hours.
  - **Quiz recording:** capture quiz scores and adjust the plan based on results.
  - **Adaptive replanning:** respond to changes (new exam date, topic weakness discovered).
  - **Natural explanations:** why a topic is urgent, what the plan covers, and what comes next.
  - **Live decision panel:** see which academic action the model chose and why.
  - **Deployed on Amazon Bedrock AgentCore Runtime.**

- **The decision handed to Strands Decider 2B:** what academic action should the agent take next—assess, plan, record, replan, explain, or ask for clarification? (`#tool-selection`)

- **Why a decision model:** the agent must pick the right tool for each request, based on the student's words and study state (subjects, exams, quiz history, current plan). Strands Decider 2B reads language and context better than arithmetic, and the decision is fast and private.

- **Amazon Bedrock:** powers the conversation, tool calling, and planning logic. Local Ollama runs during development, hosted LLM through AWS UG Madurai cloud.



## How it is built

Strands Agents with Amazon Bedrock for the generative part, the tools in `agent/tools.py`, deployed to Amazon Bedrock AgentCore Runtime, and one decision handed to Strands Decider 2B at a clear seam in the agent's path.

Amazon Bedrock AgentCore features: AgentCore Memory (summarise strategies) (configured in `agent/features.yaml`, created by `./kit deploy`).

Every Amazon Bedrock model id is set in `.env` (`BEDROCK_MODEL_ID`, and `BEDROCK_SMALL/MEDIUM/LARGE_MODEL_ID` for routing), Amazon Nova by default.



## Reusable decision pattern: academic action selector (#tool-selection)

The pattern lives in [`agent/decision.py`](agent/decision.py), labelled `REUSABLE DECISION PATTERN`. It contains the typed questions and their options, the wiring that puts the decision in the agent's path, and a note on how to reuse it:

```text
REUSABLE DECISION PATTERN: academic action selector (#tool-selection)

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
```

Typed questions:

```python
QUESTIONS: dict[str, dict[str, Any]] = {
    "action": Decider.choice(
        "Which academic action is most suited to the student's request and current study state?",
        ACTIONS,
    ),
}
```

## Measured

Decider: strands-decider-2b-hobson-v19 (ugmdu). 18 labelled cases, 18 decisions.

| | Strands Decider 2B | qwen3.5-4b |
|---|---|---|
| Accuracy | 100.0% | 100.0% |
| Latency p50 per decision | 2438 ms | 14546 ms |
| Latency p95 | 3803 ms | 29862 ms |
| Cost per 1,000 decisions | $0.0350 | $0.0000 |
| Answered alone at confidence >= 0.7 | 83% | 100% |
| Accuracy when confident | 100.0% | 100.0% |

At the median the decider was 6.0x faster than the LLM.

Reproduce with `./kit bench` (cases in `agent/eval_cases.jsonl`; charts in `submission/bench/`).

## Run it

```bash
./kit setup        # checks your machine and AWS, sets up Strands Decider 2B (local model or hosted API)
./kit demo         # web UI at http://localhost:8501
./kit bench        # the decision vs an Amazon Bedrock LLM
./kit deploy       # Amazon Bedrock AgentCore Runtime
```

Requirements: Python 3.10+, AWS credentials with Amazon Bedrock access, and for deploying, Node 20+ with the AgentCore CLI (`./kit agentcore-cli`).

## Credits

Built with the AWS User Group Madurai Strands Decider hackathon kit (https://github.com/awsugmdu). The kit's reusable library (`decider_kit/`, the demo UI, the video and article tooling, and the Kiro steering, skills and hooks) is the user group's; the agent in `agent/` is mine. Strands Decider: https://github.com/strands-labs/strands-decider (Apache-2.0).

Licence: Apache-2.0 (see LICENSE).
