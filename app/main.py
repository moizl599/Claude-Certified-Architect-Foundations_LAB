"""CCAR-F Interactive Lab Environment — FastAPI backend."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os

from executor import execute_code

app = FastAPI(title="CCAR-F Labs")

# ── Import lab data ───────────────────────────────────────────────
from labs import ALL_LABS

# ── Models ────────────────────────────────────────────────────────
class ExecuteRequest(BaseModel):
    code: str
    dry_run: bool = False
    lab_id: str = ""
    step_id: int = 0

class ApiKeyRequest(BaseModel):
    api_key: str

# ── API Routes ────────────────────────────────────────────────────
@app.get("/api/labs")
def list_labs():
    """Return lab summaries for the sidebar."""
    return [
        {
            "id": lab["id"],
            "domain": lab["domain"],
            "domain_name": lab["domain_name"],
            "title": lab["title"],
            "description": lab["description"],
            "difficulty": lab["difficulty"],
            "estimated_time": lab["estimated_time"],
            "step_count": len(lab["steps"]),
        }
        for lab in ALL_LABS
    ]

@app.get("/api/labs/{lab_id}")
def get_lab(lab_id: str):
    """Return full lab content including all steps."""
    for lab in ALL_LABS:
        if lab["id"] == lab_id:
            return lab
    raise HTTPException(status_code=404, detail=f"Lab {lab_id} not found")

@app.post("/api/execute")
def run_code(req: ExecuteRequest):
    """Execute code or return dry-run output."""
    if req.dry_run:
        # Find the lab and step, return pre-built dry-run output
        for lab in ALL_LABS:
            if lab["id"] == req.lab_id:
                for step in lab["steps"]:
                    if step["id"] == req.step_id:
                        return {
                            "stdout": step.get("dry_run_output", "(No dry-run output for this step)"),
                            "stderr": "",
                            "returncode": 0,
                            "timed_out": False,
                            "dry_run": True,
                        }
        return {
            "stdout": "(Dry-run output not available)",
            "stderr": "",
            "returncode": 0,
            "timed_out": False,
            "dry_run": True,
        }

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY") or os.environ["ANTHROPIC_API_KEY"].startswith("sk-ant-xxxxx"):
        return {
            "stdout": "",
            "stderr": "⚠️  No API key configured. Add your key to .env or switch to Dry Run mode.",
            "returncode": 1,
            "timed_out": False,
            "dry_run": False,
        }

    result = execute_code(req.code, timeout=30)
    result["dry_run"] = False
    return result

@app.post("/api/key")
def set_api_key(req: ApiKeyRequest):
    """Set the Anthropic API key at runtime (persists for session)."""
    key = req.api_key.strip()
    if not key.startswith("sk-ant-"):
        raise HTTPException(status_code=400, detail="Invalid key format. Must start with sk-ant-")
    os.environ["ANTHROPIC_API_KEY"] = key
    # Also write to .env so it survives container restarts via volume mount
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        with open(env_path, "w") as f:
            f.write(f"ANTHROPIC_API_KEY={key}\n")
    except OSError:
        pass  # Runtime env var is still set
    return {"status": "ok", "message": "API key saved"}

@app.get("/api/health")
def health():
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY")) and not os.environ.get("ANTHROPIC_API_KEY", "").startswith("sk-ant-xxxxx")
    return {"status": "ok", "api_key_configured": has_key}

# ── Static files & SPA fallback ───────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
