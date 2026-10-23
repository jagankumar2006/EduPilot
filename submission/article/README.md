# EduPilot Article Files — Ready for Publishing

This folder contains your AWS Builder Center article. It's ready to publish now.

---

## Files in This Folder

| File | Purpose | Status |
|------|---------|--------|
| **blog.md** | Full article, human-friendly tone | ✅ Ready to read |
| **fields.md** | Structured article for AWS Builder Center (title, tags, body) | ✅ Ready to submit |
| **figures.md** | Figure placeholders and how to generate them | ✅ Reference guide |
| **README.md** | This file | — |

---

## How to Publish

### Step 1: Read & Polish
1. Open `blog.md`
2. This is your full article in readable form
3. Make any edits you want (tone, examples, emphasis)

### Step 2: Generate Figures
1. Read `figures.md` for what images you need
2. Run the Python scripts (provided in figures.md) to generate PNGs
3. Save them to a `figures/` subfolder

### Step 3: Submit to AWS Builder Center

AWS Builder Center submission form:

**Title:**  
Copy from `fields.md` → "How I Built a 6× Faster AI Study Coach Using Strands Decider 2B"

**Description:**  
Copy from `fields.md` → "Learn how I used Strands Decider 2B to route student requests..."

**Tags:**  
Copy from `fields.md` → `#strands-decider-2b` `#tool-selection` `#bedrock` etc.

**Body:**  
Copy the body section from `fields.md` (everything from "### Introduction" onward)

**Figures:**  
- Where it says `< FIGURE 1: ... >`, upload the corresponding image
- AWS will handle sizing and formatting

**Author:**  
Your name (Jagan Kumar)

**Cover Image:**  
Use a screenshot from the demo UI or create a simple graphic showing "Strands Decider 2B" and "6× Faster"

---

## Article Highlights

**What makes this article stand out:**

1. **Honest tone** — not overstated, includes limitations
2. **Real numbers** — all from `submission/bench/results.json`, not invented
3. **Clear problem statement** — "students need to decide what to study next"
4. **Specific solution** — "I used Strands Decider 2B to route the request"
5. **Benchmarks** — 100% accuracy, 6× speedup, compared to LLM baseline
6. **Code is public** — readers can fork and use immediately
7. **Reusable pattern** — shows how to apply this to other problems

---

## Quick Facts to Highlight

**In casual conversation or social media:**

- "Built an AI study coach using Strands Decider 2B"
- "6× faster than asking an LLM every time"
- "100% accurate on student request routing"
- "Open source, Apache 2.0"
- "Perfect for: customer support, medical triage, hiring, any routing problem"

---

## Timeline

- **Now:** Read and polish the article
- **When ready:** Generate figures (Python scripts provided)
- **Then:** Submit to AWS Builder Center
- **Deadline:** October 23, 2026, 11:59 p.m. PT

---

## Figures You'll Need

These are referenced in `fields.md`:

1. **FIGURE 1:** Benchmark comparison table (accuracy, speed, routing)
2. **FIGURE 2:** Latency distribution (Decider vs LLM box plot)
3. **FIGURE 3:** Confidence distribution (per-action confidence scores)
4. **FIGURE 4 (optional):** EduPilot UI screenshot
5. **FIGURE 5 (optional):** Architecture diagram
6. **FIGURE 6 (optional):** Real conversation example

Scripts to generate these are in `figures.md`. Python + matplotlib only.

---

## Real Data Sources

All numbers come from:
- `../bench/results.json` — 18 test cases, 100% accuracy, real latencies
- `../bench/results.md` — summary table
- `../bench/bench-*.png` — existing charts (can reuse)

No invented numbers. No "estimated." All measured.

---

## What Reviewers Will Look For

✅ **Strands Decider 2B is the core decision** — not a side feature  
✅ **Real benchmarks** — compared against baseline, held-out test set  
✅ **Honest assessment** — includes limitations, not hype  
✅ **Reusable pattern** — code is public, documented, copy-able  
✅ **Amazon Bedrock integration** — shows real use of AWS services  
✅ **Clear problem statement** — "why this matters" is obvious  

---

## Support

**Need help with:**
- **Article content?** Edit `blog.md` directly
- **Figures?** See `figures.md` for code and tools
- **Submission format?** Use `fields.md` as your template
- **Benchmarks?** See `../bench/results.json`

---

## Next: Video

Once article is submitted, record a demo video:

```bash
./kit video --target agentcore
```

This creates `submission/video/demo.mp4`. Upload to YouTube as public.

---

## Final Checklist

- [x] Article written (human-friendly tone)
- [x] Benchmarks real and cited
- [x] Figures documented (with Python code)
- [ ] Figures generated and saved
- [ ] Article submitted to AWS Builder Center
- [ ] Video recorded and uploaded
- [ ] Links added to `submission/SUBMISSION.md`

---

## Published?

Once your article is live on AWS Builder Center, add the link here and to `submission/SUBMISSION.md`:

```
Article URL: https://builder.aws.com/...
Submitted: October 22, 2026
Published: [date]
```

---

**Built with the AWS User Group Madurai Strands Decider Hackathon Kit**  
Apache 2.0 | [GitHub](https://github.com/jagankumar2006/EduPilot)
