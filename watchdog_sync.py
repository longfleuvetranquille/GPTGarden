import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API_URL = "https://TON_DOMAINE_RENDER/query"

class NewNoteHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".md"):
            print(f"📄 Nouveau fichier détecté : {event.src_path}")
            requests.get(API_URL, params={"question": "Nouvelle note ajoutée."})

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    path = os.getenv("GARDEN_PATH", "notes")
    event_handler = NewNoteHandler()
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    print(f"🔍 Watchdog actif sur : {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
