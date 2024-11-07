import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartBotHandler(FileSystemEventHandler):
    def __init__(self, script):
        self.script = script
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen(["python", self.script])

    def on_modified(self, event):
        if event.src_path.endswith(self.script):
            print(f"{self.script} has changed. Restarting...")
            self.start_bot()

if __name__ == "__main__":
    script_to_watch = "./backend/tgbot.py"
    event_handler = RestartBotHandler(script_to_watch)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()
    print(f"Watching {script_to_watch} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    event_handler.process.terminate()
