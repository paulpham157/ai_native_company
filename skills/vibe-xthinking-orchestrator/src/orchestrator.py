import uuid

from evidence_tracker import EvidenceTracker
from agent_runner import AgentRunner
from checkpoint import Checkpoint, CheckpointResult, AutoCheckpoint
from context_provider import ContextProvider
from evidence_validator import EvidenceValidator


class XThinkingOrchestrator:
    PHASE_GROUPS = {
        "topic": [
            {
                "major_phase": "research",
                "checkpoint_after": True,
                "agents": [("research", "Researcher")],
            },
            {
                "major_phase": "thinking",
                "checkpoint_after": True,
                "agents": [
                    ("thinking", "Explicit Thinker"),
                    ("thinking", "Value Chain Analyst"),
                    ("synthesis", "Synthesizer"),
                ],
            },
            {
                "major_phase": "validation",
                "checkpoint_after": False,
                "agents": [("validation", "Validator")],
            },
        ],
    }

    def __init__(self, mode, agent_runner, evidence_tracker=None, checkpoint=None, context_provider=None, evidence_validator=None):
        if mode not in self.PHASE_GROUPS:
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode
        self.agent_runner = agent_runner
        self.evidence_tracker = evidence_tracker if evidence_tracker else EvidenceTracker()
        self.checkpoint = checkpoint
        self.context_provider = context_provider
        self.evidence_validator = evidence_validator
        self.context_provider = context_provider

    def _build_agent_context(self, handoff_brief, topic, phase_label, agent_name, phases):
        context = {
            "handoff": handoff_brief,
            "topic": topic,
            "phase": phase_label,
            "previous_outputs": [p["output"] for p in phases],
        }
        if self.context_provider:
            enriched = self.context_provider.enrich(handoff_brief, phase_label, agent_name)
            context.update(enriched)
        return context

    def execute(self, handoff_brief, analysis_id=None):
        topic = handoff_brief.get("context", {}).get("industry_context", "Unknown topic")
        if not analysis_id:
            analysis_id = f"ta-{uuid.uuid4().hex[:8]}"

        phases = []
        evidence_chain = []
        all_evidence = []
        insights = []

        for group in self.PHASE_GROUPS[self.mode]:
            major_phase = group["major_phase"]
            group_outputs = {}

            for phase_label, agent_name in group["agents"]:
                context = self._build_agent_context(
                    handoff_brief, topic, phase_label, agent_name, phases,
                )

                output = self.agent_runner.run(agent_name, phase_label, context)

                phases.append({
                    "phase": phase_label,
                    "agent": agent_name,
                    "output": output,
                })
                group_outputs[agent_name] = output

                agent_evidence = output.get("evidence", [])
                for e in agent_evidence:
                    evidence_chain.append({
                        "agent": agent_name,
                        "claim": e.get("claim", ""),
                        "confidence": e.get("confidence", 0.0),
                        "source": e.get("source", ""),
                    })
                    all_evidence.append({
                        "claim": e.get("claim", ""),
                        "confidence": e.get("confidence", 0.0),
                        "source": e.get("source", ""),
                    })

            if group["checkpoint_after"] and self.checkpoint:
                cp_result = self.checkpoint.pause(
                    phase=major_phase,
                    output=group_outputs,
                    context={
                        "phase_results": list(phases),
                        "handoff": handoff_brief,
                    },
                )
                if cp_result.action == "revise":
                    revised = self._revise_group(
                        group, handoff_brief, topic,
                        phases, evidence_chain, all_evidence,
                        cp_result.feedback,
                    )
                    phases, evidence_chain, all_evidence = revised

        tracking_result = self.evidence_tracker.track(
            evidence_chain=evidence_chain,
            analysis_ref=analysis_id,
        )

        validation_result = None
        if self.evidence_validator:
            validation_result = self.evidence_validator.assess(evidence_chain)

        for e in evidence_chain:
            insights.append({
                "claim": e["claim"],
                "evidence": e["source"],
                "source": e["agent"],
            })

        return {
            "analysis_id": analysis_id,
            "topic": topic,
            "mode": self.mode,
            "phases": phases,
            "insights": insights,
            "evidence": all_evidence,
            "confidence_score": tracking_result["confidence_score"],
            "need_review": tracking_result["need_review"],
            "validation": validation_result,
        }

    def _revise_group(self, group, handoff_brief, topic, phases, evidence_chain, all_evidence, feedback):
        for _ in range(len(group["agents"])):
            phases.pop()
        trimmed_chain = []
        trimmed_evidence = []
        for e in evidence_chain:
            if e["agent"] not in [a for _, a in group["agents"]]:
                trimmed_chain.append(e)
        for e in all_evidence:
            if e["claim"] not in [ec["claim"] for ec in trimmed_chain]:
                trimmed_evidence.append(e)
            else:
                pass  # rebuilt below

        for phase_label, agent_name in group["agents"]:
            prev_outputs = [p["output"] for p in phases]
            context = self._build_agent_context(handoff_brief, topic, phase_label, agent_name, phases)
            context["feedback"] = feedback
            context["previous_outputs"] = prev_outputs
            output = self.agent_runner.run(agent_name, phase_label, context)
            phases.append({
                "phase": phase_label,
                "agent": agent_name,
                "output": output,
            })
            agent_evidence = output.get("evidence", [])
            for e in agent_evidence:
                trimmed_chain.append({
                    "agent": agent_name,
                    "claim": e.get("claim", ""),
                    "confidence": e.get("confidence", 0.0),
                    "source": e.get("source", ""),
                })
                trimmed_evidence.append({
                    "claim": e.get("claim", ""),
                    "confidence": e.get("confidence", 0.0),
                    "source": e.get("source", ""),
                })

        return phases, trimmed_chain, trimmed_evidence
