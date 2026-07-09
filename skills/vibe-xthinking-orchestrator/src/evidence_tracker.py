class EvidenceTracker:
    DEFAULT_WEIGHTS = {
        "Researcher": 0.15,
        "Explicit Thinker": 0.20,
        "Value Chain Analyst": 0.20,
        "Synthesizer": 0.20,
        "Validator": 0.25,
    }

    DEFAULT_THRESHOLD = 0.7

    def __init__(self, weights=None, confidence_threshold=0.7):
        self.weights = weights if weights else self.DEFAULT_WEIGHTS.copy()
        self.confidence_threshold = confidence_threshold

    def aggregate(self, evidence_chain):
        if not evidence_chain:
            return 0.0
        weighted_sum = 0.0
        total_weight = 0.0
        for entry in evidence_chain:
            agent = entry.get("agent", "")
            conf = entry.get("confidence", 0.0)
            w = self.weights.get(agent, 0.0)
            weighted_sum += conf * w
            total_weight += w
        if total_weight == 0.0:
            return 0.0
        return round(weighted_sum / total_weight, 2)

    def needs_review(self, evidence_chain):
        return self.aggregate(evidence_chain) < self.confidence_threshold

    def track(self, evidence_chain, analysis_ref="", tracking_id=""):
        agg = self.aggregate(evidence_chain)
        nr = self.needs_review(evidence_chain)
        if not tracking_id:
            tracking_id = f"et-auto-{id(evidence_chain)}"
        return {
            "tracking_id": tracking_id,
            "analysis_ref": analysis_ref,
            "evidence_chain": evidence_chain,
            "aggregate_confidence": agg,
            "evidence": [
                {"claim": e["claim"], "confidence": e["confidence"], "source": e["source"]}
                for e in evidence_chain
            ],
            "confidence_score": agg,
            "need_review": nr,
        }
