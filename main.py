import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from models import Base, engine
from routes import router

app = FastAPI()

# Create DB tables on startup
Base.metadata.create_all(bind=engine)

# Include business router (no prefix – DO ingress can strip /api)

@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health", response_model=dict)
async def health() -> dict:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    html = """
    <html>
    <head>
        <title>LinkSage API Demo</title>
        <style>
            body { background-color: #0d0d0d; color: #e0e0e0; font-family: Inter, sans-serif; padding: 2rem; }
            h1 { color: #4da6ff; }
            a { color: #ffcc66; text-decoration: none; }
            a:hover { text-decoration: underline; }
            table { width: 100%; max-width: 800px; border-collapse: collapse; margin-top: 1rem; }
            th, td { padding: 0.5rem; border: 1px solid #333; text-align: left; }
            th { background-color: #1a1a1a; }
            tr:nth-child(even) { background-color: #1a1a1a; }
        </style>
    </head>
    <body>
        <h1>LinkSage – AI‑Powered Secure Bookmark Manager</h1>
        <p>Demo API showcasing AI summarization, smart tagging and secure bookmark storage.</p>
        <h2>Available Endpoints</h2>
        <table>
            <tr><th>Method</th><th>Path</th><th>Description</th></tr>
            <tr><td>GET</td><td>/health</td><td>Health check</td></tr>
            <tr><td>POST</td><td>/bookmarks</td><td>Create a bookmark (AI summary & tags)</td></tr>
            <tr><td>GET</td><td>/bookmarks/{bookmark_id}</td><td>Retrieve a bookmark with its AI summary</td></tr>
            <tr><td>POST</td><td>/summarize</td><td>Generate a summary for arbitrary text</td></tr>
            <tr><td>GET</td><td>/search?q=…</td><td>Search bookmarks (placeholder implementation)</td></tr>
        </table>
        <p>Explore the interactive docs:</p>
        <ul>
            <li><a href="/docs" target="_blank">Swagger UI</a></li>
            <li><a href="/redoc" target="_blank">ReDoc</a></li>
        </ul>
        <hr/>
        <p>Tech Stack: FastAPI 0.115.0 • Pydantic 2.9.0 • SQLAlchemy 2.0.35 • PostgreSQL (via psycopg) • DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b)</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
