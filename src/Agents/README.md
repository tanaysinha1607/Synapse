# Synapse Profiler (CrewAI)

## Quickstart

1. Clone and install deps
```
pip install -r requirements.txt
```

2. Configure environment
- Copy your env to `.env` or export variables:
```
USE_CREWAI=1
MOCK_MODE=0
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

3. Run API
```
uvicorn api.profiler_endpoints:app --reload --port 8000
```

## Endpoints
- POST /api/profiler/process-inputs
- GET /api/profiler/profile/{user_id}
- POST /api/profiler/upload-file
- PUT /api/profiler/update-goals

## CrewAI Config
- Agents: `agent.yaml`
- Tasks: `tasks.yaml`

The profiler auto-loads YAML when present; otherwise, it falls back to built-ins.