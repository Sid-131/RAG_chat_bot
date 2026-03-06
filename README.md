# RAG-Based Mutual Fund FAQ Chatbot

**"Facts-only. No investment advice."**

This is an end-to-end Retrieval-Augmented Generation (RAG) chatbot designed to answer factual questions about mutual funds available on Groww. It extracts data from SEBI, AMFI, and AMC fact sheets, ensuring all answers are grounded in official documentation and include direct citations.

## Architecture Summary
The system is built on a two-tier architecture:
1.  **FastAPI Backend (`backend/main.py`):** An orchestrator that manages guardrails, semantic retrieval via ChromaDB, and grounded generation using the Gemini 2.5 Flash API.
2.  **Streamlit Frontend (`ui/chat_app.py`):** A custom-styled React-like dashboard UI that connects to the FastAPI backend, displaying chat history, inline source citations, and suggested questions.

## Phase-Wise System Design
*   **Phases 1-3 (Ingestion & Processing):** Asynchronous web scraping (`httpx` + `Playwright`) of official AMC sources, cleaning raw HTML into plain text, and chunking into 400-token semantic blocks.
*   **Phases 4-5 (Embeddings & Vector DB):** Converting text chunks into 3072-dimensional vectors using `gemini-embedding-001` and persisting them in a local ChromaDB database.
*   **Phase 6 (Retrieval):** Cosine similarity search against ChromaDB to fetch the Top-5 most relevant chunks to a user's query.
*   **Phase 7 (Generation):** Injecting context into a rigid prompt template instructing `gemini-2.5-flash` (at `temperature=0.0`) to generate factual, ≤3 sentence answers with citations.
*   **Phase 8 (Guardrails):** A dual-layer safety system (Regex pattern matching + LLM intent classification) that instantly blocks advisory questions like *"Which fund is best?"* and safely redirects users to SEBI/AMFI educational resources.
*   **Phases 9-10 (Backend API & Frontend UI):** A FastAPI REST service and a custom-styled Streamlit application mimicking a premium AI workspace.
*   **Phases 12-13 (Evaluation & Deployment):** Evaluated locally against 10 strict factual/advisory queries and structured for Vercel/Streamlit Cloud distribution.

## Data Sources (15–25 Official URLs)
The data is sourced from official and regulatory entities:
*   **AMC Fact Sheets:** Mirae Asset Large Cap, ELSS Tax Saver, Liquid Fund, etc.
*   **SEBI:** Guidelines on Expense Ratios and ELSS Lock-in rules.
*   **AMFI:** Riskometer classifications and mutual fund categorization definitions.
*   **Groww Help Center:** Articles on downloading capital gains and CAS statements.

## Technology Stack
*   **Model:** Google Gemini API (`gemini-2.5-flash`, `gemini-embedding-001`) SDK: `google-genai`
*   **Vector Database:** ChromaDB (`chromadb`)
*   **Backend:** FastAPI, Pydantic, Uvicorn
*   **Frontend:** Streamlit (with injected HTML/CSS grids)
*   **Data Processing:** `spacy`, `BeautifulSoup4`

---

## Setup Instructions

### 1. Local Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```
*(If a `requirements.txt` is missing, ensure you have: `fastapi uvicorn pydantic python-dotenv chromadb google-genai streamlit requests beautifulsoup4`)*

### 2. Environment Variables
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY=AIzaSyDD5FxzxeN7tgjvejIn2Wk6WF1Fq...
BACKEND_PORT=8000
CHROMA_PERSIST_DIR=db/chroma
```

### 3. Running Locally
Because this is a decoupled architecture, you must run both the backend and frontend simultaneously.

**Terminal 1 (Backend):**
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
**Terminal 2 (Frontend):**
```bash
python -m streamlit run ui/chat_app.py
```
Open `http://localhost:8501` in your browser.

---

## Deployment Instructions

### Deploying the Backend on Vercel
Vercel supports running FastAPI as Serverless Functions using the `@vercel/python` runtime.
1. Install the Vercel CLI: `npm i -g vercel`
2. Run `vercel` in the project root.
3. The included `vercel.json` will automatically route all API requests to `backend/main.py`.
4. In your Vercel project settings, add the `GEMINI_API_KEY` environment variable.

### Deploying the Frontend on Streamlit Cloud
Streamlit does not run natively on Vercel due to its reliance on persistent WebSockets. The best deployment path for the frontend is Streamlit Community Cloud:
1. Push the repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io) and deploy `ui/chat_app.py`.
3. In Streamlit Cloud Advanced Settings, set `BACKEND_API_URL` to your live Vercel FastAPI URL (e.g., `https://your-backend.vercel.app/query`).

---

## Demo Video Instructions
To record a demo video for submission:
1. Show both terminal windows starting up without errors.
2. Open the browser and show the custom dashboard interface.
3. Ask a **factual question** (e.g., *"What is the exit load for Mirae Asset ELSS?"*) and show the bot returning a short answer with a clickable `[Source]` link.
4. Ask an **advisory question** (e.g., *"Which mutual fund should I invest in to get rich?"*) and show the bot refusing using the template containing SEBI/AMFI/Groww links.

## Known Limitations
*   Vercel Serverless Functions have a 10-second timeout on the Hobby tier, which might interrupt long Gemini generation tasks if the API is slow.
*   The current vector database uses local ChromaDB SQLite storage. For a true serverless Vercel deployment, ChromaDB should ideally be hosted externally (e.g., Chroma Cloud or Pinecone) as Vercel filesystems are read-only and ephemeral.
