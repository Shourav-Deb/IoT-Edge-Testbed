# sensors/network_sensor.py
import socket, json, math, random
from server.protocol import build_message

class NetworkSensor:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.t = 0

    def generate(self, mode):
        self.t += 1

        # ===== Normal traffic (equation-based) =====
        base = 60 + 8 * math.sin(2 * math.pi * self.t / 300)
        noise = random.uniform(-2, 2)
        packets = max(1, int(base + noise))

        throughput = packets * 600 * 8 / 1000
        latency = 20 + (packets / 100) ** 1.5 + random.uniform(0, 2)
        loss = min(0.5, 0.01 + packets / 8000)

        event = "Normal"

        # ===== Attack modifiers =====
        if mode == "ddos":
            packets *= 15
            throughput *= 15
            latency *= 2.5
            loss += 0.30
            event = "DDoS Attack"

        elif mode == "slowloris":
            packets *= 4
            throughput *= 2
            latency *= 4
            loss += 0.08
            event = "Slowloris Attack"

        elif mode == "portscan":
            packets *= 5
            throughput *= 3
            latency *= 1.8
            loss += 0.05
            event = "Port Scan"

        elif mode == "exfiltration":
            packets *= 8
            throughput *= 12
            latency *= 1.4
            event = "Data Exfiltration"

        elif mode == "botnet":
            packets *= 3
            throughput *= 2
            latency *= 1.2
            event = "Botnet Probe"

        return {
            "packets": packets,
            "throughput_kbps": round(throughput, 2),
            "latency_ms": round(latency, 2),
            "packet_loss": round(min(loss, 1), 3),
            "event": event
        }

    def send(self, mode):
        msg = build_message("network", self.generate(mode))
        self.sock.sendall((json.dumps(msg) + "\n").encode())
