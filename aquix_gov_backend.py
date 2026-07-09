"""
Aquix GOV Backend — BWSSB Command Centre
==========================================
Backend for aquix_gov.html (Government Dashboard).
Runs on port 5000 (matches const API = 'http://localhost:5000/api' in the HTML).

All endpoints used by the gov dashboard:
  GET  /api/health
  GET  /api/dashboard/overview
  GET  /api/dashboard/zones
  GET  /api/map/incidents
  GET  /api/map/heatmap
  GET  /api/bwssb/schedule
  GET  /api/anomaly/history
  POST /api/anomaly/detect
  POST /api/agents/run
  POST /api/services/book          (dispatch: tanker, repair team, drone, emergency)
  POST /api/complaints/submit
  GET  /api/complaints/status/<id>
  POST /api/predict/flood
  GET  /api/weather/<city>
  POST /api/gov/emergency-alert
  GET  /api/gov/sdg
  GET  /api/gov/drones
  POST /api/gov/shutdown

Setup:
  pip install flask flask-cors numpy scikit-learn

Run:
  python aquix_gov_backend.py
  python aquix_gov_backend.py --port 5000  (default — matches gov HTML)
"""

import os
import math
import argparse
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

# ── Optional deps ─────────────────────────────────────
try:
    import numpy as np
    from sklearn.ensemble import IsolationForest
    NP_AVAILABLE = True
except ImportError:
    NP_AVAILABLE = False

try:
    import requests as req_lib
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")

app = Flask(__name__)
CORS(app)  # Required — gov HTML is a local file, different origin


