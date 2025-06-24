from autogen import Agent
import datetime, pathlib
class DocScribe(Agent):
    name = "📝 DocScribe"
    def run(self, note, **k):
        path = pathlib.Path("CLAUDE_PROJECT_MEMORY.md")
        if not path.exists():
            path.write_text("# Changelog\n", encoding="utf-8")
        ts = datetime.datetime.now().isoformat(timespec="minutes")
        path.write_text(path.read_text(encoding="utf-8") + f"\n- {ts}  {note}",
                        encoding="utf-8")
        return "Changelog bijgewerkt."
