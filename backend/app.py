import asyncio
import json
import threading
from pathlib import Path
from typing import List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.runner import BugfixLoopRunner, ROOT

app = FastAPI(title="Bugfix Loop Visualizer")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections: List[WebSocket] = []
loop_lock = threading.Lock()

# Event emitter for runner that broadcasts via asyncio loop
main_asyncio_loop: asyncio.AbstractEventLoop = None

def broadcast_sync(payload: dict):
    if main_asyncio_loop and active_connections:
        asyncio.run_coroutine_threadsafe(broadcast_event(payload), main_asyncio_loop)

async def broadcast_event(payload: dict):
    msg = json.dumps(payload)
    disconnected = []
    for ws in active_connections:
        try:
            await ws.send_text(msg)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        if ws in active_connections:
            active_connections.remove(ws)

runner = BugfixLoopRunner(emit_callback=broadcast_sync)

@app.on_event("startup")
async def startup_event():
    global main_asyncio_loop
    main_asyncio_loop = asyncio.get_running_loop()

# Mount static files
static_dir = ROOT / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Dashboard index.html not found</h1>", status_code=404)

@app.get("/api/status")
async def get_status():
    return JSONResponse(runner.get_repo_status())

@app.post("/api/run/{mode}")
async def run_loop_endpoint(mode: str, background_tasks: BackgroundTasks):
    if mode not in ("good", "bad"):
        return JSONResponse({"error": "Mode must be 'good' or 'bad'"}, status_code=400)
    
    if runner.is_running:
        return JSONResponse({"error": "A loop is already in progress"}, status_code=409)

    def task():
        with loop_lock:
            runner.run_loop(mode)

    background_tasks.add_task(task)
    return JSONResponse({"status": "started", "mode": mode})

@app.post("/api/reset")
async def reset_endpoint(background_tasks: BackgroundTasks):
    if runner.is_running:
        return JSONResponse({"error": "Cannot reset while a loop is running"}, status_code=409)

    def task():
        with loop_lock:
            runner.reset_to_buggy_code()

    background_tasks.add_task(task)
    return JSONResponse({"status": "resetting"})

@app.get("/api/logs")
async def get_existing_logs():
    logs = {}
    for log_path in ROOT.glob("*.log"):
        try:
            logs[log_path.name] = log_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
    return JSONResponse(logs)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "init",
            "status": runner.get_repo_status()
        }))
        while True:
            # Keep connection alive & handle incoming pings
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)