# ════════════════════════════════════════════════════════
# DATA STORE
# ════════════════════════════════════════════════════════
class DataStore:
    def __init__(self):
        self.bookings = {}
        self.complaints = {}
        self.incidents = {}
        self.emergency_alerts = []
        self.audit_log = []
        self.anomaly_log = []
        self.ticket_counter = 2000
        self._seed_data()

    def _seed_data(self):
        """Pre-populate realistic gov data shown in the dashboard."""
        now = datetime.now()

        # Seed incidents that match the HTML mock
        seed_incidents = [
            {"id": "INC-001", "zone": "Koramangala",     "type": "Pipe Burst",           "severity": "CRITICAL", "status": "ACTIVE",       "officer": "Sr. Engineer Ravi K.", "notes": "Isolation Forest >87% confidence"},
            {"id": "INC-002", "zone": "Whitefield",      "type": "High Flow Anomaly",    "severity": "HIGH",     "status": "IN_PROGRESS",  "officer": "Engineer Priya M.",    "notes": "Flow 156 L/s — threshold 120"},
            {"id": "INC-003", "zone": "BTM Layout",      "type": "Pressure Drop",        "severity": "HIGH",     "status": "ACTIVE",       "officer": "Engineer Suresh D.",   "notes": "Pressure 1.9 bar — critical"},
            {"id": "INC-004", "zone": "HSR Layout",      "type": "Leak Detected",        "severity": "MEDIUM",   "status": "MONITORING",   "officer": "Engineer Priya M.",    "notes": "Flow anomaly, team alerted"},
            {"id": "INC-005", "zone": "Electronic City", "type": "Supply Shutdown",      "severity": "MEDIUM",   "status": "SCHEDULED",    "officer": "Sr. Engineer Ravi K.", "notes": "Planned 06:30–10:00 maintenance"},
            {"id": "INC-006", "zone": "Indiranagar",     "type": "Usage Spike",          "severity": "LOW",      "status": "MONITORING",   "officer": "Auto",                 "notes": "9% above baseline"},
            {"id": "INC-007", "zone": "Marathahalli",    "type": "Water Quality Flag",   "severity": "MEDIUM",   "status": "TESTING",      "officer": "Lab Team B",           "notes": "pH 8.6 — slightly high"},
        ]
        for i in seed_incidents:
            i["reported"] = (now - timedelta(minutes=random.randint(5, 90))).strftime("%H:%M")
            i["created"] = now.isoformat()
            self.incidents[i["id"]] = i

        # Seed complaints
        seed_complaints = [
            {"ticket_id": "AQ-2011", "title": "No water supply since 2 days",     "zone": "Koramangala", "ward": "Ward 68", "type": "Supply",        "priority": "HIGH",   "status": "Filed"},
            {"ticket_id": "AQ-2012", "title": "Pipe burst near main road",        "zone": "Whitefield",  "ward": "Ward 84", "type": "Leak",          "priority": "HIGH",   "status": "Filed"},
            {"ticket_id": "AQ-2013", "title": "Water discoloration / smell",      "zone": "Hebbal",      "ward": "Ward 5",  "type": "Quality",       "priority": "MEDIUM", "status": "Filed"},
            {"ticket_id": "AQ-2014", "title": "Meter not reading correctly",      "zone": "Jayanagar",   "ward": "Ward 19", "type": "Meter",         "priority": "LOW",    "status": "Filed"},
            {"ticket_id": "AQ-2015", "title": "Pothole from water seepage",       "zone": "BTM Layout",  "ward": "Ward 65", "type": "Infrastructure","priority": "MEDIUM", "status": "Filed"},
        ]
        for c in seed_complaints:
            c["created"] = now.isoformat()
            self.complaints[c["ticket_id"]] = c

        # Seed audit log
        self.audit_log = [
            {"time": "08:12", "icon": "✅", "msg": "System initialized — all 17 API endpoints connected",       "actor": "Sr. Engineer Ravi K."},
            {"time": "08:15", "icon": "🔄", "msg": "Zone data synced from /api/dashboard/zones — 12 zones",    "actor": "Auto"},
            {"time": "08:18", "icon": "🚨", "msg": "Critical alert: Koramangala leak by Isolation Forest",     "actor": "AI System"},
            {"time": "08:22", "icon": "🚛", "msg": "Tanker dispatched to Koramangala — Ticket BK-2001",        "actor": "Sr. Engineer Ravi K."},
            {"time": "08:31", "icon": "🚁", "msg": "Drone D3 converged on BTM Layout — thermal confirmed",     "actor": "Drone Agent"},
        ]

    # ── Ticket helpers ─────────────────────────────────
    def next_ticket(self, prefix):
        self.ticket_counter += 1
        return f"{prefix}-{self.ticket_counter}"

    def add_audit(self, msg, icon="📋", actor="Sr. Engineer Ravi K."):
        now = datetime.now()
        self.audit_log.insert(0, {
            "time":  now.strftime("%H:%M"),
            "icon":  icon,
            "msg":   msg,
            "actor": actor,
        })
        if len(self.audit_log) > 100:
            self.audit_log.pop()

    # ── Zone data — 12 zones ───────────────────────────
    def get_zones(self):
        return [
            {"zone_id": "Z1",  "name": "Koramangala",    "risk": "HIGH",   "usage_pct": 87, "population": 8500, "pressure_bar": 1.8, "leak": True,  "flow_lps": 142, "lat": 12.9279, "lng": 77.6271},
            {"zone_id": "Z2",  "name": "Indiranagar",    "risk": "MEDIUM", "usage_pct": 64, "population": 6200, "pressure_bar": 3.1, "leak": False, "flow_lps": 88,  "lat": 12.9784, "lng": 77.6408},
            {"zone_id": "Z3",  "name": "Whitefield",     "risk": "HIGH",   "usage_pct": 91, "population": 9100, "pressure_bar": 2.2, "leak": True,  "flow_lps": 156, "lat": 12.9698, "lng": 77.7500},
            {"zone_id": "Z4",  "name": "Hebbal",         "risk": "LOW",    "usage_pct": 45, "population": 4300, "pressure_bar": 3.5, "leak": False, "flow_lps": 55,  "lat": 13.0354, "lng": 77.5970},
            {"zone_id": "Z5",  "name": "Jayanagar",      "risk": "LOW",    "usage_pct": 58, "population": 5600, "pressure_bar": 3.4, "leak": False, "flow_lps": 72,  "lat": 12.9250, "lng": 77.5938},
            {"zone_id": "Z6",  "name": "HSR Layout",     "risk": "MEDIUM", "usage_pct": 73, "population": 7200, "pressure_bar": 2.8, "leak": True,  "flow_lps": 105, "lat": 12.9081, "lng": 77.6476},
            {"zone_id": "Z7",  "name": "Marathahalli",   "risk": "MEDIUM", "usage_pct": 69, "population": 6800, "pressure_bar": 2.9, "leak": False, "flow_lps": 94,  "lat": 12.9591, "lng": 77.6972},
            {"zone_id": "Z8",  "name": "Yelahanka",      "risk": "LOW",    "usage_pct": 41, "population": 3900, "pressure_bar": 3.6, "leak": False, "flow_lps": 48,  "lat": 13.1007, "lng": 77.5963},
            {"zone_id": "Z9",  "name": "Electronic City","risk": "MEDIUM", "usage_pct": 77, "population": 7500, "pressure_bar": 2.7, "leak": False, "flow_lps": 108, "lat": 12.8458, "lng": 77.6603},
            {"zone_id": "Z10", "name": "Rajajinagar",    "risk": "LOW",    "usage_pct": 52, "population": 5100, "pressure_bar": 3.3, "leak": False, "flow_lps": 66,  "lat": 12.9907, "lng": 77.5530},
            {"zone_id": "Z11", "name": "BTM Layout",     "risk": "HIGH",   "usage_pct": 88, "population": 8200, "pressure_bar": 1.9, "leak": True,  "flow_lps": 138, "lat": 12.9166, "lng": 77.6101},
            {"zone_id": "Z12", "name": "Banashankari",   "risk": "LOW",    "usage_pct": 49, "population": 4700, "pressure_bar": 3.4, "leak": False, "flow_lps": 60,  "lat": 12.9255, "lng": 77.5468},
        ]

    # ── Command overview KPIs ──────────────────────────
    def get_overview(self):
        zones = self.get_zones()
        high_risk = sum(1 for z in zones if z["risk"] == "HIGH")
        leaks     = sum(1 for z in zones if z["leak"])
        return {
            "total_supply_ml":    12.4,
            "active_leaks":       leaks,
            "zones_monitored":    len(zones),
            "high_risk_zones":    high_risk,
            "flood_risk_percent": 42,
            "water_quality_ph":   7.2,
            "usage_today_l":      147820,
            "rainfall_mm":        45,
            "tankers_active":     7,
            "drones_active":      5,
            "complaints_open":    len([c for c in self.complaints.values() if c["status"] != "Resolved"]),
            "incidents_active":   len([i for i in self.incidents.values() if i["status"] in ("ACTIVE", "IN_PROGRESS")]),
            "equity_score":       0.84,
            "ai_risk_score":      47,
        }

    # ── Incidents ──────────────────────────────────────
    def get_incidents(self):
        return sorted(
            list(self.incidents.values()),
            key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}.get(x["severity"], 4),
        )

    def create_incident(self, data):
        inc_id = f"INC-{self.ticket_counter + 1}"
        self.ticket_counter += 1
        self.incidents[inc_id] = {
            "id":       inc_id,
            "zone":     data.get("zone"),
            "type":     data.get("type"),
            "severity": data.get("severity", "MEDIUM"),
            "status":   "ACTIVE",
            "officer":  data.get("officer", "Auto"),
            "notes":    data.get("notes", ""),
            "reported": datetime.now().strftime("%H:%M"),
            "created":  datetime.now().isoformat(),
        }
        return inc_id

    def update_incident(self, inc_id, status=None, officer=None):
        if inc_id in self.incidents:
            if status:  self.incidents[inc_id]["status"]  = status
            if officer: self.incidents[inc_id]["officer"] = officer
            return True
        return False

    # ── Dispatch / Bookings ────────────────────────────
    def create_booking(self, data):
        tid = self.next_ticket("BK")
        technicians = ["Team Alpha", "Team Bravo", "Team Charlie", "Unit D4", "Unit E2"]
        self.bookings[tid] = {
            **data,
            "ticket_id":  tid,
            "status":     "Confirmed",
            "technician": random.choice(technicians),
            "eta":        f"{random.randint(1, 6)}–{random.randint(2, 8)}hr",
            "created":    datetime.now().isoformat(),
        }
        self.add_audit(
            f"Dispatched {data.get('service_type','Resource')} to {data.get('zone','zone')} — Ticket {tid}",
            icon="🚛",
            actor=data.get("booked_by", "Gov Officer"),
        )
        return self.bookings[tid]

    # ── Complaints ─────────────────────────────────────
    def create_complaint(self, data):
        tid = self.next_ticket("AQ")
        self.complaints[tid] = {
            **data,
            "ticket_id": tid,
            "status":    "Filed",
            "created":   datetime.now().isoformat(),
        }
        return tid

    def get_ticket(self, ticket_id):
        if ticket_id in self.complaints:
            c = self.complaints[ticket_id]
            return {
                "ticket_id": ticket_id,
                "status":    c["status"],
                "details":   {k: v for k, v in c.items() if k not in ("ticket_id",)},
            }
        if ticket_id in self.bookings:
            b = self.bookings[ticket_id]
            return {
                "ticket_id": ticket_id,
                "status":    b["status"],
                "details":   {k: v for k, v in b.items() if k not in ("ticket_id",)},
            }
        if ticket_id in self.incidents:
            i = self.incidents[ticket_id]
            return {"ticket_id": ticket_id, "status": i["status"], "details": i}
        return {"ticket_id": ticket_id, "status": "Not Found"}

    def get_complaints(self):
        return list(self.complaints.values())

    # ── Drones ─────────────────────────────────────────
    def get_drones(self):
        return [
            {"id": "D1", "zone": "Koramangala",    "state": "CONVERGE", "battery": 68, "signal": "Strong", "mission": "Leak thermal scan"},
            {"id": "D2", "zone": "Whitefield",     "state": "CONVERGE", "battery": 74, "signal": "Strong", "mission": "Flow anomaly verify"},
            {"id": "D3", "zone": "BTM Layout",     "state": "CONVERGE", "battery": 61, "signal": "Medium", "mission": "Pressure drop inspect"},
            {"id": "D4", "zone": "Yelahanka",      "state": "PATROL",   "battery": 88, "signal": "Strong", "mission": "Routine patrol"},
            {"id": "D5", "zone": "Hebbal",         "state": "PATROL",   "battery": 91, "signal": "Strong", "mission": "Routine patrol"},
            {"id": "D6", "zone": "HSR Layout",     "state": "INSPECT",  "battery": 55, "signal": "Weak",   "mission": "Leak site inspection"},
            {"id": "D7", "zone": "Indiranagar",    "state": "PATROL",   "battery": 82, "signal": "Strong", "mission": "Routine patrol"},
            {"id": "D8", "zone": "Marathahalli",   "state": "PATROL",   "battery": 79, "signal": "Strong", "mission": "Quality flag review"},
        ]

    # ── SDG Tracker ────────────────────────────────────
    def get_sdg(self):
        return {
            "sdg6": {
                "label": "SDG 6 — Clean Water & Sanitation",
                "target": "Universal safe water access by 2030",
                "metrics": {
                    "safe_water_access_pct":    88.4,
                    "sanitation_coverage_pct":  74.2,
                    "water_quality_compliant":  91.7,
                    "leakage_reduction_yoy":    12.3,
                    "equity_gini_score":        0.84,
                    "nrw_percent":              24.1,   # Non-Revenue Water
                },
            },
            "sdg11": {
                "label": "SDG 11 — Sustainable Cities",
                "target": "Resilient water infrastructure",
                "metrics": {
                    "zones_smart_metered_pct":  67,
                    "ai_monitored_zones":       12,
                    "incident_resolution_hrs":  4.2,
                    "flood_risk_zones_managed": 3,
                },
            },
            "overall_score": 74,
            "trend": "+3.2% vs last quarter",
            "last_updated": datetime.now().strftime("%d %b %Y"),
        }

    # ── BWSSB Schedule ─────────────────────────────────
    def get_schedule(self):
        return [
            {"zone": "Electronic City", "type": "Planned Shutdown",    "start": "06:30", "end": "10:00", "status": "ACTIVE",    "reason": "Pipeline maintenance"},
            {"zone": "Koramangala",     "type": "Emergency Repair",    "start": "08:00", "end": "14:00", "status": "ACTIVE",    "reason": "Pipe burst — INC-001"},
            {"zone": "BTM Layout",      "type": "Pressure Restoration","start": "09:00", "end": "12:00", "status": "SCHEDULED", "reason": "Pressure drop — INC-003"},
            {"zone": "Yelahanka",       "type": "Quality Testing",     "start": "11:00", "end": "13:00", "status": "SCHEDULED", "reason": "Routine water quality check"},
            {"zone": "Rajajinagar",     "type": "Meter Reading",       "start": "14:00", "end": "17:00", "status": "SCHEDULED", "reason": "Monthly meter data collection"},
        ]

    # ── Heatmap ────────────────────────────────────────
    def get_heatmap(self):
        zones = self.get_zones()
        return [
            {
                "zone_id":   z["zone_id"],
                "name":      z["name"],
                "lat":       z.get("lat", 12.9716),
                "lng":       z.get("lng", 77.5946),
                "intensity": z["usage_pct"] / 100,
                "risk":      z["risk"],
                "leak":      z["leak"],
            }
            for z in zones
        ]


