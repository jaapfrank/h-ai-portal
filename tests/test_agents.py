from main_agents import chat
def test_count():
    assert len(chat.agents) == 7         # reporter is observer, telt niet mee
