from autogen import GroupChat, GroupChatManager
from agents.manager_agent  import ManagerAgent
from agents.router_bot      import RouterBot
from agents.sql_guru        import SQLGuru
from agents.dbf_whisperer   import DBFWhisperer
from agents.viz_master      import VizMaster
from agents.doc_scribe      import DocScribe
from agents.reporter_agent  import ReporterAgent

manager  = ManagerAgent()
router   = RouterBot()
sql      = SQLGuru()
dbf      = DBFWhisperer()
viz      = VizMaster()
doc      = DocScribe()
reporter = ReporterAgent()

chat = GroupChat(
    agents=[manager, router, sql, dbf, viz, doc, reporter],
    messages=[],
    max_round=10
)

if __name__ == "__main__":
    GroupChatManager.run(chat, turn_handler=print)
