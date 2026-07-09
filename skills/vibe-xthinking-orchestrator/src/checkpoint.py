class CheckpointResult:
    def __init__(self, action, feedback=""):
        self.action = action
        self.feedback = feedback


class Checkpoint:
    def pause(self, phase, output, context=None):
        raise NotImplementedError


class AutoCheckpoint(Checkpoint):
    def pause(self, phase, output, context=None):
        return CheckpointResult("continue")
