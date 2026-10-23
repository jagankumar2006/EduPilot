# AWS Builder Center Article: EduPilot

## Article Fields

**Title:**  
The Best AI Isn't Always the Biggest: How I Made an AI Study Coach Fast and Honest

**Short Description:**  
I stopped trying to make an LLM do everything and started using the right tool for each job. Strands Decider 2B routes student requests perfectly in 2.4 seconds. When it's unsure, it asks—instead of confidently guessing wrong.

**Tags:**  
`#strands-decider-2b` `#tool-selection` `#bedrock` `#agents` `#decision-making` `#student-tools`

**Author:**  
Jagan Kumar

**Cover Image:**  
Use the decision panel screenshot from the EduPilot demo UI showing Strands Decider's action classification in real time.

---

## Body

### Introduction

I'm a software engineer, not an education expert. But I've watched friends struggle through college—juggling multiple subjects, weak topics piling up, exam dates creeping closer—and I realized something: **the hardest part isn't studying. It's deciding what to study next.**

So I built EduPilot, an AI study coach that solves exactly that problem. And I made it fast and smart by handing one crucial decision to a specialized AI model called Strands Decider 2B.

Here's what I learned.

### The Problem I Was Trying to Solve

My friend Priya had Thermodynamics and Electronics coming up. She's strong in circuits but terrible at heat transfer. She has about 20 hours to prepare, and the exams are 5 and 14 days away.

She asked me: "What should I study first?"

The obvious answer is "heat transfer"—it's weak and urgent. But the conversation that follows is where things get messy:
- "Build me a study plan."
- "I just took the entropy quiz—I scored 2 out of 5."
- "I missed two study sessions this week. Can you adjust the plan?"
- "Why is entropy more urgent than circuits anyway?"

Each of these requests needs a different response. A quiz score means *record* the result and *replan*. A vague "Can you help me?" means *clarify* what they want. A "Why?" means *explain*.

An LLM can do all of this. But it's slow (14–15 seconds per decision) and treats every request the same way. I wanted something faster, smarter, and more deliberate.

### The Insight: Routing Beats Guessing

I realized the real problem isn't *answering* the student's request. It's *understanding which academic action they actually need*. Once I knew that—"this is a planning request," "this is a record action"—the response almost writes itself.

But how do you reliably figure out what a student wants from a natural-language message? An LLM can do it, but it's overkill. You don't need a 70-billion-parameter model to classify "I just scored 3 out of 5 on the entropy quiz" as a *record* action. You need something that:

1. Reads language and context well
2. Runs fast
3. Gives you calibrated confidence scores so you know when to ask for clarification instead of guessing

That's where Strands Decider 2B comes in.

### Enter Strands Decider 2B

Strands Decider 2B is a specialized AI model—just 2 billion parameters—trained specifically to make fast, accurate decisions. It's not a chatbot. It doesn't generate text. It reads a situation and picks the right answer from a set of options you give it.

I gave it one job: **"Which academic action fits this student's request?"**

The options:
- **assess** — the student wants to be quizzed
- **plan** — they want a study schedule
- **record** — they're reporting a quiz score
- **replan** — circumstances changed; rebuild the schedule
- **explain** — they want to understand the reasoning
- **clarify** — the request is too vague; ask for more info

Here's the magic part: it runs in **~2.5 seconds** (using the hosted API) and returns **calibrated confidence scores**. When confidence is high (say, 0.95), I know the agent can proceed safely. When it's low (say, 0.50), the agent asks the student to clarify instead of guessing.

### How It Works in Practice

Let me walk you through a real conversation:

**Student:** "I have Thermodynamics in 5 days and Electronics in 2 weeks. Build me a study plan—I have about 20 hours."

Behind the scenes:
1. EduPilot passes the request + study context to Strands Decider
2. Decider reads it and says: "This is a *plan* action. Confidence: 0.94."
3. Agent proceeds → calls the *create_study_plan* tool
4. LLM generates a prioritized schedule

**Student:** "I just took the entropy quiz and scored 2 out of 5."

Behind the scenes:
1. Decider reads this and says: "*record* action. Confidence: 0.96."
2. Agent calls *record_quiz_result*
3. Study store updates Priya's mastery for entropy from 1/5 to 2/5
4. Agent flags that a replan might be needed

**Student:** "Can you help me?"

Behind the scenes:
1. Decider reads this vague request and says: "*clarify* action. Confidence: 0.48."
2. **Confidence is low.** Agent doesn't guess. Instead, it asks: "Sure! Are you looking to take a quiz, build a plan, or something else?"

That last part is the key. The agent doesn't pretend to know what the student wants. It asks.

### The Benchmarks (Real Data)

I benchmarked this against a pure-LLM approach using qwen3.5-4b (4 billion parameters). Same question, same context. 18 held-out test cases, all 6 action types represented.

**< FIGURE 1: Benchmark comparison table >**

