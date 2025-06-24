from autogen import Agent
class DBFWhisperer(Agent):
    name = "📁 DBFWhisperer"
    def run(self, intent, **k):
        return f"DBF-query voor intent: {intent}"
