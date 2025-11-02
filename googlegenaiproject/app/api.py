from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Path as ApiPath
from fastapi.middleware.cors import CORSMiddleware
import subprocess, os, uuid, shutil, json, sys
from pathlib import Path
from typing import Dict
from starlette.middleware.wsgi import WSGIMiddleware

# ------------------------
# Project paths (consistent, pathlib)
# ------------------------
THIS_FILE = Path(__file__).resolve()
APP_DIR = THIS_FILE.parent               # .../googlegenaiproject/app
PROJECT_ROOT = APP_DIR.parent            # .../googlegenaiproject
OUTPUTS_DIR = PROJECT_ROOT / "outputs"   # project-root outputs/
UPLOADS_DIR = APP_DIR / "uploads"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------
# FastAPI app
# ------------------------
app = FastAPI(title="GenAI Project API")

# ------------------------
# Mount Flask ML app (Backend/src/main_api.py)
# ------------------------
BACKEND_SRC = PROJECT_ROOT.parent / "Backend" / "src"
# Make sure the path exists, otherwise we will warn
if BACKEND_SRC.exists():
    sys.path.append(str(BACKEND_SRC))
    try:
        import main_api as ml_main   # this runs the ML initialization in main_api
        flask_ml_app = ml_main.app
        app.mount("/ml", WSGIMiddleware(flask_ml_app))
        print(f"[INFO] Mounted Flask ML app at /ml (imported from {BACKEND_SRC})")
    except Exception as e:
        print(f"[Warning] Could not import ML backend from {BACKEND_SRC}: {e}")
        flask_ml_app = None
else:
    print(f"[Warning] Backend src folder not found at: {BACKEND_SRC}")
    flask_ml_app = None

# ------------------------
# CORS
# ------------------------
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:18081",
    "https://synapse-hackathon-470816.web.app",
    "https://synapse-hackathon-470816.firebaseapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# Agents config & helpers
# ------------------------
AGENT_MODULES: Dict[str, str] = {
    "resume": "app.agents.resume",
    "quiz": "app.agents.quiz",
    "skillgap": "app.agents.skill_gap_agent",
    "mentor": "app.agents.mentor",
    "roadmap": "app.agents.roadmap",
}

def run_agent_module(module_path: str) -> None:
    try:
        # run with project root as cwd
        subprocess.check_call(["python3", "-m", module_path], cwd=str(PROJECT_ROOT))
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Agent {module_path} failed: {e}")

# ------------------------
# Endpoints (upload, run all, agent runner, outputs)
# ------------------------
@app.post("/api/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = UPLOADS_DIR / filename
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"status": "saved", "path": str(file_path)}

@app.post("/api/runall")
async def run_all(background: BackgroundTasks):
    run_script = APP_DIR / "run_all.py"
    if not run_script.exists():
        raise HTTPException(status_code=500, detail="run_all.py not found in app/")
    # Add background task correctly: add_task(func, *args, **kwargs)
    background.add_task(subprocess.run, ["python3", str(run_script)], cwd=str(APP_DIR), check=True)
    return {"status": "started"}

@app.post("/api/agent/{agent_name}")
async def run_agent(agent_name: str = ApiPath(..., description="one of: resume, quiz, skillgap, mentor, roadmap")):
    agent_key = agent_name.lower()
    if agent_key not in AGENT_MODULES:
        raise HTTPException(status_code=400, detail=f"Unknown agent '{agent_name}'")
    module = AGENT_MODULES[agent_key]
    try:
        run_agent_module(module)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    candidate_names = {
        "resume": ["resume_skills.json", "resume.json"],
        "quiz": ["quiz.json"],
        "skillgap": ["skillgap.json", "skill_gap.json"],
        "mentor": ["mentor_report.json", "mentor.json"],
        "roadmap": ["roadmap.json", "learning_roadmap.json"],
    }
    outputs = []
    for name in candidate_names.get(agent_key, []):
        p = OUTPUTS_DIR / name
        if p.exists():
            outputs.append(p)
    if outputs:
        p = outputs[0]
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return {"status": "done", "output_path": str(p)}
    return {"status": "done", "message": f"{agent_name} executed, no named output found in outputs/"}

@app.get("/api/outputs")
async def list_outputs():
    items = []
    for p in OUTPUTS_DIR.glob("*"):
        items.append({"name": p.name, "path": str(p)})
    return {"outputs": items}

@app.get("/api/outputs/{name}")
async def get_output(name: str):
    p = OUTPUTS_DIR / name
    if not p.exists():
        raise HTTPException(status_code=404, detail="Not found")
    text = p.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception:
        return {"name": p.name, "content": text}

@app.get("/api/health")
async def health():
    return {"status": "ok"}