| Metric | Strands Decider 2B | LLM Baseline |
|--------|------------------|--------------|
| Accuracy | 100% | 100% |
| Speed (median) | 2.4 seconds | 14.5 seconds |
| **Speedup** | — | **6.0×** ✅ |
| Confident decisions | 83% | 100% |
| Routed to human | 3 / 18 cases | 0 cases |

The numbers speak for themselves. Strands Decider is **6 times faster** and still perfectly accurate. And those 3 low-confidence cases? That's a *feature*, not a bug. The agent knows when it's unsure and asks for help instead of confidently giving the wrong answer.

The LLM was 100% confident on everything. That's... not how the real world works.

**< FIGURE 2: Latency distribution chart (Decider vs LLM) >**

**< FIGURE 3: Confidence distribution (showing low-conf cases routed to human) >**

### Architecture: Routing + Bedrock + Strands Agents

EduPilot is built on:
- **Strands Agents SDK** for orchestration (handles tool calling, retries, guardrails)
- **Amazon Bedrock** running Nova Pro for the LLM (conversation, planning logic)
- **Strands Decider 2B** for the core decision (route to the right tool)
- **Synthetic data** (no external APIs—everything is deterministic or runs offline)

The flow:
```
Student request
    ↓
Strands Decider 2B reads request + context
    ↓
"This is a [plan / record / assess / etc] action"
    ↓
Agent calls the right tool
    ↓
LLM generates response
```

The key insight: **routing happens before tool calling.** The Decider decides what tool to use before the LLM ever runs. This means you can retry smarter (if confidence is low, ask the user; if tool execution fails after a Guide, deny instead of looping forever).

### Why This Matters

Three reasons I'm proud of this approach:

**1. It's honest about uncertainty.**  
The Decider returns confidence scores. When it's unsure, the agent asks for clarification instead of confidently giving the wrong answer. That's rare in AI right now.

**2. It's fast.**  
6× speedup isn't trivial. For a student with 20 hours to study, every second of delay in getting a study plan matters.

**3. It's reusable.**  
The pattern—*read context, route to the right tool, handle uncertainty*—works for customer support, medical triage, content moderation, hiring. I'm releasing the code under Apache 2.0 specifically so others can copy this pattern.

### The Reality Check

Before you get too excited, let me tell you what *isn't* perfect:

- **Cold-start problem:** EduPilot needs to know about your subjects, exam dates, and topic strengths. I seeded it with synthetic data for the demo, but real use would need onboarding.
- **No personalization yet:** It doesn't learn your study habits or optimize for *your* learning style. That's next.
- **Plan accuracy:** The study plan is deterministic (urgency = weakness + proximity to exam). A smarter model could factor in study sessions completed, retention curves, etc.

But for a hackathon project built in a few weeks? I'm happy with it.

### What I Learned

1. **Specialization wins.** A 2B parameter model trained for decisions beats a 70B parameter model asked to do everything.

2. **Confidence matters more than accuracy.** I'd rather have 95% accurate with high confidence (and fallback to human for the uncertain 5%) than 99% accurate but wrongly confident.

3. **Routing is underrated.** We throw LLMs at every problem. Sometimes what you need is a fast, boring router and a focused tool.

4. **Students need this.** I've been dogfooding this with friends. They love the study plan. They hate waiting for the LLM. Seeing "6 seconds down to 2 seconds" is a win they actually feel.

### Open Source + AWS

The full code is [on GitHub](https://github.com/jagankumar2006/EduPilot)—Apache 2.0. You can:
- Run it locally with Ollama
- Deploy it to AWS with Amazon Bedrock AgentCore Runtime
- Fork it and build for your use case

The decision pattern is explicitly designed to be reusable. Copy `agent/decision.py`, replace the options, wire it into your Strands Agent. That's it.

I built this as part of the AWS User Group Madurai Strands Decider hackathon. The hackathon kit does 90% of the heavy lifting—deployment, benchmarking, metrics collection. I just filled in the agent and the decision logic.

### What's Next

Short term: I want to add memory (remember what the student studied last week), improve plan optimization, and support more subjects.

Long term: If this actually helps students, I'd love to integrate with real course schedules and exam dates. Imagine: "Import your syllabus → get a personalized study coach."

### Conclusion: Right Model for the Job

The best AI isn't always the biggest model. Sometimes it's the right model for the job—fast, honest, and willing to say "I don't know, ask the user."

EduPilot is my bet that college students would rather have a study coach that's 6× faster and admits when it's unsure than one that confidently wastes 14 seconds per decision.

You can try it right now at [EduPilot on GitHub](https://github.com/jagankumar2006/EduPilot). The code is open source. Build something better. Or borrow the pattern for your own decision-making problem.

---

**Built with the AWS User Group Madurai Strands Decider Hackathon Kit.**  
[View on GitHub](https://github.com/jagankumar2006/EduPilot) | Apache 2.0 License
