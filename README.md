# 🧵 Message Queue System

A lightweight, in-memory message queuing system in Python — designed for educational use and real-time observability.
Implements the classic **Producer-Consumer** pattern with advanced features like:

- Message-based **consumer dependencies**
- In-memory, **bounded queue**
- **Retry logic** for consumer failures
- Real-time **web dashboard** using Flask + Bootstrap
- File-based **message publishing** (via `input.txt`)

---

## 📂 Project Structure

```
message_queue/
├── app.py                   # Entry point
├── dashboard_api.py         # Flask API & dashboard
├── input.txt                # Source for messages
├── logs/                    # Processed and error logs
│   ├── error_log.txt
│   └── processed_log.csv
├── message_queue/           # Core system logic
│   ├── core.py              # Queue, Consumer, dependencies
│   ├── utils.py             # Logging, hashing
│   ├── watcher.py           # File watcher
│   └── __init__.py
├── templates/
│   └── dashboard.html       # Live Bootstrap dashboard
├── requirements.txt         # Install dependencies
├── pyproject.toml           # Optional modern Python packaging and dependency management using pip or build tools.
├── .gitignore
└── README.md
```

---

## 🚀 How to Run

### ✅ Setup

```bash
# Clone the repo
$ git clone https://github.com/onlycodeblog/message_queue.git
$ cd message_queue

# (Recommended) Create a virtual environment
$ python -m venv .venv
$ source .venv/bin/activate

# Install dependencies
$ pip install -r requirements.txt
```

### ▶️ Launch the system

```bash
$ python app.py --max-size 3
```

This will:
- Watch for new messages in `input.txt`
- Launch the message queue
- Start the Flask dashboard on [http://localhost:5000](http://localhost:5000)

---

## ✏️ How to Test

1. Open the `input.txt` file
2. Add a new line — each line = one message
3. Messages are consumed in order by A → B → C (based on dependencies)
4. Observe:
   - Console output
   - Dashboard (queue size, retries, per-consumer counts)

---

## 📊 Live Dashboard

Visit [http://localhost:5000](http://localhost:5000) to see:

- Queue size (live)
- Pending messages
- Messages processed by each consumer
- Retry statistics

Styled with **Bootstrap dark theme** ✨

---

## 🪵 Logging

- **Processed messages:** `logs/processed_log.csv`
- **Errors / retries:** `logs/error_log.txt`

---

## 🛠️ Features Summary

- ✅ Thread-safe queue using `queue.Queue`
- ✅ Blocking enqueue/dequeue with `block=True`
- ✅ Retry mechanism with max attempts
- ✅ Dependency-aware dispatching: C → (A, B)
- ✅ Real-time UI via Flask & Bootstrap

---

## 📚 Inspired By

Classic concurrency problems and real-world systems.

---

