# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

"""
FastAPI Server for ATOM Environment.
Wraps the openenv-generated app with CORS, auth middleware,
WebSocket observer broadcasts, and custom endpoints for the frontend.
"""

import json
import os
import secrets as _secrets
import asyncio
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, Request, Response, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from openenv.core.env_server import create_app

try:
    from .atom_environment import AtomEnvironment
    from .auth import get_api_key, verify_api_key, print_api_key_banner
except ImportError:
    from server.atom_environment import AtomEnvironment
    from server.auth import get_api_key, verify_api_key, print_api_key_banner

try:
    from models import AtomAction, AtomObservation
except ImportError:
    from models import AtomAction, AtomObservation

# Import task definitions for the /tasks endpoint
try:
    from .rubrics.evaluator import TASKS
except ImportError:
    from server.rubrics.evaluator import TASKS


# ── WebSocket Observer Manager ────────────────────────────────

class ObserverManager:
    """
    Manages WebSocket connections from frontend observers.
    Broadcasts environment state changes (from reset/step calls)
    to all connected observers in real-time.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        print(f"[WS] Observer connected. Total: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"[WS] Observer disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send a message to all connected observers."""
        async with self._lock:
            dead = []
            for ws in self.active_connections:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.active_connections.remove(ws)

    @property
    def observer_count(self) -> int:
        return len(self.active_connections)


observer_manager = ObserverManager()


# ── Create the openenv-generated sub-app ──────────────────────
openenv_app = create_app(
    AtomEnvironment,
    AtomAction,
    AtomObservation,
    max_concurrent_envs=10,
)

# ── Create the wrapper FastAPI app ────────────────────────────
app = FastAPI(
    title="A.T.O.M. Server",
    description="Agentic Trajectories for Optimizing Molecules",
    version="2.0.4",
)

# ── CORS middleware ───────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── API Key auth middleware ───────────────────────────────────
class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates the API key on all requests
    except /health, /docs, /openapi.json, and OPTIONS preflight.
    Also intercepts /env/reset and /env/step responses to
    broadcast observations to WebSocket observers.
    """
    async def dispatch(self, request: Request, call_next):
        # Skip auth for OPTIONS (CORS preflight) and WebSockets (auth handled in endpoint)
        if request.method == "OPTIONS" or request.url.path.startswith("/ws/"):
            return await call_next(request)

        # Only enforce API key authentication on protected backend routes
        # NOTE: /env/ routes are PUBLIC so the automated validator can call reset()/step()/state()
        protected_prefixes = ("/auth/verify", "/tasks", "/observers")
        is_protected = any(request.url.path.startswith(prefix) for prefix in protected_prefixes)
        
        if not is_protected:
            # Let it through (health checks, docs, frontend static files, etc)
            return await call_next(request)

        # Validate API key for protected routes
        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            return Response(
                content=json.dumps({"detail": "Missing Authorization header"}),
                status_code=401,
                media_type="application/json"
            )

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return Response(
                content=json.dumps({"detail": "Invalid Authorization format. Use: Bearer <key>"}),
                status_code=401,
                media_type="application/json"
            )

        if not _secrets.compare_digest(parts[1], get_api_key()):
            return Response(
                content=json.dumps({"detail": "Invalid API key"}),
                status_code=401,
                media_type="application/json"
            )

        # Execute request
        response = await call_next(request)

        return response


app.add_middleware(APIKeyMiddleware)


# ── Custom endpoints ─────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check (no auth required)."""
    return {"status": "ok", "service": "atom"}


@app.get("/auth/verify")
async def verify_auth(request: Request):
    """
    Verify that the provided API key is valid.
    Auth middleware already validated it if we get here.
    """
    return {
        "status": "authenticated",
        "message": "API key is valid. Connection established."
    }


@app.get("/tasks")
async def list_tasks():
    """Returns available task definitions for the frontend."""
    tasks_list = []
    for task_id, task_def in TASKS.items():
        tasks_list.append({
            "task_id": task_def.task_id,
            "difficulty": task_def.difficulty,
            "starting_scaffold": task_def.starting_scaffold,
            "max_steps": task_def.max_steps,
            "tpp": task_def.tpp,
        })
    return {"tasks": tasks_list}


@app.get("/observers")
async def observer_count():
    """Returns the number of active WebSocket observers."""
    return {"count": observer_manager.observer_count}


