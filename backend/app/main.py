from backend.app.database import get_db
from backend.app.logger import FlowVisualizerMiddleware, flow_event_history
from backend.app.models import Transaction
from backend.app.schemas import TransactionCreate, TransactionResponse
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(
    title="FinAI API",
    description="Backend service for FinAI Financial Assistant",
    version="0.1.0",
)

# Attach our real-time flow visualizer middleware
app.add_middleware(FlowVisualizerMiddleware)

fake_transaction_db = []


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FinAI API", "version": "0.1.0"}


@app.get("/flow/events")
def get_flow_events():
    """Endpoint consumed by the flow frontend to trigger live animations in real-time."""
    return JSONResponse(content=list(flow_event_history))


@app.get("/flow", response_class=HTMLResponse)
def visual_flow():
    """Designer-grade interactive visual debugger and reactive architecture map."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FinAI Reactive Architecture & Live Signal Stream</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg: #07090e;
                --panel: rgba(15, 23, 42, 0.75);
                --panel-border: rgba(56, 189, 248, 0.15);
                --accent: #38bdf8;
                --accent-glow: rgba(56, 189, 248, 0.45);
                --success: #10b981;
                --success-glow: rgba(16, 185, 129, 0.5);
                --error: #f43f5e;
                --error-glow: rgba(244, 63, 94, 0.5);
                --purple: #a855f7;
                --text: #f8fafc;
                --muted: #94a3b8;
                --code-bg: #030712;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: 'Plus Jakarta Sans', sans-serif;
                background-color: var(--bg);
                background-image: 
                    radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.08) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.08) 0px, transparent 50%),
                    linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                    linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
                background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px;
                color: var(--text);
                min-height: 100vh;
                padding: 1.5rem;
                display: flex;
                flex-direction: column;
                gap: 1.25rem;
            }

            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: var(--panel);
                border: 1px solid var(--panel-border);
                backdrop-filter: blur(12px);
                padding: 1rem 1.5rem;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            }

            .logo-group {
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            .pulse-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background: var(--success);
                box-shadow: 0 0 12px var(--success);
                animation: live-blink 2s ease-in-out infinite;
            }
            @keyframes live-blink {
                0%, 100% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.4; transform: scale(0.85); }
            }

            .title-group h1 {
                font-size: 1.25rem;
                font-weight: 700;
                letter-spacing: -0.02em;
                background: linear-gradient(135deg, #fff, var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .title-group p {
                font-size: 0.75rem;
                color: var(--muted);
            }

            .action-bar {
                display: flex;
                gap: 0.75rem;
                align-items: center;
            }
            .btn {
                cursor: pointer;
                border: 1px solid var(--panel-border);
                background: rgba(30, 41, 59, 0.6);
                color: var(--text);
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-size: 0.8rem;
                font-weight: 600;
                font-family: inherit;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .btn:hover {
                background: rgba(56, 189, 248, 0.15);
                border-color: var(--accent);
                transform: translateY(-1px);
            }
            .btn-success:hover {
                background: rgba(16, 185, 129, 0.15);
                border-color: var(--success);
                color: #a7f3d0;
            }
            .btn-fail:hover {
                background: rgba(244, 63, 94, 0.15);
                border-color: var(--error);
                color: #fecdd3;
            }

            .workspace {
                display: grid;
                grid-template-columns: 1fr 480px;
                gap: 1.25rem;
                height: calc(100vh - 130px);
            }

            /* Diagram Stage */
            .stage-card {
                background: var(--panel);
                border: 1px solid var(--panel-border);
                backdrop-filter: blur(12px);
                border-radius: 12px;
                padding: 1.25rem;
                position: relative;
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .stage-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            .stage-header span {
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--muted);
            }
            .live-feed-badge {
                font-size: 0.7rem;
                font-family: 'JetBrains Mono', monospace;
                padding: 0.2rem 0.6rem;
                background: rgba(16, 185, 129, 0.12);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 20px;
                color: #6ee7b7;
            }

            svg {
                width: 100%;
                height: 100%;
            }

            /* Node Elements */
            .node {
                cursor: pointer;
                transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            }
            .node:hover {
                transform: translateY(-2px);
            }
            .node-box {
                fill: #0f172a;
                stroke: #334155;
                stroke-width: 1.5;
                rx: 10;
                transition: all 0.3s;
            }
            .node:hover .node-box, .node.selected .node-box {
                stroke: var(--accent);
                fill: #1e293b;
                filter: drop-shadow(0 0 14px var(--accent-glow));
            }
            .node.error-glow .node-box {
                stroke: var(--error) !important;
                filter: drop-shadow(0 0 16px var(--error-glow)) !important;
            }
            .node.success-glow .node-box {
                stroke: var(--success) !important;
                filter: drop-shadow(0 0 16px var(--success-glow)) !important;
            }
            .node-title {
                font-weight: 700;
                font-size: 13px;
                fill: #f8fafc;
            }
            .node-subtitle {
                font-size: 10.5px;
                fill: #94a3b8;
                font-family: 'JetBrains Mono', monospace;
            }
            .node-role {
                font-size: 11px;
                fill: #cbd5e1;
            }

            /* Edges */
            .edge-pipe {
                fill: none;
                stroke: #1e293b;
                stroke-width: 3;
                stroke-linecap: round;
            }
            .edge-pipe-glow {
                fill: none;
                stroke: transparent;
                stroke-width: 5;
                stroke-linecap: round;
                transition: stroke 0.3s;
            }
            .edge-pipe-glow.beam-active {
                stroke: var(--accent);
                stroke-dasharray: 8 8;
                animation: dashBeam 0.9s linear infinite;
                filter: drop-shadow(0 0 8px var(--accent-glow));
            }
            .edge-pipe-glow.beam-error {
                stroke: var(--error);
                stroke-dasharray: 6 6;
                animation: dashBeam 0.9s linear infinite;
                filter: drop-shadow(0 0 8px var(--error-glow));
            }
            @keyframes dashBeam {
                to { stroke-dashoffset: -16; }
            }

            .pulse-orb {
                fill: var(--accent);
                filter: drop-shadow(0 0 8px var(--accent));
            }
            .pulse-orb.orb-err {
                fill: var(--error);
                filter: drop-shadow(0 0 8px var(--error));
            }

            /* Explainer Panel */
            .inspector-card {
                background: var(--panel);
                border: 1px solid var(--panel-border);
                backdrop-filter: blur(12px);
                border-radius: 12px;
                padding: 1.5rem;
                display: flex;
                flex-direction: column;
                gap: 1.1rem;
                overflow-y: auto;
            }
            .inspector-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding-bottom: 0.75rem;
            }
            .ins-meta {
                display: flex;
                flex-direction: column;
                gap: 0.2rem;
            }
            .ins-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: var(--accent);
            }
            .ins-file {
                font-size: 0.75rem;
                font-family: 'JetBrains Mono', monospace;
                color: var(--muted);
            }
            .badge-role {
                font-size: 0.68rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                padding: 0.25rem 0.6rem;
                border-radius: 6px;
                background: rgba(56, 189, 248, 0.15);
                color: var(--accent);
                border: 1px solid rgba(56, 189, 248, 0.3);
            }

            .label-bar {
                font-size: 0.72rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--accent);
                margin-bottom: 0.35rem;
                display: flex;
                align-items: center;
                gap: 0.4rem;
            }

            .analogy-card {
                background: linear-gradient(135deg, rgba(30, 58, 138, 0.3), rgba(15, 23, 42, 0.6));
                border-left: 3px solid var(--accent);
                padding: 0.85rem 1rem;
                border-radius: 0 8px 8px 0;
                font-size: 0.82rem;
                line-height: 1.5;
                color: #e2e8f0;
            }

            .desc-card {
                font-size: 0.82rem;
                line-height: 1.5;
                color: var(--muted);
            }

            .code-wrap {
                background: var(--code-bg);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 0.85rem;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.74rem;
                line-height: 1.45;
                color: #93c5fd;
                overflow-x: auto;
            }

            .fail-card {
                background: rgba(244, 63, 94, 0.08);
                border: 1px solid rgba(244, 63, 94, 0.25);
                border-radius: 8px;
                padding: 0.75rem 1rem;
                font-size: 0.78rem;
                color: #fecdd3;
                line-height: 1.45;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo-group">
                <div class="pulse-dot"></div>
                <div class="title-group">
                    <h1>FinAI System Flow & Signal Engine</h1>
                    <p>Live Parallel Bus • Watching Port 8000 & PostgreSQL 5432</p>
                </div>
            </div>
            <div class="action-bar">
                <button class="btn btn-success" onclick="triggerTest(true)">⚡ Test Live Valid (₹1,850)</button>
                <button class="btn btn-fail" onclick="triggerTest(false)">⚠️ Test Live Invalid (-₹500)</button>
                <button class="btn" onclick="resetTelemetry()">↺ Reset</button>
            </div>
        </header>

        <div class="workspace">
            <!-- Left: Flow Diagram -->
            <div class="stage-card">
                <div class="stage-header">
                    <span>Active Topology Map (Click Any Station)</span>
                    <div id="live_status" class="live-feed-badge">● Listening for requests...</div>
                </div>

                <svg id="stage_svg" viewBox="0 0 760 520">
                    <defs>
                        <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                            <path d="M 0 1 L 10 5 L 0 9 z" fill="#334155" />
                        </marker>
                    </defs>

                    <!-- CONNECTING CONDUITS -->
                    <!-- 1. Client -> Middleware -->
                    <path class="edge-pipe" d="M 170 100 L 250 100" />
                    <path id="pipe_c_mw" class="edge-pipe-glow" d="M 170 100 L 250 100" />

                    <!-- 2. Middleware -> Router -->
                    <path class="edge-pipe" d="M 430 100 L 510 100" />
                    <path id="pipe_mw_r" class="edge-pipe-glow" d="M 430 100 L 510 100" />

                    <!-- 3. Router -> Pydantic -->
                    <path class="edge-pipe" d="M 595 140 L 595 210" />
                    <path id="pipe_r_pyd" class="edge-pipe-glow" d="M 595 140 L 595 210" />

                    <!-- 4. Pydantic -> Database -->
                    <path class="edge-pipe" d="M 595 290 L 595 360" />
                    <path id="pipe_pyd_db" class="edge-pipe-glow" d="M 595 290 L 595 360" />

                    <!-- 5. Database -> asyncpg Courier -->
                    <path class="edge-pipe" d="M 510 400 L 400 400" />
                    <path id="pipe_db_courier" class="edge-pipe-glow" d="M 510 400 L 400 400" />

                    <!-- 6. Error return arc: Pydantic back to Client -->
                    <path id="pipe_pyd_err" class="edge-pipe-glow" d="M 510 250 C 350 260, 260 180, 170 120" style="display:none;" />

                    <!-- STATIONS / NODES -->
                    <!-- Node 1: Browser -->
                    <g id="node_client" class="node" transform="translate(20, 60)" onclick="selectNode('client')">
                        <rect class="node-box" width="150" height="80" />
                        <text x="18" y="30" class="node-title">🌐 Browser Client</text>
                        <text x="18" y="48" class="node-subtitle">Origin: HTTP / JSON</text>
                        <text x="18" y="66" class="node-role">Sends POST / GET</text>
                    </g>

                    <!-- Node 2: Middleware -->
                    <g id="node_middleware" class="node" transform="translate(250, 60)" onclick="selectNode('middleware')">
                        <rect class="node-box" width="180" height="80" />
                        <text x="18" y="30" class="node-title">🛡️ Flow Middleware</text>
                        <text x="18" y="48" class="node-subtitle">backend/app/logger.py</text>
                        <text x="18" y="66" class="node-role">Measures Latency (ms)</text>
                    </g>

                    <!-- Node 3: Router -->
                    <g id="node_router" class="node" transform="translate(510, 60)" onclick="selectNode('router')">
                        <rect class="node-box" width="170" height="80" />
                        <text x="18" y="30" class="node-title">⚡ FastAPI Router</text>
                        <text x="18" y="48" class="node-subtitle">backend/app/main.py</text>
                        <text x="18" y="66" class="node-role">Directs to Function</text>
                    </g>

                    <!-- Node 4: Pydantic -->
                    <g id="node_pydantic" class="node" transform="translate(510, 210)" onclick="selectNode('pydantic')">
                        <rect class="node-box" width="170" height="80" />
                        <text x="18" y="30" class="node-title">👮 Pydantic Guard</text>
                        <text x="18" y="48" class="node-subtitle">backend/app/schemas.py</text>
                        <text x="18" y="66" class="node-role">Validates Amount &gt; 0</text>
                    </g>

                    <!-- Node 5: Database Engine -->
                    <g id="node_database" class="node" transform="translate(510, 360)" onclick="selectNode('database')">
                        <rect class="node-box" width="170" height="85" />
                        <text x="18" y="30" class="node-title">🗄️ PostgreSQL 18</text>
                        <text x="18" y="48" class="node-subtitle">finai_db : 5432</text>
                        <text x="18" y="66" class="node-role">Disk Relational Vault</text>
                    </g>

                    <!-- Node 6: asyncpg Driver -->
                    <g id="node_courier" class="node" transform="translate(230, 360)" onclick="selectNode('courier')">
                        <rect class="node-box" width="170" height="85" />
                        <text x="18" y="30" class="node-title">⚡ asyncpg Courier</text>
                        <text x="18" y="48" class="node-subtitle">Async Network Driver</text>
                        <text x="18" y="66" class="node-role">Zero-Freeze Wire Courier</text>
                    </g>

                    <!-- Moving Signal Orb -->
                    <circle id="signal_orb" class="pulse-orb" cx="0" cy="0" r="7" style="opacity:0;" />
                </svg>
            </div>

            <!-- Right: Explainer & Code Storyboard -->
            <div class="inspector-card" id="inspector">
                <div class="inspector-header">
                    <div class="ins-meta">
                        <h2 id="ins_title" class="ins-title">Select Any Station</h2>
                        <span id="ins_file" class="ins-file">File: Ready to inspect</span>
                    </div>
                    <span id="ins_badge" class="badge-role">INSPECTOR</span>
                </div>

                <div>
                    <div class="label-bar">💡 Real-World Plain English Analogy</div>
                    <div class="analogy-card" id="ins_analogy">
                        Open another tab or click one of the live test buttons above to see the signal travel across your actual backend in real time!
                    </div>
                </div>

                <div>
                    <div class="label-bar">⚙️ What Is Happening At This Station?</div>
                    <div class="desc-card" id="ins_desc">
                        Every layer in FinAI is decoupled with a dedicated single responsibility.
                    </div>
                </div>

                <div>
                    <div class="label-bar">💻 Exact Project Source Code</div>
                    <div class="code-wrap">
                        <pre id="ins_code"><code>// Source code will render here...</code></pre>
                    </div>
                </div>

                <div>
                    <div class="label-bar">🚨 Failure Conditions & Exceptions</div>
                    <div class="fail-card" id="ins_fail">
                        No active error state.
                    </div>
                </div>
            </div>
        </div>

        <script>
            const STATION_GUIDE = {
                client: {
                    title: "1. Browser Client",
                    file: "Web Browser (Swagger /docs, Postman, or React UI)",
                    badge: "HTTP ORIGIN",
                    analogy: "Like a customer walking up to an HDFC bank counter and sliding an account deposit slip through the glass window.",
                    desc: "Packages your inputs into standard JSON bytes and sends an HTTP POST request across the TCP network socket to 127.0.0.1:8000.",
                    code: `fetch('http://127.0.0.1:8000/transactions', {\\n  method: 'POST',\\n  headers: { 'Content-Type': 'application/json' },\\n  body: JSON.stringify({\\n    amount: 1850.50,\\n    merchant: 'DMart',\\n    category: 'Groceries',\\n    transaction_date: '2026-10-04'\\n  })\\n});`,
                    fail: "Connection Refused: If Uvicorn is offline, the browser immediately crashes with 'ERR_CONNECTION_REFUSED' because the port is closed."
                },
                middleware: {
                    title: "2. Logger Middleware",
                    file: "backend/app/logger.py",
                    badge: "INTERCEPTOR",
                    analogy: "Like a receptionist at the entrance who stamps the exact time you arrived, writes down your badge number, and clocks your exit with a stopwatch.",
                    desc: "Intercepts every single byte entering the application before FastAPI routes it. Computes duration in milliseconds and pushes telemetry events to this live flow map.",
                    code: `class FlowVisualizerMiddleware(BaseHTTPMiddleware):\\n    async def dispatch(self, request: Request, call_next):\\n        start = time.time()\\n        response = await call_next(request)\\n        latency = (time.time() - start) * 1000\\n        print(f"Dispatched in {latency:.2f}ms")\\n        return response`,
                    fail: "Server 500 Crash: If an unhandled exception triggers inside middleware, the request dies right at the door before touching your routes."
                },
                router: {
                    title: "3. FastAPI Router",
                    file: "backend/app/main.py",
                    badge: "URL DISPATCHER",
                    analogy: "Like a bank receptionist who reads your slip title: 'Deposit' goes to Counter 3; 'Health Check' goes to Information Desk 1.",
                    desc: "Inspects HTTP Method (POST) and URL Path (/transactions) and delegates the payload to the matching Python function create_transaction().",
                    code: `@app.post("/transactions")\\ndef create_transaction(transaction: TransactionCreate):\\n    # Router resolves dependencies and executes logic\\n    saved = transaction.model_dump()\\n    fake_transaction_db.append(saved)\\n    return {"message": "Success", "data": saved}`,
                    fail: "HTTP 404 Not Found: Occurs when calling an unregistered URL path.\\nHTTP 405: Occurs when calling a POST route using GET."
                },
                pydantic: {
                    title: "4. Pydantic Guard",
                    file: "backend/app/schemas.py",
                    badge: "SCHEMA GATEWAY",
                    analogy: "Like a strict bank teller who inspects the deposit slip. If you wrote a negative number like -₹500, they immediately return the slip without touching the vault.",
                    desc: "Enforces data constraints before your core application logic runs. Validates that amount > 0, merchant name is valid, and the date matches ISO format.",
                    code: `class TransactionCreate(BaseModel):\\n    amount: float = Field(..., gt=0, description="Must be greater than 0")\\n    merchant: str = Field(..., min_length=2)\\n    category: str = Field(...)\\n    transaction_date: date`,
                    fail: "HTTP 422 Unprocessable Content: If amount <= 0, Pydantic halts execution immediately and rejects the request. The database is never touched."
                },
                database: {
                    title: "5. PostgreSQL Relational Vault",
                    file: "backend/app/database.py & 01_init.sql",
                    badge: "PERSISTENCE",
                    analogy: "Like the underground fireproof bank safe. Once a ledger row is committed here, it survives system restarts, server reboots, and power failures.",
                    desc: "Stores financial ledger records with exact decimal math (NUMERIC) and enforces referential integrity so transactions can never reference nonexistent accounts.",
                    code: `CREATE TABLE transactions (\\n    id SERIAL PRIMARY KEY,\\n    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,\\n    amount NUMERIC(10, 2) NOT NULL,\\n    merchant VARCHAR(100) NOT NULL,\\n    transaction_date DATE NOT NULL\\n);`,
                    fail: "ForeignKeyViolation: If account_id doesn't exist, PostgreSQL halts the commit.\\nConnection Refused: If PostgreSQL service on 5432 is stopped."
                },
                courier: {
                    title: "6. asyncpg Network Courier",
                    file: "backend/app/database.py (.env: asyncpg)",
                    badge: "WIRE DRIVER",
                    analogy: "Like a restaurant smart-buzzer system: the kitchen takes your order and hands you a vibrating token, allowing the cashier to take orders from 100 more people without freezing the line!",
                    desc: "The high-speed non-blocking driver that encodes Python objects into PostgreSQL binary wire packets, allowing FastAPI to juggle thousands of requests asynchronously.",
                    code: `# Connection Engine using asyncpg:\\nDATABASE_URL = "postgresql+asyncpg://postgres:pass@127.0.0.1:5432/finai_db"\\nengine = create_async_engine(DATABASE_URL, echo=True)`,
                    fail: "DNS / Name Resolution Error ([Errno 11003]): Happens when password characters like '@' aren't URL-encoded to '%40'."
                }
            };

            function selectNode(key) {
                const data = STATION_GUIDE[key];
                if (!data) return;

                document.querySelectorAll('.node').forEach(n => n.classList.remove('selected'));
                const el = document.getElementById('node_' + key);
                if (el) el.classList.add('selected');

                document.getElementById('ins_title').innerText = data.title;
                document.getElementById('ins_file').innerText = "File: " + data.file;
                document.getElementById('ins_analogy').innerText = data.analogy;
                document.getElementById('ins_desc').innerText = data.desc;
                document.getElementById('ins_code').innerText = data.code;
                document.getElementById('ins_fail').innerText = data.fail;

                const badge = document.getElementById('ins_badge');
                badge.innerText = data.badge;
            }

            // Real-Time Animated Signal Traveling Across SVG
            function animateSegment(p1, p2, duration, orbClass, onDone) {
                const orb = document.getElementById('signal_orb');
                orb.setAttribute('class', orbClass);
                orb.style.opacity = '1';

                const start = performance.now();
                function step(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    const cx = p1.x + (p2.x - p1.x) * progress;
                    const cy = p1.y + (p2.y - p1.y) * progress;
                    orb.setAttribute('cx', cx);
                    orb.setAttribute('cy', cy);

                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else if (onDone) {
                        onDone();
                    }
                }
                requestAnimationFrame(step);
            }

            function playFlowAnimation(isSuccess, latency) {
                resetPipes();
                const statusEl = document.getElementById('live_status');
                statusEl.innerText = `● Signal Active: ${isSuccess ? 'HTTP 200 OK' : 'HTTP 422 REJECTED'} (${latency}ms)`;
                statusEl.style.color = isSuccess ? '#6ee7b7' : '#fecdd3';

                // Leg 1: Client -> Middleware
                selectNode('client');
                document.getElementById('pipe_c_mw').classList.add('beam-active');
                animateSegment({x: 170, y: 100}, {x: 250, y: 100}, 350, 'pulse-orb', () => {

                    // Leg 2: Middleware -> Router
                    selectNode('middleware');
                    document.getElementById('pipe_mw_r').classList.add('beam-active');
                    animateSegment({x: 430, y: 100}, {x: 510, y: 100}, 350, 'pulse-orb', () => {

                        // Leg 3: Router -> Pydantic
                        selectNode('router');
                        document.getElementById('pipe_r_pyd').classList.add('beam-active');
                        animateSegment({x: 595, y: 140}, {x: 595, y: 210}, 350, 'pulse-orb', () => {

                            selectNode('pydantic');

                            if (isSuccess) {
                                // Leg 4: Pydantic -> Database
                                document.getElementById('pipe_pyd_db').classList.add('beam-active');
                                animateSegment({x: 595, y: 290}, {x: 595, y: 360}, 400, 'pulse-orb', () => {
                                    
                                    selectNode('database');
                                    // Leg 5: Database -> Courier
                                    document.getElementById('pipe_db_courier').classList.add('beam-active');
                                    animateSegment({x: 510, y: 400}, {x: 400, y: 400}, 350, 'pulse-orb', () => {
                                        selectNode('courier');
                                        document.getElementById('signal_orb').style.opacity = '0';
                                    });
                                });
                            } else {
                                // Error branch: Pydantic halts and sends rejection back
                                const pydNode = document.getElementById('node_pydantic');
                                pydNode.classList.add('error-glow');

                                const errPipe = document.getElementById('pipe_pyd_err');
                                errPipe.style.display = 'block';
                                errPipe.classList.add('beam-error');

                                animateSegment({x: 510, y: 250}, {x: 170, y: 120}, 500, 'pulse-orb orb-err', () => {
                                    selectNode('client');
                                    document.getElementById('signal_orb').style.opacity = '0';
                                });
                            }
                        });
                    });
                });
            }

            function resetPipes() {
                document.querySelectorAll('.edge-pipe-glow').forEach(p => {
                    p.classList.remove('beam-active', 'beam-error');
                });
                document.querySelectorAll('.node').forEach(n => {
                    n.classList.remove('selected', 'error-glow', 'success-glow');
                });
                document.getElementById('pipe_pyd_err').style.display = 'none';
                document.getElementById('signal_orb').style.opacity = '0';
            }

            function resetTelemetry() {
                resetPipes();
                selectNode('pydantic');
                const statusEl = document.getElementById('live_status');
                statusEl.innerText = "● Listening for requests...";
                statusEl.style.color = "#6ee7b7";
            }

            // Real Live HTTP Test Handlers
            async function triggerTest(isValid) {
                const payload = isValid
                    ? { amount: 1850.50, merchant: "DMart", category: "Groceries", transaction_date: "2026-10-04" }
                    : { amount: -500.00, merchant: "Test", category: "Test", transaction_date: "2026-10-04" };

                try {
                    await fetch('/transactions', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                } catch(e) {
                    console.error("Test fetch dispatched", e);
                }
            }

            // PARALLEL TELEMETRY STREAMING: Continuously checks backend for new activity from ANY tab
            let lastEventId = 0;
            async function pollEvents() {
                try {
                    const res = await fetch('/flow/events');
                    if (res.ok) {
                        const events = await res.json();
                        if (events.length > 0) {
                            const latest = events[events.length - 1];
                            if (latest.id !== lastEventId) {
                                lastEventId = latest.id;
                                const isSuccess = latest.status === 'success';
                                playFlowAnimation(isSuccess, latest.latency_ms);
                            }
                        }
                    }
                } catch(e) {
                    // Backoff silently if server restarts
                }
                setTimeout(pollEvents, 700);
            }

            // Start polling and default select
            window.addEventListener('DOMContentLoaded', () => {
                selectNode('courier');
                pollEvents();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate, db: AsyncSession = Depends(get_db)
):
  """Inserts a validated transaction into PostgreSQL via asyncpg."""
  try:
    db_item = Transaction(
        account_id=transaction.account_id,
        amount=transaction.amount,
        merchant=transaction.merchant,
        category=transaction.category,
        transaction_date=transaction.transaction_date,
        description=transaction.description,
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
  except Exception as e:
    await db.rollback()
    raise HTTPException(status_code=500, detail=str(e))


@app.get("/transactions")
async def get_transactions(db: AsyncSession = Depends(get_db)):
  """Fetches real persisted records from PostgreSQL."""
  result = await db.execute(select(Transaction).order_by(Transaction.id.desc()))
  items = result.scalars().all()
  return {
      "count": len(items),
      "transactions": items,
  }