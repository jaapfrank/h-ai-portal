from autogen import Agent
class ManagerAgent(Agent):
    name = "🧑‍💼 ManagerAgent"
    def run(self, task, **k):
        return f"Taak ontvangen: {task}"
