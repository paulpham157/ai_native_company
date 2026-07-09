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
        "problem": [
            {
                "major_phase": "analysis",
                "checkpoint_after": False,
                "agents": [("analysis", "Problem Analyst")],
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
        if self.mode == "problem":
            return self._execute_problem(handoff_brief, analysis_id)

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
                "claim": e.get("claim", ""),
                "evidence_source": e.get("source", ""),
                "agent": e.get("agent", ""),
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
        revise_agents = {a for _, a in group["agents"]}
        for _ in range(len(group["agents"])):
            phases.pop()

        new_chain = [e for e in evidence_chain if e.get("agent") not in revise_agents]
        new_evidence = [
            {"claim": e.get("claim", ""), "confidence": e.get("confidence", 0.0), "source": e.get("source", "")}
            for e in new_chain
        ]

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
                new_chain.append({
                    "agent": agent_name,
                    "claim": e.get("claim", ""),
                    "confidence": e.get("confidence", 0.0),
                    "source": e.get("source", ""),
                })
                new_evidence.append({
                    "claim": e.get("claim", ""),
                    "confidence": e.get("confidence", 0.0),
                    "source": e.get("source", ""),
                })

        return phases, new_chain, new_evidence

    def _execute_problem(self, handoff_brief, analysis_id):
        problem = handoff_brief.get("context", {}).get("industry_context", "Unknown problem")
        if not analysis_id:
            analysis_id = f"pa-{uuid.uuid4().hex[:8]}"

        context = {
            "handoff": handoff_brief,
            "problem": problem,
            "analysis_id": analysis_id,
        }
        if self.context_provider:
            enriched = self.context_provider.enrich(handoff_brief, "analysis", "Problem Analyst")
            context.update(enriched)

        output = self.agent_runner.run("Problem Analyst", "analysis", context)

        evidence_chain = []
        all_evidence = []
        for e in output.get("evidence", []):
            evidence_chain.append({
                "agent": "Problem Analyst",
                "claim": e.get("claim", ""),
                "confidence": e.get("confidence", 0.0),
                "source": e.get("source", ""),
            })
            all_evidence.append({
                "claim": e.get("claim", ""),
                "confidence": e.get("confidence", 0.0),
                "source": e.get("source", ""),
            })

        insights = [{
            "claim": e.get("claim", ""),
            "evidence_source": e.get("source", ""),
            "agent": "Problem Analyst",
        } for e in evidence_chain]

        tracking_result = self.evidence_tracker.track(
            evidence_chain=evidence_chain,
            analysis_ref=analysis_id,
        )

        validation_result = None
        if self.evidence_validator:
            validation_result = self.evidence_validator.assess(evidence_chain)

        return {
            "analysis_id": analysis_id,
            "problem": problem,
            "mode": self.mode,
            "framework": output.get("framework", "5-whys"),
            "root_causes": output.get("root_causes", []),
            "recommendations": output.get("recommendations", []),
            "evidence": all_evidence,
            "insights": insights,
            "confidence_score": tracking_result["confidence_score"],
            "need_review": tracking_result["need_review"],
            "validation": validation_result,
        }