# ════════════════════════════════════════════════════════
# ANOMALY ENGINE
# ════════════════════════════════════════════════════════
class AnomalyEngine:

    def _z_flags(self, values):
        if len(values) < 2:
            return [False] * len(values)
        mean = sum(values) / len(values)
        std  = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)) or 1
        return [abs(v - mean) / std > 2.5 for v in values]

    def _iqr_flags(self, values):
        if not NP_AVAILABLE or len(values) < 4:
            return [False] * len(values)
        q1 = float(np.percentile(values, 25))
        q3 = float(np.percentile(values, 75))
        iqr = q3 - q1
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        return [v < lo or v > hi for v in values]

    def _if_flags(self, matrix):
        if not NP_AVAILABLE or len(matrix) < 4:
            return [False] * len(matrix)
        X     = np.array(matrix, dtype=float)
        preds = IsolationForest(contamination=0.2, random_state=42).fit_predict(X)
        return [p == -1 for p in preds]

    def detect(self, zones):
        flows     = [z.get("flow_lps", 0)       for z in zones]
        consumps  = [z.get("consumption_l", 0)  for z in zones]
        pressures = [z.get("pressure_bar", 3.0) for z in zones]
        per_cap   = [z.get("consumption_l", 0) / max(z.get("population", 1), 1) for z in zones]

        z_flow  = self._z_flags(flows)
        z_cons  = self._z_flags(consumps)
        iq_flow = self._iqr_flags(flows)
        iq_pc   = self._iqr_flags(per_cap)
        if_flag = self._if_flags([[f, c, p] for f, c, p in zip(flows, consumps, pressures)])

        results = []
        for i, z in enumerate(zones):
            vote       = sum([z_flow[i], z_cons[i], iq_flow[i], iq_pc[i], if_flag[i]])
            is_anomaly = vote >= 2
            pressure   = z.get("pressure_bar", 3.0)
            flow       = z.get("flow_lps", 0)
            pc         = per_cap[i]

            if is_anomaly:
                if pressure < 2.0 and flow > 100:
                    atype     = "LEAK"
                    severity  = "CRITICAL" if pressure < 1.5 else "HIGH"
                    just      = f"Pressure {pressure:.1f} bar (↓ low) + flow {flow:.0f} L/s (↑ high). {vote}/5 detectors."
                else:
                    atype     = "OVERCONSUMPTION"
                    severity  = "HIGH" if vote >= 4 else "MEDIUM"
                    just      = f"Per-capita {pc:.1f} L/person above norm. Ensemble {vote}/5."
            else:
                atype, severity, just = "NORMAL", "LOW", "All sensors within expected range."

            results.append({
                "zone_id":       z.get("zone_id"),
                "name":          z.get("name", z.get("zone_id")),
                "is_anomaly":    is_anomaly,
                "anomaly_type":  atype,
                "severity":      severity,
                "justification": just,
                "vote_score":    vote,
                "metrics": {
                    "pressure_bar":  pressure,
                    "flow_lps":      flow,
                    "consumption_l": z.get("consumption_l", 0),
                    "per_capita_l":  round(pc, 2),
                    "population":    z.get("population", 0),
                },
            })
        return results


