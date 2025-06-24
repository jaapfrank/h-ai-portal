"""
Zet alle agent-bestanden, requirements, tests én
start de GroupChat met live rapportage.

Run één keer:
    python bootstrap_agents.py
"""

import os, subprocess, textwrap, sys, json, importlib.util

PROJECT_ROOT = os.path.dirname(__file__)
AGENTS_DIR    = os.path.join(PROJECT_ROOT, "agents")
TEST_DIR      = os.path.join(PROJECT_ROOT, "tests")

FILES = {
    # __init__.py
    os.path.join(AGENTS_DIR, "__init__.py"): "",
    # ManagerAgent
    os.path.join(AGENTS_DIR, "manager_agent.py"): textwrap.dedent("""
        from autogen import Agent
        class ManagerAgent(Agent):
            name = "🧑‍💼 ManagerAgent"
            def run(self, task, memory, **k):
                return f"Taak ontvangen: {task}"
    """),
    # RouterBot
    os.path.join(AGENTS_DIR, "router_bot.py"): textwrap.dedent("""
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
    """),
    # SQLGuru
    os.path.join(AGENTS_DIR, "sql_guru.py"): textwrap.dedent("""
        from autogen import Agent
        class SQLGuru(Agent):
            name = "💾 SQLGuru"
            def run(self, intent, **k):
                return f"SELECT * FROM … /* intent: {intent} */"
    """),
    # DBFWhisperer
    os.path.join(AGENTS_DIR, "dbf_whisperer.py"): textwrap.dedent("""
        from autogen import Agent
        class DBFWhisperer(Agent):
            name = "📁 DBFWhisperer"
            def run(self, intent, **k):
                return f"DBF-query voor intent: {intent}"
    """),
    # VizMaster
    os.path.join(AGENTS_DIR, "viz_master.py"): textwrap.dedent("""
        from autogen import Agent
        class VizMaster(Agent):
            name = "📊 VizMaster"
            def run(self, data, **k):
                return f"GRAPH(bar) op basis van {data[:40]}…"
    """),
    # TestNinja
    os.path.join(AGENTS_DIR, "test_ninja.py"): textwrap.dedent("""
        from autogen import Agent
        import subprocess, sys
        class TestNinja(Agent):
            name = "🧪 TestNinja"
            def run(self, *a, **k):
                res = subprocess.run([sys.executable, "-m", "pytest", "-q"], capture_output=True, text=True)
                return "✅ Alle tests groen" if res.returncode == 0 else res.stdout + res.stderr
    """),
    # DocScribe
    os.path.join(AGENTS_DIR, "doc_scribe.py"): textwrap.dedent("""
        from autogen import Agent, utils
        import datetime, pathlib, textwrap, os, json
        class DocScribe(Agent):
            name = "📝 DocScribe"
            def run(self, note, **k):
                path = pathlib.Path("CLAUDE_PROJECT_MEMORY.md")
                ts   = datetime.datetime.now().isoformat(timespec="minutes")
                line = f"\\n- {ts}  {note}"
                path.write_text(path.read_text() + line, encoding="utf-8")
                return "Changelog bijgewerkt."
    """),
    # ReporterAgent
    os.path.join(AGENTS_DIR, "reporter_agent.py"): textwrap.dedent("""
        from autogen.agentchat import ObserverAgent
        class ReporterAgent(ObserverAgent):
            name = "📣 ReporterAgent"
            def on_message(self, message, sender, listeners):
                print(f"[{sender.name}] → {message.content}")
    """),
    # main_agents.py
    os.path.join(PROJECT_ROOT, "main_agents.py"): textwrap.dedent("""
        from autogen import GroupChat, GroupChatManager
        from agents.manager_agent import ManagerAgent
        from agents.router_bot     import RouterBot
        from agents.sql_guru       import SQLGuru
        from agents.dbf_whisperer  import DBFWhisperer
        from agents.viz_master     import VizMaster
        from agents.test_ninja     import TestNinja
        from agents.doc_scribe     import DocScribe
        from agents.reporter_agent import ReporterAgent

        manager  = ManagerAgent()
        router   = RouterBot()
        sql      = SQLGuru()
        dbf      = DBFWhisperer()
        viz      = VizMaster()
        tester   = TestNinja()
        doc      = DocScribe()
        reporter = ReporterAgent()

        chat = GroupChat(
            agents=[manager, router, sql, dbf, viz, tester, doc, reporter],
            messages=[],
            max_round=10
        )

        if __name__ == "__main__":
            GroupChatManager.run(chat, turn_handler=print)
    """),
    # pytest
    os.path.join(TEST_DIR, "test_agents.py"): textwrap.dedent("""
        from main_agents import chat
        def test_agent_count():
            assert len(chat.agents) == 8
    """)
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# 1. directories
ensure_dir(AGENTS_DIR)
ensure_dir(TEST_DIR)

# 2. write all files
for path, content in FILES.items():
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.lstrip())

# 3. requirements
req_path = os.path.join(PROJECT_ROOT, "requirements.txt")
if os.path.exists(req_path):
    with open(req_path, "r+", encoding="utf-8") as f:
        txt = f.read()
        if "autogen" not in txt:
            f.write("\nautogen>=0.2.18\n")
else:
    with open(req_path, "w", encoding="utf-8") as f:
        f.write("autogen>=0.2.18\n")

# 4. install autogen if nodig
if importlib.util.find_spec("autogen") is None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "autogen>=0.2.18"])

# 5. run pytest
subprocess.run([sys.executable, "-m", "pytest", "-q"], check=False)

# 6. start agents
subprocess.run([sys.executable, "main_agents.py"])
