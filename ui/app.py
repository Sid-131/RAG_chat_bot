"""
app.py
------
Streamlit UI for the Groww Mutual Fund FAQ Chatbot.

Layout:
  - Header band (Groww brand green #00D09C)
  - Scheme filter sidebar (All / per scheme)
  - Single-line query input
  - Answer card with formatted response
  - Source citation (hyperlinked, grey text)
  - Fixed disclaimer banner at bottom

State:    Stateless — no chat history across sessions (Phase 1)
Streaming: Disabled — full answer appears at once
"""

import streamlit as st
from guardrails.patterns import is_advisory
from guardrails.classifier import classify_intent
from guardrails.refusal import get_refusal
from retrieval.query_embedder import embed_query
from retrieval.retriever import Retriever
from retrieval.context_builder import build_context
from llm.prompt_builder import build_prompt
from llm.generator import AnswerGenerator
from llm.formatter import format_answer
from embeddings.index import VectorIndex

# ---- Page config ----
st.set_page_config(
    page_title="Mutual Fund FAQ — Groww",
    page_icon="📊",
    layout="centered",
)

# ---- Custom CSS ----
st.markdown("""
<style>
    .header-band {
        background-color: #00D09C;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    .header-band h1 { color: white; margin: 0; font-size: 1.4rem; }
    .answer-card {
        background: #f8f9fa;
        border-left: 4px solid #00D09C;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
    }
    .source-link { color: #888; font-size: 0.85rem; margin-top: 0.5rem; }
    .disclaimer {
        position: fixed; bottom: 0; left: 0; right: 0;
        background: #fff3cd; padding: 0.5rem 1rem;
        font-size: 0.78rem; color: #555; text-align: center;
        border-top: 1px solid #ffc107; z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("""
<div class="header-band">
  <h1>📊 Mutual Fund FAQ — Groww</h1>
</div>
""", unsafe_allow_html=True)

# ---- Sidebar: scheme filter ----
SCHEME_OPTIONS = [
    "All Schemes",
    "Mirae Asset Large Cap Fund",
    "Mirae Asset ELSS Tax Saver Fund",
    "Mirae Asset Emerging Bluechip Fund",
    "Mirae Asset Liquid Fund",
    "Mirae Asset Balanced Advantage Fund",
]
selected_scheme = st.sidebar.selectbox("Filter by Scheme", SCHEME_OPTIONS)
scheme_filter = None if selected_scheme == "All Schemes" else selected_scheme

# ---- Query input ----
query = st.text_input(
    label="Your question",
    placeholder="e.g. What is the expense ratio of Mirae Asset Large Cap Fund?",
    label_visibility="collapsed",
)
ask_btn = st.button("Ask", type="primary")

# ---- Main logic ----
if ask_btn and query.strip():
    with st.spinner("Thinking…"):

        # Layer 1: regex guardrail
        advisory = is_advisory(query)

        # Layer 2: LLM fallback (only if regex unclear)
        if not advisory:
            intent = classify_intent(query)
            advisory = (intent == "ADVISORY")

        if advisory:
            st.markdown(
                f'<div class="answer-card">{get_refusal("ADVISORY")}</div>',
                unsafe_allow_html=True,
            )
        else:
            # Retrieval
            index = VectorIndex()
            retriever = Retriever(index)
            q_vec = embed_query(query)
            chunks = retriever.retrieve(q_vec, scheme_filter=scheme_filter)

            if not chunks:
                st.markdown(
                    f'<div class="answer-card">{get_refusal("NO_CONTEXT")}</div>',
                    unsafe_allow_html=True,
                )
            else:
                context_block, source_urls = build_context(chunks)
                prompt = build_prompt(query, context_block, source_urls)
                generator = AnswerGenerator()
                raw_answer = generator.generate(prompt)
                final_answer = format_answer(raw_answer, source_urls)

                # Split answer and citation for display
                lines = final_answer.rsplit("\n", 1)
                answer_text = lines[0]
                citation = lines[-1] if len(lines) > 1 else ""

                st.markdown(
                    f'<div class="answer-card">{answer_text}</div>',
                    unsafe_allow_html=True,
                )
                if citation:
                    st.markdown(
                        f'<p class="source-link">📎 Source: <a href="{citation}" target="_blank">{citation}</a></p>',
                        unsafe_allow_html=True,
                    )

# ---- Disclaimer ----
st.markdown("""
<div class="disclaimer">
  ⚠️ This chatbot provides factual information only and does not constitute financial advice.
  Please consult a SEBI-registered investment advisor for personalised guidance.
</div>
""", unsafe_allow_html=True)
