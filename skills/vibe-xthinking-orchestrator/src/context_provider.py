from pathlib import Path


class ContextProvider:
    def enrich(self, handoff_brief, phase, agent_name):
        raise NotImplementedError


class KBContextProvider(ContextProvider):
    PHASE_KB_DOCS = {
        "research": ["evidence-rubric.md", "quality-standards.md"],
        "thinking": ["analysis-frameworks.md", "thinking-anti-patterns.md"],
        "validation": ["evidence-tracking-rubric.md", "quality-standards.md"],
    }

    INDUSTRY_KEYWORDS = {
        "startup": "tech-startup",
        "tech": "tech-startup",
        "ecommerce": "ecommerce",
        "retail": "ecommerce",
        "consult": "consulting",
        "consulting": "consulting",
    }

    def __init__(self, skill_dir=None):
        self.skill_dir = Path(skill_dir) if skill_dir else self._find_skill_dir()

    def enrich(self, handoff_brief, phase, agent_name):
        industry = handoff_brief.get("context", {}).get("industry_context", "")
        return {
            "kb_docs": self._load_kb_docs(phase),
            "industry_template": self._load_industry_template(industry),
        }

    def _find_skill_dir(self):
        return Path(__file__).resolve().parent.parent

    def _load_kb_docs(self, phase):
        docs = {}
        for doc_name in self.PHASE_KB_DOCS.get(phase, []):
            path = self.skill_dir / "kb" / doc_name
            if path.is_file():
                docs[doc_name] = path.read_text()
        return docs

    def _load_industry_template(self, industry_context):
        industry_lower = industry_context.lower()
        for keyword, template_name in self.INDUSTRY_KEYWORDS.items():
            if keyword in industry_lower:
                path = self.skill_dir / "kb" / "industry-analysis-templates" / f"{template_name}.md"
                if path.is_file():
                    return path.read_text()
        return None
