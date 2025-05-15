import os
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FileTracker:
    def __init__(self, filepath):
        self.filepath = filepath
        self.offset = 0

    def read_new_lines(self):
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, "r") as f:
            f.seek(self.offset)
            new_lines = f.readlines()
            self.offset = f.tell()
        return [line.strip() for line in new_lines if line.strip()]


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filepath, on_change):
        self.filepath = filepath
        self.on_change = on_change

    def on_modified(self, event):
        if event.src_path.endswith(self.filepath):
            print(f"[watcher] Detected change in: {event.src_path}")
            self.on_change()


def start_watcher(filepath, on_change):
    handler = FileChangeHandler(filepath, on_change)
    observer = Observer()
    observer.schedule(handler, path=os.path.dirname(filepath) or ".", recursive=False)
    observer.start()
    print(f"[watcher] Watching for changes in {filepath}...")
    return observer
