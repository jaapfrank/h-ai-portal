from autogen import Agent
class VizMaster(Agent):
    name = "📊 VizMaster"
    def run(self, data, **k):
        return f"GRAPH(bar) op basis van {str(data)[:40]}…"