# ════════════════════════════════════════════════════════
# REDISTRIBUTION ENGINE
# ════════════════════════════════════════════════════════
class RedistributionEngine:
    def plan(self, zones, anomaly_results):
        anomalous_ids = {r["zone_id"] for r in anomaly_results if r["is_anomaly"]}
        normal_zones  = [z for z in zones if z.get("zone_id") not in anomalous_ids]

        total_pop  = sum(z.get("population", 0) for z in zones) or 1
        fair_share = {z["zone_id"]: z.get("population", 0) / total_pop for z in zones}

        transfers = []
        for r in anomaly_results:
            if not r["is_anomaly"] or not normal_zones:
                continue
            need  = round(fair_share.get(r["zone_id"], 0.1) * 100 * 1000)
            donor = max(normal_zones, key=lambda x: x.get("consumption_l", 0))
            transfers.append({
                "from_zone": donor.get("name", donor.get("zone_id")),
                "to_zone":   r["name"],
                "volume_l":  need,
                "priority":  r["severity"],
            })

        consumps = [z.get("consumption_l", 1) / max(z.get("population", 1), 1) for z in zones]
        equity_score = 1.0
        if len(consumps) > 1:
            mean_c = sum(consumps) / len(consumps)
            gini   = sum(abs(a - b) for a in consumps for b in consumps) / (
                2 * len(consumps) ** 2 * max(mean_c, 1)
            )
            equity_score = round(1 - gini, 2)

        return {
            "transfers":    transfers,
            "equity_score": equity_score,
            "explanation":  (
                f"Population-proportional redistribution. "
                f"Equity score: {equity_score:.0%}. "
                f"{len(transfers)} transfer(s) planned."
            ),
        }


