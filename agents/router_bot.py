from autogen import Agent
class RouterBot(Agent):
    name = "🧭 RouterBot"
    def run(self, question, **k):
        kw = question.lower()
        if any(w in kw for w in ("omzet", "rekening", "factuur")):
            return "AccountView"
        if any(w in kw for w in ("voorraad", "productie")):
            return "Ridder"
        return "CompanyDB"
