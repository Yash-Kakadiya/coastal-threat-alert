# 🌊 Coastal Threat Alert System

**Gujarat Coastal Guardian** — An AI-powered early warning system for coastal threats (HackOut'25)

![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![Hackathon](https://img.shields.io/badge/Event-HackOut'25-blue)
![Tech Stack](https://img.shields.io/badge/Stack-Python%20%7C%20React%20%7C%20Firebase-green)

## 🎯 One-line summary
A lightweight, explainable early-warning platform that ingests coastal sensor CSVs (simulated), runs a rule-based threat scorer, and serves real-time alerts to a React dashboard with maps and charts.

## 🎯 Problem Statement
Coastal communities face threats from storm surges, rising sea levels, pollution, illegal dumping, cyclones, and algal blooms. **Gujarat Coastal Guardian** provides early detection and human-readable alerts to protect lives, livelihoods, and blue carbon ecosystems.

## 🚀 Key Features
- Real-time threat scoring (rule-based AI brain v0, extendable to ML)
- Multi-parameter monitoring: wind, wave, tide, turbidity, chlorophyll, SST, etc.
- Interactive React dashboard (Vite + Recharts + Leaflet)
- Map markers with threat-color coding for Gujarat coastal locations
- Alert history persisted to Firebase (Firestore)
- Sensor simulator to emulate live feeds from CSVs for demo mode

## 🛠️ Tech Stack
### Backend
- **Framework:** FastAPI + uvicorn
- **Language:** Python 3.8+
- **Data processing:** pandas, numpy
- **Persistence:** Firebase (Firestore) for alerts & history
- **Testing:** pytest

### Frontend
- **Framework:** React (Vite)
- **Charts:** Recharts
- **Maps:** Leaflet
- **Styling:** Tailwind / CSS (your choice)

### Data
- **Sensor CSVs:** Kaggle / NOAA-style CSVs (placed under `backend/data/raw/`)
- **Processed data:** exported to `backend/data/processed/` (parquet/csv)
- **Satellite / mock feeds:** optional CSVs or mocked payloads

---

## 🏖️ Target Locations (Gujarat Coast)
- Kandla Port  
- Porbandar  
- Dwarka  
- Jamnagar  
- Bhavnagar

---

## 📊 Threat Levels (rule-based thresholds)
The backend returns a **0–100** score and a level:

| Level   | Score  | Color |
|---------|--------|-------|
| SAFE    | 0–30   | 🟢    |
| WATCH   | 31–60  | 🟡    |
| WARNING | 61–80  | 🟠    |
| DANGER  | 81–100 | 🔴    |

> These thresholds are configurable in `backend/config.py` (demo tunable during the hackathon).

---

## 📁 Project Structure
```
coastal-threat-alert/
├── backend/
│   ├── app.py                 # FastAPI entrypoint
│   ├── threat_model.py        # rule-based scoring logic
│   ├── data_prep.py           # CSV load / merge / resample helpers
│   ├── sensor_simulator.py    # stream processed rows as live readings
│   ├── config.py              # weights, clips, thresholds
│   ├── data/
│   │   ├── raw/               # put original CSVs here
│   │   └── processed/         # output of preprocessing
│   ├── requirements.txt
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
├── docs/
│   └── api_documentation.md
└── README.md
```

---

## 🚦 Getting Started (Backend-first quickstart)

### Prerequisites
- Python 3.8+  
- Node.js 16+ (frontend)  
- Firebase account (for production/demo persistence)  
- Git

### Backend — local dev
From repo root:

```bash
# 1. create virtualenv & install
cd backend
python -m venv venv
source venv/bin/activate       # Linux / macOS
# .\venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt

# 2. run FastAPI server (dev)
uvicorn backend.app:app --reload --port 7777
```

**Demo usage (quick test)** — use `sensor_override` to test without processed CSVs:
```powershell
curl -X POST "http://127.0.0.1:7777/get_threat_level" -H "Content-Type: application/json" -d "{
  \"location_id\": \"PORBANDAR\",
  \"sensor_override\": {
    \"timestamp\": \"2025-08-30T07:00:00Z\",
    \"wind_speed_m_s\": 12.0,
    \"wave_height_m\": 1.5,
    \"tide_level_m\": 0.6,
    \"turbidity_ntu\": 10.0,
    \"chlorophyll\": 1.2,
    \"sst\": 29.0
  }
}"
OR
$body = @{
  location_id = "PORBANDAR"
  sensor_override = @{
    timestamp = "2025-08-30T07:00:00Z"
    wind_speed_m_s = 12.0
    wave_height_m = 1.5
    tide_level_m = 0.6
    turbidity_ntu = 10.0
    chlorophyll = 1.2
    sst = 29.0
  }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://127.0.0.1:7777/get_threat_level" -Method POST -Body $body -ContentType "application/json"
```

### Data preprocessing (once you have CSVs)
Put datasets in `backend/data/raw/`. Then run the preprocessing helpers (example):

```py
# Python snippet (run inside backend virtualenv)
from backend.data_prep import preprocess_csv_paths
csvs = ["backend/data/raw/wind.csv", "backend/data/raw/waves.csv", "backend/data/raw/tide.csv"]
preprocess_csv_paths(csvs, "backend/data/processed/porbandar.parquet")
```

After preprocessing the backend will be able to load the latest processed row per location and compute threat scores automatically (replace demo `sensor_override` mode).

### Frontend — local dev
From repo root:

```bash
cd frontend
npm install
npm run dev
```

Frontend should poll `POST /get_threat_level` every ~5s (or call a streaming endpoint if you add one later). For initial integration, use the `sensor_override` demo payload to verify UI behavior.

---

## 🔍 API (initial endpoints)
- `GET /health` — service health  
- `POST /get_threat_level` — compute threat for `location_id` (accepts `sensor_override` for demo)  
- `GET /alerts` — recent alerts (read from Firestore)  
- `POST /alerts/acknowledge` — acknowledge alert

> Pydantic models and example responses are in `backend/app.py`. Use the `tests/` folder for contract tests.

---

## 🧠 Threat Model (explainable baseline)
- Normalizes sensor values into 0–1 ranges using configurable clips.
- Aggregates **physical** (wind, wave, tide) and **environmental** (turbidity, chlorophyll, SST) subscores with configurable weights.
- Adds a small **anomaly boost** for rapid spikes (z-score style to be added later).
- Returns an explanation string and component breakdown to show why an alert fired.

This keeps the system interpretable for operators and easy to tune during the hack.

---

## ✅ Demo priorities (72-hour plan)
**Day 1: Backend Core (must-have)**  
- CSV ingestion & preprocessing → `data/processed/`  
- `calculate_threat_score()` implemented and unit-tested (done)  
- FastAPI with `/get_threat_level` and demo `sensor_override` (done)

**Day 2: Frontend + integration**  
- React dashboard with Threat card, line chart (Recharts), and Leaflet map  
- Map markers for Gujarat coast, color-coded by threat level  
- Poll backend every 5s, show alert history

**Day 3: Polish & pitch**  
- Auto-insights and canned alert explanations for “Warning” & “Danger”  
- Presentation slides + demo recording  
- Deploy backend (Railway) and frontend (Vercel)

---

## 🧪 Running tests
From repo root:

```bash
cd backend
source venv/bin/activate
pytest
```

---

## 🔌 Firebase notes
- Use Firestore to store alerts with schema:
  - `timestamp`, `location_id`, `score`, `threat_level`, `components`, `raw_params`, `acknowledged`
- Keep Firebase keys in `.env` (do **not** commit secrets)
- Add `.env.example` with placeholder keys

---

## 🏆 Team & Timeline
**Team Name**: Coastal Guardians  
**Project Track**: Environmental Solutions  
**Development Period**: August 30 — September 1, 2025  
**HackOut'25 Deliverable**: Demo-ready dashboard + API + short recorded walkthrough

---

## 🤝 Contributing
1. Fork repo  
2. Create a feature branch (`git checkout -b feature/xyz`)  
3. Commit with clear messages (`git commit -m "feat: add X"`)  
4. Push and open a PR

---

## 📞 Contact
**Developer**: Yash Kakadiya  
**Event**: HackOut'25

---

*Built with ❤️ to protect Gujarat’s coastline*
