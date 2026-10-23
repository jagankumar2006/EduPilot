# EduPilot Article — Figure Placeholders

When publishing to AWS Builder Center, replace these placeholders with actual images/charts.

---

## FIGURE 1: Benchmark Comparison Table

**Description:** Side-by-side comparison of Strands Decider 2B vs LLM baseline

**What to include:**
- Accuracy: 100% vs 100%
- Speed (median): 2.4s vs 14.5s with 6.0× speedup highlighted
- Confident decisions: 83% vs 100%
- Human escalation: 3/18 vs 0/18

**Source:** `submission/bench/results.md`

**Recommendation:** Screenshot or export from `submission/bench/results.json` as a clean table.

---

## FIGURE 2: Latency Distribution Chart

**Description:** Box plot or histogram showing latency distribution

**What to show:**
- Strands Decider 2B: median 2.4s, p95 3.8s (tight distribution)
- LLM baseline: median 14.5s, p95 29.9s (wide distribution)
- Highlight the 6× speedup

**Source:** `submission/bench/results.json` → `decider_ms` and `llm_ms` arrays

**Tools:** Use matplotlib (included in requirements.txt):
```python
import json
import matplotlib.pyplot as plt

with open('submission/bench/results.json') as f:
    data = json.load(f)

decider_latencies = [r['decider_ms'] for r in data['rows']]
llm_latencies = [r['llm_ms'] for r in data['rows']]

plt.figure(figsize=(10, 6))
plt.boxplot([decider_latencies, llm_latencies], labels=['Strands Decider 2B', 'LLM Baseline'])
plt.ylabel('Latency (ms)')
plt.title('Decision Latency Comparison')
plt.grid(True, alpha=0.3)
plt.savefig('latency-comparison.png', dpi=150, bbox_inches='tight')
```

---

## FIGURE 3: Confidence Distribution

**Description:** Histogram or chart showing confidence scores per action type

**What to show:**
- Which actions have high confidence (assess, plan, record)
- Which have lower confidence (replan, clarify)
- Highlight the 3 cases routed to human (confidence < 0.7)

**Source:** `submission/bench/results.json` → per-action confidence scores

**Tools:**
```python
import json
import matplotlib.pyplot as plt

with open('submission/bench/results.json') as f:
    data = json.load(f)

actions = {}
for row in data['rows']:
    action = row['expected']['action']
    confidence = row['decider']['action']['confidence']
    if action not in actions:
        actions[action] = []
    actions[action].append(confidence)

plt.figure(figsize=(10, 6))
for action, confs in sorted(actions.items()):
    plt.scatter([action] * len(confs), confs, alpha=0.6, s=100)

plt.axhline(y=0.7, color='r', linestyle='--', label='Threshold (route to human if <0.7)')
plt.ylabel('Confidence')
plt.xlabel('Action Type')
plt.title('Strands Decider 2B Confidence by Action')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('confidence-distribution.png', dpi=150, bbox_inches='tight')
```

---

## FIGURE 4 (Optional): EduPilot UI Screenshot

**Description:** Demo UI showing the decision panel in action

**What to capture:**
1. Open http://localhost:8501 (if demo is still running)
2. Paste a prompt like "I have Thermodynamics in 5 days. What should I study first?"
3. Screenshot showing:
   - Student message on the left
   - Agent response
   - **Decision panel on the right** showing action, confidence, latency, verdict

**File:** Save as `edupilot-ui.png`

---

## FIGURE 5 (Optional): Architecture Diagram

**Description:** Visual showing the flow: Student Request → Decider → Tool → LLM → Response

**Tools:** Use Mermaid or simple draw:
```
┌──────────────────────┐
│  Student Request     │
│  (natural language)  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│ Strands Decider 2B       │
│ "Which action?"          │
│ Confidence score returned │
└──────────┬───────────────┘
           │
           ├─ High confidence → Proceed
           └─ Low confidence  → Ask for clarification
                    │
                    ▼
         ┌──────────────────┐
         │ Execute Tool     │
         │ (assess/plan/    │
         │  record/replan/  │
         │  explain)        │
         └─────────┬────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ Amazon Bedrock   │
         │ (LLM generation) │
         │ Nova Pro         │
         └─────────┬────────┘
                   │
                   ▼
         ┌──────────────────┐
         │ Natural response │
         │ to student       │
         └──────────────────┘
```

**Tool:** https://mermaid.live/ (free, online)

---

## FIGURE 6 (Optional): Real Conversation Example

**Description:** Annotated screenshot or diagram showing the 4-turn demo conversation with decisions

**Turns:**
1. "I have Thermodynamics in 5 days... Build me a study plan"
   - Decision: *plan* (0.94 confidence)
2. "I just took the entropy quiz and scored 2 out of 5"
   - Decision: *record* (0.96 confidence)
3. "I missed two study sessions this week. Can you adjust?"
   - Decision: *replan* (0.69 confidence, borderline)
4. "Can you help me?"
   - Decision: *clarify* (0.49 confidence, routed to human)

**Recommendation:** Format as a table or conversational flow.

---

## How to Generate Figures Programmatically

All charts can be generated from `submission/bench/results.json`:

```bash
# From the submission/article directory:
python3 << 'EOF'
import json
import matplotlib.pyplot as plt
import numpy as np

with open('../bench/results.json') as f:
    data = json.load(f)

# Create all figures
# (use code snippets above)
EOF
```

---

## When Publishing

1. **Save all PNGs** to `submission/article/figures/`
2. **In fields.md,** replace `< FIGURE N: ... >` with the actual image filename
3. **AWS Builder Center** will host the images; they provide upload UI

---

## Alternative: Link to Live Data

If you prefer, you can link to:
- **GitHub raw files:** https://github.com/jagankumar2006/EduPilot/raw/main/submission/bench/results.json
- **Live demo:** http://localhost:8501 (won't work for public readers, but shows the idea)

AWS Builder Center recommends uploading images directly for best rendering.
