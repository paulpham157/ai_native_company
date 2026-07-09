class EvidenceValidator:
    def assess(self, evidence_chain):
        gaps = []
        issues = []
        conflicts = self._find_duplicates(evidence_chain)
        gapped_indices = set()

        for i, entry in enumerate(evidence_chain):
            source = entry.get("source", "")
            claim = entry.get("claim", "")
            conf = entry.get("confidence", 0)

            if not source.strip():
                gaps.append({
                    "agent": entry.get("agent", ""),
                    "claim": claim,
                    "issue": "Missing evidence source",
                })
                gapped_indices.add(i)

            if not claim.strip():
                gaps.append({
                    "agent": entry.get("agent", ""),
                    "claim": claim,
                    "issue": "Empty claim",
                })
                gapped_indices.add(i)

            if not (0 <= conf <= 1):
                issues.append({
                    "agent": entry.get("agent", ""),
                    "claim": claim,
                    "issue": f"Confidence {conf} out of range [0, 1]",
                })

        valid_count = len(evidence_chain) - len(gapped_indices)
        assessment = self._generate_assessment(len(evidence_chain), len(gaps), len(conflicts), len(issues))

        return {
            "conflicts": conflicts,
            "gaps": gaps,
            "issues": issues,
            "total_evidence": len(evidence_chain),
            "valid_count": valid_count,
            "assessment": assessment,
        }

    def _find_duplicates(self, evidence_chain):
        seen = {}
        conflicts = []
        for entry in evidence_chain:
            claim = entry.get("claim", "").strip().lower()
            if claim and claim in seen:
                conflicts.append({
                    "claim": entry.get("claim", ""),
                    "agents": [seen[claim]["agent"], entry.get("agent", "")],
                    "confidences": [seen[claim]["confidence"], entry.get("confidence", 0)],
                })
            elif claim:
                seen[claim] = entry
        return conflicts

    def _generate_assessment(self, total, gaps, conflicts, issues):
        parts = []
        if total == 0:
            return "No evidence to validate."
        if gaps == 0 and conflicts == 0 and issues == 0:
            parts.append(f"All {total} evidence entries valid.")
        else:
            parts.append(f"{total} evidence entries checked:")
            if gaps > 0:
                parts.append(f"{gaps} gap(s) — missing sources or empty claims")
            if conflicts > 0:
                parts.append(f"{conflicts} conflict(s) — duplicate claims detected")
            if issues > 0:
                parts.append(f"{issues} issue(s) — out-of-range values")
        return " ".join(parts)
