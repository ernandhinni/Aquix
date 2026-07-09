from datetime import datetime


class DataStore:
    def __init__(self):
        self.history = []
        self.bookings = {}
        self.complaints = {}
        self.next_ticket = 1001

    def log_anomaly_run(self, anomaly_results, redistrib_plan):
        self.history.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "anomalies": anomaly_results,
            "redistribution": redistrib_plan,
        })

    def get_history(self, n):
        return self.history[-n:]

    def create_booking(self, data):
        ticket = f"B{self.next_ticket}"
        self.next_ticket += 1
        self.bookings[ticket] = {"status": "confirmed", "data": data}
        return ticket

    def create_complaint(self, data):
        ticket = f"C{self.next_ticket}"
        self.next_ticket += 1
        self.complaints[ticket] = {"status": "received", "data": data}
        return ticket

    def get_complaint_status(self, ticket_id):
        return self.complaints.get(ticket_id, {"status": "not_found"})

    def get_overview(self):
        return {
            "water_usage_l": 1200,
            "active_leaks": 3,
            "rainfall_mm": 45,
            "risk_level": "Medium",
            "anomaly_runs": len(self.history),
        }

    def get_zones(self):
        return [
            {"zone_id": "Z1", "name": "Koramangala", "risk": "normal"},
            {"zone_id": "Z2", "name": "Indiranagar", "risk": "high"},
            {"zone_id": "Z3", "name": "Whitefield", "risk": "medium"},
        ]