# ════════════════════════════════════════════════════════
# INIT
# ════════════════════════════════════════════════════════
db             = DataStore()
anomaly_engine = AnomalyEngine()
redistrib      = RedistributionEngine()


def _build_summary(anomaly_results, redistrib_plan):
    anomalous = [z for z in anomaly_results if z["is_anomaly"]]
    return {
        "total_zones":     len(anomaly_results),
        "anomalous_zones": len(anomalous),
        "leak_suspects":   sum(1 for z in anomalous if z["anomaly_type"] == "LEAK"),
        "overconsumption": sum(1 for z in anomalous if z["anomaly_type"] == "OVERCONSUMPTION"),
        "equity_score":    redistrib_plan["equity_score"],
        "alert_level":     "CRITICAL" if len(anomalous) >= 3 else "WARNING" if anomalous else "NORMAL",
    }


def _mock_weather():
    return {
        "city": "Bengaluru", "temp": 28, "feels_like": 32,
        "humidity": 78, "description": "thunderstorm with rain",
        "wind_speed": 5.1, "rain_1h": 2.4,
        "forecast": [
            {"day": "Mon", "icon": "🌤️", "temp": 30},
            {"day": "Tue", "icon": "⛈️",  "temp": 26},
            {"day": "Wed", "icon": "🌧️", "temp": 24},
            {"day": "Thu", "icon": "☀️",  "temp": 33},
        ],
    }


