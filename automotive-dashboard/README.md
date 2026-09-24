# AutoSense AI — Predictive Maintenance Dashboard

Modern React dashboard for the existing FastAPI automotive predictive-maintenance backend.

## Stack

- React 19.3
- Vite 8.3
- Recharts
- FastAPI backend
- PostgreSQL
- Scikit-learn
- RAG + LangGraph + LLM

React 19.3 is the current stable React release as of September 2026. Vite 8.3 is the current Vite release.

## 1. Requirements

Install Node.js 20.19+ or 22.12+.

Check:

```bash
node --version
npm --version
```

## 2. Create/install

If you received this complete folder, enter it:

```bash
cd automotive-dashboard
npm install
```

Run:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

## 3. Backend

The frontend expects FastAPI at:

```text
http://127.0.0.1:8000
```

You can change this with:

```text
VITE_API_URL=http://127.0.0.1:8000
```

Create `.env` in the frontend root:

```text
VITE_API_URL=http://127.0.0.1:8000
```

## 4. CORS

Because React runs on port 5173 and FastAPI runs on port 8000, enable CORS in your FastAPI backend.

Add:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Place it immediately after:

```python
app = FastAPI(title="Automotive Predictive Maintenance API")
```

Restart FastAPI after changing it.

## 5. Backend endpoints used

The dashboard uses the existing endpoints:

- GET `/vehicles`
- GET `/vehicles/{vehicle_id}/latest`
- GET `/vehicles/{vehicle_id}/previous`
- GET `/vehicles/{vehicle_id}/health`
- GET `/vehicles/{vehicle_id}/prediction`
- GET `/vehicles/{vehicle_id}/agent`
- POST `/models/train`
- POST `/upload-csv`

## 6. Dashboard features

- Vehicle selector
- Health status
- Risk points
- Failure probability
- Anomaly status
- All major sensor values
- Recent telemetry visualization
- Maintenance action recommendations
- LangGraph + RAG + LLM engineering explanation
- CSV upload
- Model training button
- Responsive mobile layout

## 7. Production build

```bash
npm run build
```

Preview:

```bash
npm run preview
```

## Important

The dashboard does not replace the backend ML/RAG logic. It visualizes and consumes the existing FastAPI system.
