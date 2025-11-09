"""
Master orchestrator stub.
Decides which agent to invoke. Right now it is a placeholder.
"""
from ..utils.logger import get_logger

logger = get_logger(__name__)

class Orchestrator:
    def __init__(self):
        # registry could be a mapping of agent name -> agent instance
        self.registry = {}

    def register_agent(self, name: str, agent):
        self.registry[name] = agent
        logger.info(f"[Orchestrator] Registered agent '{name}'")

    def decide_action(self, telemetry):
        # simple policy: if telemetry triggers something, let analysis agent handle it
        logger.debug("[Orchestrator] decide_action called")
        # This is where you'd put orchestration logic
        return None
