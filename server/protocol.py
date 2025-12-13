# server/protocol.py
# Defines how sensor messages look

def build_message(sensor_name, payload):
    """
    Wrap sensor payload into a protocol message.
    """
    return {
        "sensor": sensor_name,
        "values": payload
    }
