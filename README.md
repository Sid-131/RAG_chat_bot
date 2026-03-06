# RAG-Based Mutual Fund FAQ Chatbot

> Factual Q&A about mutual fund schemes — powered by Google Gemini + Chroma + Streamlit.

---

## Overview

This chatbot answers factual questions about mutual fund schemes in the context of **Groww**:
- Expense ratios, exit loads, SIP minimums
- ELSS lock-in periods, riskometer levels
- Benchmark indices
- Statement and capital gains report downloads

It **refuses advisory questions** (e.g. "Which fund should I invest in?") politely, and every answer includes exactly **one source citation** from an official public page (AMC, SEBI, AMFI, or Groww Help).

### AMC Coverage (Phase 1)
**Mirae Asset Mutual Fund** — 5 schemes:
| Scheme | Category |
|--------|----------|
| Mirae Asset Large Cap Fund | Large Cap Equity |
| Mirae Asset ELSS Tax Saver Fund | ELSS |
| Mirae Asset Emerging Bluechip Fund | Large & Mid Cap |
| Mirae Asset Liquid Fund | Liquid / Debt |
| Mirae Asset Balanced Advantage Fund | Hybrid |

---

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the full phase-wise system design.

### High-Level Flow

```
Official Pages → Scraper → Cleaner → Chunker → Gemini Embeddings → Chroma
User Query → Guardrail → Query Embedder → Chroma Top-K → Gemini LLM → Answer + Citation
```

---

## Project Structure

```
mf-faq-chatbot/
├── data/               # sources list, chunks, embeddings, golden QA set
├── ingestion/          # scraper, HTML cleaner, validator, pipeline
├── processing/         # chunker, metadata builder, document registry
├── embeddings/         # Gemini embedding generator, Chroma index
├── retrieval/          # query embedder, retriever, context builder
├── llm/                # prompt builder, Gemini generator, answer formatter
├── guardrails/         # regex patterns, LLM intent classifier, refusal messages
├── evaluation/         # retrieval eval, answer eval, guardrail eval
├── ui/                 # Streamlit app
├── config/             # settings (env-backed)
├── tests/              # unit tests
└── docs/               # architecture document
```

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini 1.5 Flash |
| Embeddings | Gemini `text-embedding-004` (768-dim) |
| Vector DB | Chroma (persistent, cosine similarity) |
| Backend | Python 3.11+ |
| UI | Streamlit |
| Testing | pytest |

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/Sid-131/RAG_chat_bot.git
cd RAG_chat_bot
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run the ingestion pipeline

```bash
python -m ingestion.pipeline
```

### 4. Launch the Streamlit UI

```bash
streamlit run ui/app.py
```

---

## Evaluation

```bash
# Retrieval quality (Recall@5, MRR, Precision@1)
python evaluation/retrieval_eval.py --dataset data/golden_qa.json

# Answer quality (citation rate, sentence constraint, faithfulness)
python evaluation/answer_eval.py --dataset data/golden_qa.json

# Guardrail accuracy (advisory refusal rate)
python evaluation/guardrail_eval.py
```

### Evaluation Targets

| Metric | Target |
|--------|--------|
| Recall@5 | ≥ 0.85 |
| MRR | ≥ 0.75 |
| Precision@1 | ≥ 0.70 |
| Citation inclusion | 100% |
| 3-sentence constraint | 100% |
| Answer faithfulness | ≥ 90% |
| Advisory refusal accuracy | 100% |

---

## Constraints

- ✅ Factual answers only — no financial advice
- ✅ Maximum 3 sentences per response
- ✅ One source citation per answer (official pages only)
- ✅ Advisory queries politely refused before any LLM call
- ✅ `temperature=0.0` — deterministic, grounded answers

---

## Status

> **Phase 1 — Architecture & Scaffold complete.**
> Implementation (Phase 2) is the next step.

---

*Data sources: Mirae Asset MF · AMFI · SEBI · Groww Help · CAMS*
