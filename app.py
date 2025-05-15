import argparse
import csv
import threading
import time
import uuid

import dashboard_api
from dashboard_api import app as flask_app
from message_queue import MessageQueue, Consumer
from message_queue.watcher import start_watcher, FileTracker

INPUT_FILE = "input.txt"
PROCESSED_CSV = "logs/processed_log.csv"


def log_processed(consumer_name, message, message_id):
    try:
        with open(PROCESSED_CSV, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([consumer_name, message_id, message])
    except Exception as e:
        print(f"[!] Failed to log processed message: {e}")


def process_wrapper(consumer_name):
    def _fn(msg, msg_id):
        print(f"[{consumer_name}] processed:", msg)
        log_processed(consumer_name, msg, msg_id)

    return _fn


def run_dashboard(mq):
    def dashboard():
        while True:
            total = sum(len(v) for v in mq.processed_messages.values())
            print(f"\n[dashboard] Processed: {total} messages")
            for cname, msgs in mq.processed_messages.items():
                print(f" - {cname}: {len(msgs)}")
            try:
                qsize = mq.queue.qsize()
                print(f"[dashboard] Queue size: {qsize} / {mq.queue.maxsize}")
            except RuntimeError:
                pass
            time.sleep(5)

    threading.Thread(target=dashboard, daemon=True).start()


def run_flask_server():
    flask_app.run(port=5000, use_reloader=False)


def main(queue_size):
    mq = MessageQueue(max_size=queue_size)
    file_tracker = FileTracker(INPUT_FILE)

    mq.add_consumer(Consumer("A", process_wrapper("A"), dependencies=[],
                             filter_fn=lambda m: m.lower().startswith('a')))
    mq.add_consumer(Consumer("B", process_wrapper("B"), dependencies=["A"],
                             filter_fn=lambda m: m.lower().startswith('b')))
    mq.add_consumer(Consumer("C", process_wrapper("C"), dependencies=["B"],
                             filter_fn=lambda m: m.lower().startswith('c')))

    run_dashboard(mq)  # command-line dashboard

    dashboard_api.message_queue = mq  # attach your mq instance with (web) dashboard message_queue
    threading.Thread(target=run_flask_server, daemon=True).start()

    def on_file_change():
        try:
            messages = file_tracker.read_new_lines()
            for msg in messages:
                msg_id = str(uuid.uuid4())  # a universally unique identifier (UUID) for every message
                mq.publish((msg_id, msg))
        except Exception as e:
            print(f"[!] Error reading file change: {e}")

    observer = start_watcher(INPUT_FILE, on_file_change)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[app] Shutting down...")  # for graceful shutdown
        observer.stop()
        observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the message queue system with file watching.")
    parser.add_argument("--max-size", type=int, default=10, help="Max queue size")
    args = parser.parse_args()

    main(args.max_size)
