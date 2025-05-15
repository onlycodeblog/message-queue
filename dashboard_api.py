from flask import Flask, jsonify, render_template

app = Flask(__name__)
message_queue = None  # this will be set externally by your main app


# Route for the dashboard UI (serves an HTML template)
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# API endpoint to fetch live system stats in JSON format
@app.route("/")
def home():
    if message_queue is None:
        return jsonify({"error": "MessageQueue not attached"}), 503

    return jsonify({
        "queue_size": message_queue.queue.qsize(),
        "queue_max": message_queue.queue.maxsize,
        "pending": len(message_queue.pending),
        "processed": {k: len(v) for k, v in message_queue.processed_messages.items()},
        "retries": {
            cname: sum(message_queue.retry_counts[cname].values())
            for cname in message_queue.retry_counts
        }
    })