# ════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════

@app.route("/api/health")
def health():
    return jsonify({
        "status":          "ok",
        "version":         "4.0-gov",
        "engine":          "Aquix GOV",
        "numpy_sklearn":   NP_AVAILABLE,
        "zones_loaded":    len(db.get_zones()),
        "incidents_active":len([i for i in db.incidents.values() if i["status"] == "ACTIVE"]),
        "uptime":          "Running",
    })


# ── Dashboard ──────────────────────────────────────────
@app.route("/api/dashboard/overview")
def dashboard_overview():
    return jsonify(db.get_overview())


@app.route("/api/dashboard/zones")
def dashboard_zones():
    return jsonify(db.get_zones())


# ── Incidents ──────────────────────────────────────────
@app.route("/api/map/incidents")
def map_incidents():
    """Gov dashboard incidents table and overview zone table."""
    return jsonify(db.get_incidents())


@app.route("/api/map/incidents/<inc_id>", methods=["PATCH"])
def update_incident(inc_id):
    d = request.get_json(force=True)
    ok = db.update_incident(inc_id, status=d.get("status"), officer=d.get("officer"))
    if ok:
        db.add_audit(f"Incident {inc_id} updated — status: {d.get('status','')}", "📋")
        return jsonify({"success": True, "incident": db.incidents[inc_id]})
    return jsonify({"success": False, "error": "Incident not found"}), 404


@app.route("/api/map/incidents", methods=["POST"])
def create_incident():
    d = request.get_json(force=True)
    inc_id = db.create_incident(d)
    db.add_audit(f"New incident created: {inc_id} — {d.get('zone')} / {d.get('type')}", "🚨")
    return jsonify({"success": True, "incident_id": inc_id, "incident": db.incidents[inc_id]})


# ── Heatmap ────────────────────────────────────────────
@app.route("/api/map/heatmap")
def map_heatmap():
    return jsonify(db.get_heatmap())


# ── BWSSB Schedule ─────────────────────────────────────
@app.route("/api/bwssb/schedule")
def bwssb_schedule():
    return jsonify(db.get_schedule())


# ── Anomaly Detection ──────────────────────────────────
@app.route("/api/anomaly/detect", methods=["POST"])
def detect_anomalies():
    body  = request.get_json(force=True)
    zones = body.get("zones", db.get_zones())
    if not zones:
        return jsonify({"error": "No zone data"}), 400

    results     = anomaly_engine.detect(zones)
    redist_plan = redistrib.plan(zones, results)
    db.anomaly_log.append({
        "timestamp":      datetime.now().isoformat(),
        "anomalies":      results,
        "redistribution": redist_plan,
    })
    if len(db.anomaly_log) > 50:
        db.anomaly_log.pop(0)

    db.add_audit("Anomaly detection run completed", "🔍", "AI System")
    return jsonify({
        "anomalies":      results,
        "redistribution": redist_plan,
        "summary":        _build_summary(results, redist_plan),
    })


@app.route("/api/anomaly/history")
def anomaly_history():
    n = int(request.args.get("n", 10))
    return jsonify(db.anomaly_log[-n:])


# ── Multi-Agent Run ────────────────────────────────────
@app.route("/api/agents/run", methods=["POST"])
def agents_run():
    zones       = db.get_zones()
    results     = anomaly_engine.detect(zones)
    redist_plan = redistrib.plan(zones, results)

    anomalous   = [r for r in results if r["is_anomaly"]]
    leaks       = [r for r in anomalous if r["anomaly_type"] == "LEAK"]
    alert_level = "CRITICAL" if len(anomalous) >= 3 else "WARNING" if anomalous else "NORMAL"

    db.add_audit(f"All agents run — {alert_level}: {len(leaks)} leak(s) detected", "🤖", "AI System")

    return jsonify({
        "prediction_agent": {
            "agent":           "Prediction Agent",
            "flood_risk":      42,
            "demand_forecast": "147,820 L today",
            "proactive_alerts": [
                "🌧️ Moderate rain forecast — monitoring sensitivity elevated.",
                f"🌊 {len(leaks)} active leak(s) — dispatch recommended.",
            ],
        },
        "leak_agent": {
            "agent":            "Leak Detection Agent",
            "leaks_detected":   len(leaks),
            "zones_flagged":    [r["name"] for r in leaks],
            "summary":          f"{len(leaks)} leak(s) confirmed by ensemble model.",
        },
        "decision_agent": {
            "agent":        "Decision Agent",
            "alert_level":  alert_level,
            "equity_score": redist_plan["equity_score"],
            "recommendations": [
                {"action": "DISPATCH_REPAIR_TEAM", "zone": r["name"], "priority": r["severity"]}
                for r in leaks
            ],
        },
        "redistribution": redist_plan,
        "summary":        _build_summary(results, redist_plan),
    })


