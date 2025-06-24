from autogen.agentchat.observer_agent import ObserverAgent
class ReporterAgent(ObserverAgent):
    name = "📣 ReporterAgent"
    def on_message(self, message, sender, listeners):
        print(f"[{sender.name}] → {message.content}")
