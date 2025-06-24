from autogen import Agent
class SQLGuru(Agent):
    name = "💾 SQLGuru"
    def run(self, intent, **k):
        return f"SELECT * FROM … /* intent: {intent} */"
