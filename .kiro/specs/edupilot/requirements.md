# EduPilot — Requirements

## Problem

College students preparing for multiple exams face a common bottleneck: they have uneven topic
mastery, different exam dates, and limited study hours, but no fast way to decide *what to
study next*. They either guess, or spend time they don't have working it out manually.

## Solution

EduPilot is an AI study coach that holds a conversation with the student, reads their study
state (subjects, topic strengths, exam dates, quiz history), and picks the right academic
action for each request. Strands Decider 2B makes the routing decision — not arithmetic, not
an LLM reasoning about numbers — so the decision is fast, cheap, and carries a calibrated
confidence the code can branch on.

## Users

College students with:
- two or more subjects with different exam dates,
- uneven topic mastery (some topics strong, some weak),
- a limited weekly study budget (10–30 hours).

## Functional requirements

| # | Requirement |
|---|---|
| FR-1 | Inspect a student's subjects, topic strengths (1–5), exam dates, and quiz history. |
| FR-2 | Assess a topic: present a quiz question and record the student's self-reported score. |
| FR-3 | Generate a study plan: assign topics to sessions, ordered by urgency (weakness × proximity to exam). All scheduling arithmetic is in Python, not in the LLM or decider. |
| FR-4 | Record a quiz result: update topic strength to the reported score; append to quiz history. |
| FR-5 | Replan: rebuild the session schedule after a score change, new exam, or availability change. |
| FR-6 | Explain a recommendation: state which topic is top priority, the supporting evidence (strength, days to exam, urgency rank), and what comes next. |
| FR-7 | Handle low-confidence requests: when the decider is unsure about the right action, guide the agent to ask a clarifying question instead of guessing. |

## Decision requirement

Strands Decider 2B receives a state string containing the recent conversation and the student's
live study snapshot, and answers one question:

> Which academic action is most suited to the student's request and current study state?
> Options: assess, plan, record, replan, explain, clarify.

The decider must read language (what the student meant, whether they are reporting a result or
asking for a plan). It must **not** be asked to calculate urgency scores, compare dates, or
count sessions — those are deterministic Python calculations done before the state is built.

## Non-requirements (MVP scope)

- No database, no external API, no authentication.
- No multi-student support (single synthetic profile for the demo).
- No persistent storage between process restarts.
- No frontend framework beyond the kit's existing demo UI.
