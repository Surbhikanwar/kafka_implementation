"""
Simple registry helper. Could be extended to discover agents over network.
"""
class Registry:
    def __init__(self):
        self._agents = {}

    def add(self, name, agent):
        self._agents[name] = agent

    def get(self, name):
        return self._agents.get(name)

    def list_agents(self):
        return list(self._agents.keys())
