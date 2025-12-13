# server/packet_parser.py

# Validates and parses incoming TCP packets

import json

def parse_packet(raw_bytes):
    """
    Convert raw TCP bytes into Python dict.
    """
    try:
        decoded = raw_bytes.decode("utf-8").strip()
        return json.loads(decoded)
    except Exception:
        return None
