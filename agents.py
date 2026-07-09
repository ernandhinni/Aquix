import os

import cohere


class AquixAgents:
    def __init__(self):
        api_key = os.getenv("COHERE_API_KEY")
        self.client = cohere.Client(api_key) if api_key else None

    def decide(self, anomaly_results, redistrib_plan):
        anomalous = [item for item in anomaly_results if item.get("is_anomaly")]
        if not anomalous:
            recommendation = "System stable. Continue routine monitoring."
        elif len(anomalous) >= 3:
            recommendation = "Escalate to emergency operations and deploy field teams."
        else:
            recommendation = "Dispatch inspection team and apply redistribution plan."

        return {
            "severity": "critical" if len(anomalous) >= 3 else "warning" if anomalous else "normal",
            "recommendation": recommendation,
            "transfers_planned": len(redistrib_plan.get("transfers", [])),
        }

    def chat(self, message, language="en"):
        if not message.strip():
            return "Please enter a question."
        if not self.client:
            return "Cohere API key is not configured."

        response = self.client.chat(
            model="command-a-03-2025",
            message=message,
            max_tokens=180,
        )
        return response.text.strip()
