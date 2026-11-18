import sys
import os
from pathlib import Path

# Add project root to sys.path so modules in root and backend can be imported
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from backend.app import app
except Exception as e:
    import traceback
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="Error Handler")
    error_trace = traceback.format_exc()

    @app.get("/{full_path:path}")
    def error_view(full_path: str = ""):
        return HTMLResponse(
            f"<html><body style='font-family:sans-serif;padding:30px;background:#0f172a;color:#f87171'>"
            f"<h2>Vercel Serverless Boot Exception</h2>"
            f"<pre style='background:#1e293b;padding:20px;border-radius:8px;color:#e2e8f0;overflow:auto'>{error_trace}</pre>"
            f"</body></html>",
            status_code=500
        )
