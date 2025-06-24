# run_agents.py  –  Autonome Manager + realtime stuur­commando’s
# --------------------------------------------------------------
# ▸ Werkt met autogen ≥ 0.9
# ▸ Console + bestand-logging (logs/chat.log)
# ▸ Slash-commando’s: /status /pause /resume /skip /add <taak>

import logging, pathlib, queue, threading, time
from autogen import Agent, GroupChat, GroupChatManager

# ----------------- logging-setup -----------------
log_dir = pathlib.Path("logs"); log_dir.mkdir(exist_ok=True)
logging.basicConfig(filename=log_dir / "chat.log",
                    level=logging.INFO,
                    format="%(asctime)s  %(message)s")

def log(msg): print(msg); logging.info(msg)

# ----------------- gedeelde taakqueue ------------
TASK_QUEUE   = queue.Queue()
INITIAL_TASKS = [
    "Voorraad controleren",
    "Omzetoverzicht genereren",
    "Facturen valideren",
]
for t in INITIAL_TASKS:
    TASK_QUEUE.put(t)

PAUSED = threading.Event()      # False = run, True = pauze
CURRENT_TASK = {"name": None}   # gedeelde state voor reporter

# ----------------- agents ------------------------
class Manager(Agent):
    name = "🧑‍💼 Manager"

    def run(self, _msg, **k):
        if PAUSED.is_set():
            return "Pauze – wacht op /resume"
        if CURRENT_TASK["name"]:
            return f"Bezig met: {CURRENT_TASK['name']}"   # al werkend

        try:
            task = TASK_QUEUE.get_nowait()
        except queue.Empty:
            return "Geen taken meer."

        CURRENT_TASK["name"] = task
        log(f"[TASK] Start: {task}")
        # -------- hier komt echte taaklogica (SQL, grafiek, …) -------
        time.sleep(1)  # simulatie
        log(f"[DONE] Klaar met: {task}")
        CURRENT_TASK["name"] = None
        return f"Klaar met: {task}"

class Reporter(Agent):
    name = "📣 Reporter"
    def receive(self, message, sender=None, **k):
        log(f"[{sender.name}] → {message.content}")

# ----------------- hulpfuncties ------------------
def queue_status():
    pending = list(TASK_QUEUE.queue)
    cur = CURRENT_TASK["name"] or "—"
    state = "PAUSED" if PAUSED.is_set() else "RUNNING"
    return f"Status: {state}\nHuidige taak: {cur}\nWachtrij: {pending or '—'}"

def add_task(txt):
    TASK_QUEUE.put(txt)
    return f"Taak toegevoegd: {txt}"

# ----------------- runtime-loop ------------------
chat = GroupChat([Manager(), Reporter()], messages=[], max_round=1)

log("▶ Typ /status /pause /resume /skip /add <taak>  —  of gewoon tekst (Ctrl+C stopt)")
try:
    while True:
        line = input("> ").strip()
        if not line:
            continue

        # -------- slash-commando’s ---------------
        if line.startswith("/"):
            cmd, *rest = line[1:].split(maxsplit=1)
            if cmd == "status":
                log(queue_status())
            elif cmd == "pause":
                PAUSED.set();  log("⏸ Manager gepauzeerd.")
            elif cmd == "resume":
                PAUSED.clear(); log("▶ Manager hervat.")
            elif cmd == "skip":
                CURRENT_TASK["name"] = None
                log("⏭ Huidige taak overgeslagen.")
            elif cmd == "add" and rest:
                log(add_task(rest[0]))
            else:
                log("Onbekend commando.")
            continue

        # -------- normale input ------------------
        GroupChatManager.run(chat, reset_reason="new", messages=[line])

except KeyboardInterrupt:
    log("Gestopt.")
