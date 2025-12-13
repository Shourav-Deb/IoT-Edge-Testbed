# server/testbed_logger.py
# Writes packets into JSONL log file

import json, time, os

DATA_DIR = "data/testbed"
os.makedirs(DATA_DIR, exist_ok=True)

_current_file = None

def start_session():
    global _current_file
    fname = time.strftime("testbed_%Y%m%d_%H%M%S.jsonl")
    _current_file = open(os.path.join(DATA_DIR, fname), "a")

def stop_session():
    global _current_file
    if _current_file:
        _current_file.close()
        _current_file = None

def log_record(record):
    if not _current_file:
        return
    record["timestamp"] = int(time.time())
    _current_file.write(json.dumps(record) + "\n")
    _current_file.flush()