# ── Resource Dispatch / Booking ────────────────────────
@app.route("/api/services/book", methods=["POST"])
def book_service():
    """
    Gov dashboard dispatches resources via this endpoint.
    Accepts: service_type, zone, priority, notes, booked_by
    Returns: ticket_id, technician, eta (for the dispatch modal result display)
    """
    d = request.get_json(force=True)
    if not d.get("zone"):
        return jsonify({"success": False, "error": "zone is required"}), 400

    booking = db.create_booking(d)
    return jsonify({
        "success":    True,
        "ticket_id":  booking["ticket_id"],
        "technician": booking["technician"],
        "eta":        booking["eta"],
        "status":     booking["status"],
        "message":    f"Dispatched! Ticket {booking['ticket_id']} · {booking['technician']} · ETA {booking['eta']}",
    })


# ── Complaints ─────────────────────────────────────────
@app.route("/api/complaints/submit", methods=["POST"])
def submit_complaint():
    d = request.get_json(force=True)
    tid = db.create_complaint(d)
    return jsonify({"success": True, "ticket_id": tid})


@app.route("/api/complaints/status/<ticket_id>")
def complaint_status(ticket_id):
    """Gov complaint lookup — returns full details dict for the gov dashboard table."""
    return jsonify(db.get_ticket(ticket_id))


@app.route("/api/complaints/list")
def complaints_list():
    return jsonify(db.get_complaints())


# ── Flood Prediction ───────────────────────────────────
@app.route("/api/predict/flood", methods=["POST"])
def predict_flood():
    d = request.get_json(force=True)
    mi  = float(d.get("monsoon_intensity", 5))
    td  = float(d.get("topography_drainage", 5))
    rm  = float(d.get("river_management", 5))
    def_ = float(d.get("deforestation", 5))

    score = (mi * 0.40 + (10 - td) * 0.25 + (10 - rm) * 0.20 + def_ * 0.15) * 10
    score = round(min(100, max(0, score)))
    risk  = "LOW" if score < 30 else "MODERATE" if score < 60 else "HIGH" if score < 80 else "CRITICAL"

    ps = round(min(100, score * 0.9 + mi * 2))
    ll = round(min(100, ps * 0.85))

    alerts = []
    if score >= 60: alerts.append("⚠️ High pipeline stress — pre-position repair teams.")
    if score >= 40: alerts.append("💧 Increase monitoring sensitivity across all zones.")
    if mi >= 7:     alerts.append("🌧️ Severe rain — pre-emptive tanker redistribution advised.")

    db.add_audit(f"Flood prediction run — Risk: {risk} ({score}%)", "🌊", "Gov Officer")
    return jsonify({
        "flood_probability":           score,
        "risk_level":                  risk,
        "pipeline_stress_probability": ps,
        "leak_likelihood_during_rain": ll,
        "smart_alerts":                alerts,
        "recommendation": (
            "Activate emergency protocol immediately." if score >= 80
            else "Temporary shutoff of low-priority zones." if score >= 60
            else "Enhanced monitoring required." if score >= 40
            else "Normal operations."
        ),
    })


# ── Weather ────────────────────────────────────────────
@app.route("/api/weather/<city>")
def weather(city):
    if REQUESTS_AVAILABLE and OPENWEATHER_KEY:
        try:
            r = req_lib.get(
                f"https://api.openweathermap.org/data/2.5/weather"
                f"?q={city}&appid={OPENWEATHER_KEY}&units=metric",
                timeout=5,
            )
            wd = r.json()
            return jsonify({
                "city":        city,
                "temp":        wd["main"]["temp"],
                "feels_like":  wd["main"]["feels_like"],
                "humidity":    wd["main"]["humidity"],
                "description": wd["weather"][0]["description"],
                "wind_speed":  wd["wind"]["speed"],
                "rain_1h":     wd.get("rain", {}).get("1h", 0),
                "forecast": [
                    {"day": "Mon", "icon": "🌤️", "temp": 30},
                    {"day": "Tue", "icon": "⛈️",  "temp": 26},
                    {"day": "Wed", "icon": "🌧️", "temp": 24},
                    {"day": "Thu", "icon": "☀️",  "temp": 33},
                ],
            })
        except Exception:
            pass
    return jsonify(_mock_weather())