# ── WebSocket Observer Endpoint ───────────────────────────────

@app.websocket("/ws/observe")
async def websocket_observe(websocket: WebSocket):
    """
    WebSocket endpoint for frontend observers.
    
    Auth: Pass API key as query param: /ws/observe?token=<api_key>
    (WebSocket doesn't support Authorization headers easily)
    
    Messages received by observers:
    - {"type": "reset", "data": {"observation": {...}}}
    - {"type": "step", "data": {"observation": {...}, "reward": float}}
    - {"type": "connected", "message": "..."}
    
    Observers can also send commands:
    - {"command": "reset", "task_id": int}
    - {"command": "ping"}
    """
    # Validate API key from query params
    token = websocket.query_params.get("token", "")
    if not token or not _secrets.compare_digest(token, get_api_key()):
        await websocket.close(code=4001, reason="Invalid API key")
        return

    await observer_manager.connect(websocket)

    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": "WebSocket observer connected. You will receive live updates.",
        "observers": observer_manager.observer_count,
    })

    try:
        while True:
            # Keep connection alive and handle incoming commands
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("command") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await observer_manager.disconnect(websocket)
    except Exception:
        await observer_manager.disconnect(websocket)


# ── Persistent Environment Manager ────────────────────────────
# OpenEnv HTTP endpoints are stateless (create+destroy env per request).
# We need stateful reset→step, so we manage a persistent env instance.

class EnvManager:
    """Manages a persistent AtomEnvironment instance for HTTP API."""
    def __init__(self):
        self.env: Optional[AtomEnvironment] = None

    def get_or_create(self) -> AtomEnvironment:
        if self.env is None:
            self.env = AtomEnvironment()
        return self.env

    def reset_env(self, task_id: int = 1):
        self.env = AtomEnvironment(task_id=task_id)
        return self.env

env_manager = EnvManager()


@app.post("/env/reset")
async def env_reset(task_id: int = 1):
    """Reset the environment with a new task. Returns initial observation."""
    env = env_manager.reset_env(task_id)
    obs = env.reset(task_id=task_id)

    result = {
        "observation": obs.model_dump() if hasattr(obs, 'model_dump') else obs.__dict__,
        "reward": 0.0,
        "done": False,
    }

    await observer_manager.broadcast({"type": "reset", "data": result})
    return result


@app.post("/env/step")
async def env_step(request: Request):
    """Execute an action on the current environment. Returns observation."""
    body = await request.json()
    action_data = body.get("action", body)

    env = env_manager.get_or_create()

    try:
        action = AtomAction(**action_data)
    except Exception as e:
        return {"error": f"Invalid action: {str(e)}"}

    obs = env.step(action)
    done = getattr(obs, 'done', False)
    reward = getattr(obs, 'reward', 0.0)

    result = {
        "observation": obs.model_dump() if hasattr(obs, 'model_dump') else obs.__dict__,
        "reward": reward,
        "done": done,
    }

    await observer_manager.broadcast({"type": "step", "data": result})
    return result


@app.get("/env/state")
async def env_state():
    """Return current environment state (OpenEnv spec compliance)."""
    env = env_manager.get_or_create()
    state = env.state
    return {
        "step_count": getattr(state, 'step_count', 0),
        "task_id": getattr(state, 'task_id', 1),
        "done": getattr(state, 'done', False),
    }


# ── Mount the openenv app at /env/openenv (for schema/ws/etc) ─
app.mount("/env/openenv", openenv_app)


# ── Serve React frontend (in Docker) ─────────────────────────
# When SERVE_FRONTEND=true, serve the built React app from /static
# This enables single-container deployment on HuggingFace Spaces
_serve_frontend = os.environ.get("SERVE_FRONTEND", "").lower() in ("true", "1", "yes")
_static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

if _serve_frontend and os.path.isdir(_static_dir):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=os.path.join(_static_dir, "assets")), name="static-assets")

    # SPA catch-all: serve index.html for any unmatched route
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for any route not handled by the API."""
        file_path = os.path.join(_static_dir, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_static_dir, "index.html"))

    print(f"[FRONTEND] Serving React app from {_static_dir}")
else:
    if _serve_frontend:
        print(f"[FRONTEND] WARNING: SERVE_FRONTEND=true but static dir not found at {_static_dir}")


# ── Startup event ────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    print_api_key_banner()


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    main()
