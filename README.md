# 💧 Aquix — Smart Water Intelligence System for Bangalore (BWSSB)

Aquix is an AI-powered water management platform for Bangalore's water utility (BWSSB). It combines anomaly detection (leak/overconsumption), demand & flood prediction, drone-based leak scanning, equitable water redistribution, and a citizen + government dashboard experience — backed by a Flask API and a Cohere-powered conversational assistant.

The project currently ships as several related surfaces that share the same backend logic:

| Component | File | Description |
|---|---|---|
| 🏛️ **Government Command Centre** | `aquix_gov.html` + `aquix_gov_backend.py` | BWSSB-facing ops dashboard: incident management, drone fleet, emergency alerts, SDG reporting, service dispatch. Runs on port `5000`. |
| 🚁 **Citizen Web Dashboard** | `Drone.html` | Public-facing "BWSSB Bangalore Water Detection" dashboard with live drone-swarm leak scanning visualization, zone risk map, and AI agent panel. |
| ⚙️ **Core Backend API** | `aquix_backend.py` | Full-featured Flask API (v4.0) — anomaly detection, ML predictions, weather, chatbot, redistribution engine, map/heatmap data. Runs on port `5006`. |
| 🧠 **AI Agents** | `agents.py` | Lightweight decision & chat agent layer built on Cohere's `command-a-03-2025` model. |
| 📊 **Prototype / Demo App** | `app.py` | An earlier Streamlit prototype of the dashboard (overview, demand prediction, leak detection, weather, map, farmer insights, services, chatbot) — useful for quick local demos. |
| 📱 **Mobile App Shell** | `app.json` | Expo/React Native configuration for the Aquix mobile app (iOS/Android/Web), built with `expo-router`. |

---

## ✨ Key Features

- **Leak & Anomaly Detection** — Ensemble of Z-score, IQR, and Isolation Forest models flags pipe bursts and unusual consumption across 12+ Bangalore zones (Koramangala, Whitefield, HSR Layout, etc.), with human-readable justifications and severity scoring.
- **Water Redistribution Engine** — Computes population-proportional "fair share" allocations and plans transfers from surplus to deficit zones, with an equity score (Gini-based).
- **Predictive Models**
  - 📈 Demand forecasting (temperature, humidity, density, rainfall, user type)
  - 🚨 Leak probability scoring (pressure, flow, turbidity)
  - 🌊 Flood risk & pipeline stress prediction (monsoon intensity, drainage, deforestation)
  - 💧 Water potability check (pH, TDS, turbidity)
  - 🌾 Crop recommendation for irrigation planning
- **Drone Fleet Simulation** — Autonomous drones "swarm" toward high-risk zones on the live map, visualized in real time (`Drone.html`).
- **Weather Integration** — Live OpenWeather data with graceful mock-data fallback.
- **Multi-Agent Orchestration** (`/api/agents/run`) — Combines prediction, leak detection, and decision agents into a single situational report.
- **Citizen Services** — Book tankers/plumbers, file complaints, track ticket status.
- **AI Chatbot** — Cohere-powered assistant ("AquaSphere Assistant") for citizen queries, multi-language ready.
- **Government Ops Tools** — Emergency alert broadcast, drone dispatch, BWSSB supply schedules, SDG progress reporting, incident audit log.

---

## 🏗️ Architecture

```
┌─────────────────────┐      ┌──────────────────────┐
│   aquix_gov.html      │────▶│  aquix_gov_backend.py  │  (port 5000)
│  Gov Command Centre │      │   Flask API (Gov)     │
└─────────────────────┘      └──────────────────────┘

┌─────────────────────┐      ┌──────────────────────┐
│      Drone.html      │────▶│    aquix_backend.py    │  (port 5006)
│  Citizen Dashboard  │      │  Flask API (Core v4)  │
└─────────────────────┘      └──────────┬───────────┘
                                          │
                                    agents.py
                              (Cohere decision + chat agent)

┌─────────────────────┐
│       app.py          │  Streamlit prototype (standalone demo)
└─────────────────────┘

┌─────────────────────┐
│       app.json        │  Expo mobile app config
└─────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- `pip`
- (Optional) Node.js + Expo CLI if working on the mobile app

### 1. Clone & install dependencies

```bash
pip install flask flask-cors numpy scikit-learn cohere requests python-dotenv streamlit folium streamlit-folium
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
COHERE_API_KEY=your-cohere-api-key
OPENWEATHER_API_KEY=your-openweather-api-key
```

> ⚠️ **Security note:** `app.py` currently has API keys hardcoded directly in the source. Before sharing or deploying this project, move those keys into `.env` (as already done in `aquix_backend.py` / `agents.py`) and **rotate the exposed keys**, since they've been committed to a shared file.

### 3. Run the core backend

```bash
python aquix_backend.py --port 5006
```

Then open `http://localhost:5006/` — this serves the connected frontend and exposes 17+ REST endpoints (see below).

### 4. Run the government dashboard backend

```bash
python aquix_gov_backend.py --port 5000
```

Then open `aquix_gov.html` directly in a browser (it calls `http://localhost:5000/api`).

### 5. (Optional) Run the Streamlit prototype

```bash
streamlit run app.py
```

### 6. (Optional) Run the mobile app

```bash
npx expo start
```

---

## 📡 API Reference (Core Backend — `aquix_backend.py`)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/anomaly/detect` | Run ensemble anomaly detection on zone data |
| GET | `/api/anomaly/history` | Retrieve past anomaly runs |
| POST | `/api/predict/demand` | Forecast water demand |
| POST | `/api/predict/leak` | Leak probability scoring |
| POST | `/api/predict/flood` | Flood risk & pipeline stress prediction |
| POST | `/api/predict/potability` | Water potability check |
| POST | `/api/predict/crop` | Crop recommendation |
| GET | `/api/weather/<city>` | Live weather + prediction agent insight |
| POST | `/api/farmer/agent` | Irrigation recommendation agent |
| POST | `/api/agents/run` | Full multi-agent situational report |
| POST | `/api/services/book` | Book a service (tanker, plumber, etc.) |
| POST | `/api/complaints/submit` | File a citizen complaint |
| GET | `/api/complaints/status/<ticket_id>` | Check complaint/booking status |
| POST | `/api/chat` | AI chatbot (Cohere) |
| GET | `/api/dashboard/overview` | City-wide KPI summary |
| GET | `/api/dashboard/zones` | Per-zone metrics |
| GET | `/api/map/heatmap` | Heatmap + zone polygon data |
| GET | `/api/map/incidents` | Active incidents for map |
| GET | `/api/bwssb/schedule` | Water supply schedule by zone |

The government backend (`aquix_gov_backend.py`) additionally exposes `/api/gov/emergency-alert`, `/api/gov/sdg`, `/api/gov/drones`, and `/api/gov/shutdown`.

---

## 🗂️ Project Structure

```
.
├── aquix_backend.py        # Core Flask API (anomaly detection, ML models, agents)
├── aquix_gov_backend.py    # Government dashboard Flask API
├── aquix_gov.html          # Government Command Centre frontend
├── Drone.html              # Citizen-facing dashboard with drone visualization
├── agents.py                # Cohere-based decision & chat agent
├── app.py                   # Streamlit prototype/demo
└── app.json                 # Expo mobile app configuration
```

---
