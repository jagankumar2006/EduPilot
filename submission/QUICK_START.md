# EduPilot — Quick Start (Local)

## What You Have

✅ **Fully built AI agent** that decides which academic action a student needs  
✅ **Strands Decider 2B integration** making the decision at the core  
✅ **Real benchmarks:** 100% accuracy, 6× faster than LLM baseline  
✅ **69 passing tests**  
✅ **Web UI** running at http://localhost:8501  
✅ **GitHub repo:** public, Apache-2.0  

---

## Try It Right Now

### Option 1: Web UI (Visual)
Open your browser: **http://localhost:8501**

You'll see:
- Chat with EduPilot on the left
- Live decision panel on the right (see what Strands Decider chose)

**Example prompts:**
```
I have Thermodynamics in 5 days. What should I study first?

I just scored 3/5 on the entropy quiz. Record that.

I missed two study sessions. Can you adjust my plan?

Can you help me?
```

### Option 2: Terminal
```bash
python -c "
from agent.agent import HackathonAgent
a = HackathonAgent(eager=True)
r = a.chat('I have Thermodynamics in 5 days. What should I study first?')
print('Agent reply:')
print(r['reply'])
print()
print('Decision made:', r['decisions'][0]['verdict']['action']['label'])
print('Confidence:', r['decisions'][0]['verdict']['action']['confidence'])
"
```

---

## What Strands Decider 2B Does

Before the agent calls any tool, it reads:
- **The student's request** (natural language)
- **The study context** (subjects, exams, quiz history, current plan)

Then it picks **one of 6 actions:**

| Action | When | Example |
|--------|------|---------|
| assess | "Quiz me" | "Can you test me on thermodynamics?" |
| plan | "Make a schedule" | "Build me a study plan" |
| record | "I got a score" | "I scored 3/5 on entropy" |
| replan | "Things changed" | "I missed two sessions" |
| explain | "Why this?" | "Why is this urgent?" |
| clarify | "Not clear" | "Can you help me?" ← Low confidence |

**When confidence is low (<0.7),** the agent asks the student instead of guessing.

**Result:** Fast, safe, calibrated decisions. 6× speedup vs asking the LLM every time.

---

## The Numbers

**Test accuracy:** 18 held-out eval cases  
- Decider: **100%** ✅
- LLM baseline: **100%** (for comparison)

**Speed:** Median latency per decision
- Decider: **2,438 ms**
- LLM: **14,546 ms**
- **Speedup: 6.0×** 🚀

**Confidence:** When to route to human
- 15/18 cases (83%) decided alone
- 3/18 cases (<0.7 confidence) flagged for human review ← **Safe fallback**

---

## Files You Need

| File | Purpose |
|------|---------|
| `agent/agent.py` | Main agent class (HackathonAgent) |
| `agent/decision.py` | **Reusable decision pattern** for tool selection |
| `agent/tools.py` | The 6 academic tools |
| `agent/eval_cases.jsonl` | 36 labeled test cases |
| `submission/bench/results.json` | Raw benchmark data |
| `submission/DEPLOYMENT.md` | How to deploy (local + AWS) |
| `submission/SUBMISSION.md` | Full submission details |

---

## Next Steps for Submission

1. **Record video** (when network is stable):
   ```bash
   ./kit video --target agentcore
   ```
   Upload to YouTube/Vimeo as public.

2. **Write article** on AWS Builder Center:
   ```bash
   ./kit article
   ```
   Use the generated markdown in `submission/article/`.

3. **Add links** to `submission/SUBMISSION.md`:
   - Video URL
   - Article URL

4. **Deploy to AWS** (when network allows):
   ```bash
   ./kit aws-login
   ./kit deploy
   ```

5. **Submit** on AWS Builder Center by October 23, 2026, 11:59 p.m. PT

---

## Deployment Paths

### Path A: Local (Now) ✅
```bash
./kit demo-bg
# http://localhost:8501
```
**Status:** Working

### Path B: AWS (When Network Allows)
```bash
./kit deploy
./kit invoke "I have Thermodynamics in 5 days..."
```
**Status:** Configuration ready; network blocked npm install

---

## How to Read the Decision Pattern

Open [`agent/decision.py`](../agent/decision.py).

Look for:
- `PATTERN_TAG = "#tool-selection"` — the pattern type
- `QUESTIONS` — the typed questions the decider answers
- `AcademicActionSelector` — the wiring into the Strands Agent
- Docstring starting with `REUSABLE DECISION PATTERN:` — how to copy and adapt it

This pattern can be reused for any domain that needs to route a request to one of N tools based on natural language + rich context.

---

## Key Points for Judges

1. **Strands Decider 2B is the core decision maker** — every tool call goes through it first.
2. **It works:** 100% accuracy, 6× faster than LLM baseline.
3. **It's safe:** Low-confidence cases go to human, not guessed.
4. **It's reusable:** Copy `decision.py` for similar problems.
5. **It's honest:** All numbers come from real benchmarks, not invented.
6. **Built with the kit:** AWS UG Madurai provided the framework and library.

---

## Questions?

- **Local setup issue?** See [`submission/DEPLOYMENT.md`](DEPLOYMENT.md)
- **How the decision works?** See [`agent/decision.py`](../agent/decision.py)
- **Benchmark details?** See [`submission/bench/results.json`](bench/results.json)
- **Code quality?** Run `./kit test` (69/69 pass)

---

## Built with the AWS User Group Madurai Strands Decider Hackathon Kit

License: Apache-2.0  
Repo: https://github.com/jagankumar2006/EduPilot
