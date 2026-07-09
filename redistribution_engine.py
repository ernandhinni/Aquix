class RedistributionEngine:
    def plan(self, zones, anomaly_results):
        anomalous_ids = {
            item["zone_id"]
            for item in anomaly_results
            if item.get("is_anomaly")
        }
        stable = [z for z in zones if z.get("zone_id") not in anomalous_ids]
        affected = [z for z in zones if z.get("zone_id") in anomalous_ids]

        transfers = []
        if stable and affected:
            per_zone = 500
            for target in affected:
                source = stable[len(transfers) % len(stable)]
                transfers.append({
                    "from_zone": source.get("zone_id", "stable"),
                    "to_zone": target.get("zone_id", "affected"),
                    "volume_l": per_zone,
                    "reason": "Temporary support for anomalous zone",
                })

        equity_score = max(0.0, 1.0 - (len(affected) / max(len(zones), 1)))
        return {
            "transfers": transfers,
            "equity_score": round(equity_score, 3),
            "affected_zones": len(affected),
        }
