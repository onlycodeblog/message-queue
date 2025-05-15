import threading
import time
from collections import defaultdict, deque
from queue import Queue
from message_queue.utils import timestamped_log, ensure_log_dirs


class Consumer:
    def __init__(self, name, callback, dependencies=None, filter_fn=None):
        self.name = name
        self.callback = callback  # function() that processes the message
        self.dependencies = dependencies or []
        self.filter_fn = filter_fn or (lambda m: True)  # filter for which messages should be consumed


class MessageQueue:
    def __init__(self, max_size=10):
        # Queue is thread-safe, so no external Lock is needed
        self.queue = Queue(maxsize=max_size)
        self.consumers = {}
        self.processed_messages = defaultdict(set)  # consumer_name -> set(message_ids)
        self.retry_counts = defaultdict(lambda: defaultdict(int))  # consumer -> message_id -> retries
        self.pending = deque()  # Holds (consumer, message_id, message) when deps not satisfied
        self.MAX_RETRIES = 3
        ensure_log_dirs()

        threading.Thread(target=self._dispatch_loop, daemon=True).start()
        threading.Thread(target=self._pending_loop, daemon=True).start()

    def add_consumer(self, consumer: Consumer):
        self.consumers[consumer.name] = consumer

    def publish(self, message_tuple):
        message_id, message = message_tuple
        try:
            self.queue.put((message_id, message), block=True)  # block=True: Wait indefinitely until there's space
            if self.queue.full():
                print(f"[queue] Queue is FULL.")
        except Exception as e:
            timestamped_log(f"[!] Failed to enqueue message: {message} - {e}", "logs/error_log.txt")

    def _dispatch_loop(self):
        while True:
            message_id, message = self.queue.get(block=True)  # block=True: Wait indefinitely until a msg is available
            try:
                self._process_message_chain(message_id, message)
                if self.queue.empty():
                    print(f"[queue] Queue is EMPTY. Waiting..")
            except RuntimeError as e:
                print(f"Exception Occurred: {e}")
                self.pending.append((message_id, message))  # fallback if exception occurs


    def _pending_loop(self):
        while True:
            time.sleep(10)  # Check pending list periodically
            for _ in range(len(self.pending)):
                message_id, message = self.pending.popleft()
                try:
                    self._process_message_chain(message_id, message)
                except RuntimeError as e:
                    print(f"Exception Occurred: {e}")
                    self.pending.append((message_id, message))  # fallback if exception occurs


    def _process_message_chain(self, message_id, message):
        processed_consumers = set()
        remaining_consumers = set(self.consumers.keys())

        while remaining_consumers:
            progress = False
            for name in list(remaining_consumers):
                consumer = self.consumers[name]
                # If the consumer filters out the message or has already processed it,
                # mark it as processed to unblock dependents
                if not consumer.filter_fn(message) or message_id in self.processed_messages[name]:
                    processed_consumers.add(name)  # mark consumer as processed
                    remaining_consumers.remove(name)
                    progress = True
                    continue
                # Process the consumer only if all its dependencies have completed
                if all(dep in processed_consumers for dep in consumer.dependencies):
                    self._process_message(consumer, message_id, message)
                    processed_consumers.add(name)
                    remaining_consumers.remove(name)
                    progress = True
            if not progress:
                raise RuntimeError("Circular dependency or unresolved consumer chain")  # error message for a deadlock

    def _process_message(self, consumer, message_id, message):
        try:
            consumer.callback(message, message_id)
            self.processed_messages[consumer.name].add(message_id)
        except Exception as e:
            self.retry_counts[consumer.name][message_id] += 1
            count = self.retry_counts[consumer.name][message_id]
            err_msg = f"[x] Error in consumer {consumer.name}: {e} (Retry {count}/{self.MAX_RETRIES})"
            print(err_msg)
            timestamped_log(err_msg, "logs/error_log.txt")
            if count < self.MAX_RETRIES:
                retry_msg = f"[~] Retrying {consumer.name} for message {message_id} (attempt {count + 1})"
                print(retry_msg)
                timestamped_log(retry_msg, "logs/error_log.txt")
                time.sleep(1)
                self._process_message(consumer, message_id, message)