# ── Gov-specific endpoints ─────────────────────────────

@app.route("/api/gov/emergency-alert", methods=["POST"])
def emergency_alert():
    """Gov emergency alert modal — POST from issueEmergencyAlert()."""
    d = request.get_json(force=True)
    alert = {
        "type":    d.get("type", "General Alert"),
        "zones":   d.get("zones", "All"),
        "message": d.get("message", ""),
        "issued_by": d.get("officer", "Gov Officer"),
        "issued_at": datetime.now().isoformat(),
    }
    db.emergency_alerts.append(alert)
    db.add_audit(
        f"EMERGENCY ALERT issued: {alert['type']} — Zones: {alert['zones']}",
        "🚨",
        alert["issued_by"],
    )
    return jsonify({"success": True, "alert": alert, "broadcast_zones": alert["zones"]})


@app.route("/api/gov/emergency-alerts")
def list_emergency_alerts():
    return jsonify(db.emergency_alerts[-20:])


@app.route("/api/gov/drones")
def drones():
    return jsonify(db.get_drones())


@app.route("/api/gov/sdg")
def sdg():
    return jsonify(db.get_sdg())


@app.route("/api/gov/audit")
def audit_log():
    n = int(request.args.get("n", 50))
    return jsonify(db.audit_log[:n])


@app.route("/api/gov/shutdown", methods=["POST"])
def zone_shutdown():
    """Gov shutdown modal — shut down water supply to a zone."""
    d = request.get_json(force=True)
    zone    = d.get("zone")
    reason  = d.get("reason", "Maintenance")
    officer = d.get("officer", "Gov Officer")
    if not zone:
        return jsonify({"success": False, "error": "zone required"}), 400

    tid = db.next_ticket("SD")
    db.add_audit(f"Zone SHUTDOWN initiated: {zone} — Reason: {reason} — Ref: {tid}", "⚠️", officer)
    return jsonify({
        "success":    True,
        "shutdown_id": tid,
        "zone":       zone,
        "reason":     reason,
        "initiated_at": datetime.now().isoformat(),
        "estimated_restore": (datetime.now() + timedelta(hours=4)).strftime("%H:%M"),
        "message":    f"Shutdown initiated for {zone}. Ref: {tid}. Estimated restore: +4hr.",
    })


@app.route("/api/gov/reports/generate", methods=["POST"])
def generate_report():
    d    = request.get_json(force=True)
    rtype = d.get("report_type", "Leak Detection Report")
    fmt   = d.get("format", "PDF")
    db.add_audit(f"Report generated: {rtype} ({fmt})", "📊")
    return jsonify({
        "success":     True,
        "report_type": rtype,
        "format":      fmt,
        "generated_at": datetime.now().isoformat(),
        "download_url": f"/api/gov/reports/download/{rtype.replace(' ','_').lower()}.{fmt.lower()}",
        "message":     f"{rtype} ready for download.",
    })


# ════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aquix GOV Backend")
    parser.add_argument("--port", type=int, default=5007,
                        help="Port (default: 5007 — matches aquix_gov.html)")
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    print(f"\n🏛️  Aquix GOV Backend v4.0 — http://localhost:{args.port}/api")
    print(f"   ➜  aquix_gov.html expects port 5000  (const API = 'http://localhost:5007/api')")
    print(f"   NumPy / sklearn: {'✅' if NP_AVAILABLE else '⚠️  pip install numpy scikit-learn'}")
    print()
    print("   Key endpoints:")
    print(f"   GET  http://localhost:{args.port}/api/dashboard/overview")
    print(f"   GET  http://localhost:{args.port}/api/dashboard/zones")
    print(f"   GET  http://localhost:{args.port}/api/map/incidents")
    print(f"   POST http://localhost:{args.port}/api/services/book")
    print(f"   GET  http://localhost:{args.port}/api/complaints/status/<id>")
    print(f"   GET  http://localhost:{args.port}/api/gov/drones")
    print(f"   GET  http://localhost:{args.port}/api/gov/sdg")
    print(f"   POST http://localhost:{args.port}/api/gov/emergency-alert")
    print(f"   POST http://localhost:{args.port}/api/gov/shutdown")
    print()

    app.run(host=args.host, port=args.port, debug=True)
