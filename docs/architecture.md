# FinAI — System Architecture (Day 1)

## Core Flow: "Why did I spend more money this month?"

1. **User Query**: Natural language question entered via UI.
2. **Backend Gateway (FastAPI)**: Receives query and passes schema/tool definitions to LLM.
3. **Intent Engine (LLM via Ollama)**: Identifies the required tool (`compare_monthly_spending`) and extracts parameters.
4. **Deterministic Analysis (Python + SQL)**:
   - Queries PostgreSQL for monthly totals, category breakdowns, and outliers.
   - Calculates exact deltas (e.g., +₹16,000 net increase).
5. **Synthesis (LLM)**: Takes verified numerical facts and drafts an evidence-backed natural explanation.
6. **Delivery**: Returns the answer to the user via the frontend.

## Key Architectural Principles
- **₹0 Cost**: Built using local open-source tools (PostgreSQL, FastAPI, Ollama).
- **No LLM Math**: LLMs route and explain; SQL and Python compute.
- **Controlled Access**: Database access is strictly mediated through backend tools.