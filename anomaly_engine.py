import numpy as np


class AnomalyEngine:
    def detect(self, zones):
        if not zones:
            return []

        consumption = np.array([float(z.get("consumption_l", 0)) for z in zones])
        flows = np.array([float(z.get("flow_lps", 0)) for z in zones])
        pressures = np.array([float(z.get("pressure_bar", 0)) for z in zones])

        def z_scores(values):
            std = values.std()
            if std == 0:
                return np.zeros_like(values, dtype=float)
            return np.abs((values - values.mean()) / std)

        consumption_z = z_scores(consumption)
        flow_z = z_scores(flows)
        pressure_z = z_scores(pressures)

        results = []
        for i, zone in enumerate(zones):
            leak_score = max(flow_z[i], pressure_z[i])
            demand_score = consumption_z[i]
            is_leak = (
                leak_score >= 1.5 and flows[i] > flows.mean()
            ) or (pressures[i] < 1.5 and flows[i] > 100)
            is_overuse = (
                demand_score >= 1.5 and consumption[i] > consumption.mean()
            ) or consumption[i] > 2500
            anomaly_type = "LEAK" if is_leak else "OVERCONSUMPTION" if is_overuse else "NORMAL"

            results.append({
                "zone_id": zone.get("zone_id", f"Z{i + 1}"),
                "name": zone.get("name", f"Zone {i + 1}"),
                "is_anomaly": anomaly_type != "NORMAL",
                "anomaly_type": anomaly_type,
                "score": round(float(max(leak_score, demand_score)), 3),
                "pressure_bar": float(zone.get("pressure_bar", 0)),
                "flow_lps": float(zone.get("flow_lps", 0)),
                "consumption_l": float(zone.get("consumption_l", 0)),
            })

        return results
