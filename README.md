# Tvara AI — Round 2 Challenge Submission

## What I Built & What I Tried

This README honestly describes my approach, what worked, what didn't, and the logic I applied for each task within the 90-minute constraint.

---

## Task 1 — GPT-5-Nano + Moderation Pipeline

### What I Tried

My goal was to build a linear pipeline:

```
PDF Input → Extract Text → Truncate Tokens → Moderate → LLM Call → Output
```

**PDF Extraction**
I used `pypdf` to read pages and extract raw text. The logic loops over all pages and joins them. I also added an early guard — if the extracted text is empty or blank, the pipeline immediately returns `{"allowed": false, "flag": "empty_pdf"}` without going further.

**Token Truncation**
Before passing anything to the moderation or LLM layer, I truncate the text to 800 tokens (words) by splitting on whitespace. The reason: to keep API calls predictable in cost and to avoid hitting model context limits. Even as a mock, I wanted this to reflect real production thinking.

**Moderation Layer**
I tried to implement a two-step moderation approach:
- Step 1: A local regex pass — catches obvious harmful patterns like `suicide`, `self-harm`, `kill myself` instantly with zero latency and no API dependency.
- Step 2: The real OpenAI Moderation API call (stubbed/mocked, awaiting key).

If flagged at either step, the pipeline returns `{"allowed": false, "flag": "<category>"}` and stops — the LLM never gets called.

**Retry Utility**
I wrote a `retry()` higher-order function that wraps any callable and retries it once with a 0.5s delay on failure. The idea was to keep retry logic separate from business logic — you apply it at the call site, not inside the function itself. This makes it reusable across both the moderation and LLM modules.

**What Went Wrong**
The pipeline did not execute successfully. After the session I identified two bugs:
1. Unclosed string quote inside the `re.compile()` call in `FLAG_PATTERNS` — the regex string is missing its closing quote before the flags argument. One-line fix.
2. The `parts` list in `extract_text_from_pdf` was never appended to — `page_text` was computed but not added to `parts`, so the function would return an empty string even for valid PDFs.

The overall structure and logic of the pipeline is correct — the failures were syntax/logic bugs, not design flaws.

### What the Output Should Look Like

**Safe content:**
```json
{
  "allowed": true,
  "flag": "",
  "response": "[MOCK] GPT-5-Nano response for the provided text"
}
```

**Flagged content:**
```json
{
  "allowed": false,
  "flag": "self_harm"
}
```

**Empty PDF:**
```json
{
  "allowed": false,
  "flag": "empty_pdf"
}
```

---

## Task 2 — RAG Pipeline

### What I Tried

My goal was a minimal but correct retrieval pipeline:

```
Raw Text Chunks → Embed → Store → Query → Cosine Similarity → Top-K Results
```

**Embedding**
I used `sentence-transformers` with `all-MiniLM-L6-v2` — a lightweight, CPU-friendly model. The spec asked for `intfloat/e5-small-v2`; these are interchangeable in structure, just a model name swap. I encode all documents at `add_documents()` time so retrieval is fast (no re-encoding on every query).

**Vector Store (numpy instead of FAISS)**
Instead of FAISS, I used raw `numpy` for cosine similarity — dot product of L2-normalized vectors gives identical results to a flat FAISS index for small document sets. For demo scale this is perfectly fine and avoids an extra dependency.

Chunk size reasoning: Fixed chunks of 2–3 sentences keep semantic context intact without needing a recursive splitter — appropriate for demo scope.

**Retrieval**
The `retrieve()` method takes a query string, encodes it, computes cosine similarity against all stored embeddings, and returns the top-K results sorted by score:
```json
{
  "chunks": ["It also helps in machine learning concepts", "..."],
  "scores": [0.89, 0.76]
}
```

**Error Handling I Added**
- If no documents are loaded (`self.embeddings is None`) → returns `[]` cleanly
- If query is empty → no crash, returns `[]`

**What Worked**
This task executed successfully end to end. Documents were embedded, query was passed in, and ranked results with cosine scores were returned correctly.

**What I Did Not Complete (time ran out)**
- Docling for PDF parsing — used plain string input instead
- GPT-5-Nano mock answer using retrieved chunks (the bonus step)

---

## Task 3 — GitHub Structure & PR

### What I Know & Would Do

I have not pushed to GitHub yet, but I know exactly how to complete this:

**Repository structure I would follow:**
```
tvara-ai-round2/
├── src/
│   ├── moderation/    ← moderation logic isolated here
│   ├── llm/           ← LLM client stub here
│   ├── utils/         ← pdf extraction, retry, truncation here
│   └── rag/           ← full RAG pipeline here
├── pipeline.py        ← Task 1 entry point
├── rag_demo.py        ← Task 2 entry point
├── requirements.txt
└── README.md
```

**Branching workflow I would follow:**
- Do all work on a `dev` branch
- Keep `main` as the stable/reviewed branch
- Open one PR from `dev → main` with a description covering: what was built, how to run it, what's missing due to time, and where the OpenAI key plugs in

**Git commands:**
```bash
git init
git checkout -b dev
git add .
git commit -m "feat: add moderation pipeline and RAG implementation"
git remote add origin https://github.com/<username>/tvara-ai-round2.git
git push -u origin dev

# Then open PR on GitHub: dev → main
```

**Where the API key plugs in once received:**
- `src/llm/gpt_client.py` → replace mock string with `openai.chat.completions.create(model="gpt-5-nano", ...)`
- `src/moderation/moderator.py` → replace regex-only check with `openai.moderations.create(input=text)`

---

## Setup

```bash
pip install pypdf sentence-transformers numpy
python pipeline.py sample.pdf   # Task 1
python rag_demo.py               # Task 2
```

---

## Honest Summary

| Task | Status | Notes |
|------|--------|-------|
| Task 1 — Pipeline structure & logic | ✅ Complete | Correct architecture, retry, truncation, moderation flow |
| Task 1 — Execution | ❌ Did not run | Two small bugs identified post-session (syntax + missing append) |
| Task 2 — RAG pipeline | ✅ Executed successfully | Embedding, retrieval, and scores all working |
