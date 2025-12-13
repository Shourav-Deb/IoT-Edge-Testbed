# app.py
# EWAD Testbed Backend
# - TCP-based sensor ingestion
# - Scenario-driven testbed controller
# - Flask REST API

from flask import Flask, jsonify, request, render_template
import threading, os

from server.tcp_server import ThreadedTCPServer, TCPHandler
from server.testbed_logger import start_session, stop_session
from testbed.scenario_engine import ScenarioEngine
from testbed.controller import TestbedController

# -------------------------------------------------
# Flask App Setup
# -------------------------------------------------
app = Flask(
    __name__,
    template_folder="ui/templates",
    static_folder="ui/static"
)

HOST = "0.0.0.0"
TCP_PORT = 9000
HTTP_PORT = int(os.environ.get("PORT", 5000))  # Streamlit/GitHub friendly

# -------------------------------------------------
# Global Testbed State
# -------------------------------------------------
tcp_server = None
tcp_thread = None
testbed = None
scenario = None
testbed_running = False

# -------------------------------------------------
# Start TCP Server (background thread)
# -------------------------------------------------
def start_tcp_server():
    global tcp_server
    tcp_server = ThreadedTCPServer((HOST, TCP_PORT), TCPHandler)
    tcp_server.serve_forever()

# -------------------------------------------------
# Flask Routes
# -------------------------------------------------

@app.route("/")
def index():
    """
    Web UI entry
    """
    return render_template("index.html")


@app.route("/api/testbed/start", methods=["POST"])
def start_testbed():
    global testbed, scenario, testbed_running

    if testbed_running:
        return jsonify({"ok": False, "error": "Testbed already running"})

    data = request.get_json() or {}
    scenario_path = data.get("scenario_path", "scenarios/default_scenario.json")

    if not os.path.exists(scenario_path):
        return jsonify({"ok": False, "error": "Scenario file not found"})

    # Start logging session
    start_session()

    # Load scenario
    scenario = ScenarioEngine(scenario_path)

    # Start testbed controller
    testbed = TestbedController(scenario)
    testbed.start()

    testbed_running = True
    return jsonify({"ok": True, "msg": "Testbed started"})


@app.route("/api/testbed/stop", methods=["POST"])
def stop_testbed():
    global testbed_running

    if not testbed_running:
        return jsonify({"ok": False, "error": "Testbed not running"})

    testbed_running = False
    stop_session()

    return jsonify({"ok": True, "msg": "Testbed stopped"})


@app.route("/api/testbed/status")
def testbed_status():
    return jsonify({
        "running": testbed_running
    })


@app.route("/api/scenario/upload", methods=["POST"])
def upload_scenario():
    """
    Allows uploading a scenario file (JSON)
    """
    file = request.files.get("file")
    if not file:
        return jsonify({"ok": False, "error": "No file uploaded"})

    os.makedirs("scenarios", exist_ok=True)
    path = os.path.join("scenarios", file.filename)
    file.save(path)

    return jsonify({"ok": True, "path": path})


@app.route("/api/testbed/files")
def list_testbed_files():
    """
    Lists completed testbed JSONL files
    """
    base = "data/testbed"
    os.makedirs(base, exist_ok=True)

    files = []
    for f in sorted(os.listdir(base)):
        if f.endswith(".jsonl"):
            files.append({
                "path": os.path.join(base, f),
                "display": f.replace("testbed_", "").replace(".jsonl", "")
            })

    return jsonify({"files": files})


@app.route("/api/testbed/load", methods=["POST"])
def load_testbed_file():
    """
    Loads a JSONL file for replay (UI or Streamlit)
    """
    data = request.get_json()
    path = data.get("path")

    if not path or not os.path.exists(path):
        return jsonify({"ok": False, "error": "File not found"})

    rows = []
    with open(path) as f:
        for line in f:
            rows.append(eval(line))  # trusted internal logs

    return jsonify({"ok": True, "rows": rows})


# -------------------------------------------------
# Main Entry
# -------------------------------------------------
if __name__ == "__main__":
    # Start TCP server once
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Start Flask app
    app.run(host=HOST, port=HTTP_PORT, debug=False)
