class AgentRunner:
    def run(self, agent_name, phase, context):
        raise NotImplementedError


class FakeAgentRunner(AgentRunner):
    def __init__(self, outputs=None):
        self.outputs = outputs if outputs else {}
        self.calls = []

    def run(self, agent_name, phase, context):
        key = f"{phase}:{agent_name}"
        self.calls.append((key, context))
        return self.outputs.get(key, {"evidence": []})
