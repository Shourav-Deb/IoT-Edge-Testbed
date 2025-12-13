# sensors/device_sensor.py
import socket, json, math, random
from server.protocol import build_message

class DeviceSensor:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.t = 0
        self.mem_leak = 0

    def generate(self, mode):
        self.t += 1

        cpu = 35 + 10 * math.sin(2 * math.pi * self.t / 180)
        mem = 55 + 5 * math.sin(2 * math.pi * self.t / 240)
        disk = 8 + random.uniform(0, 4)
        proc = 80 + random.randint(-5, 5)

        event = "Normal"

        if mode == "system_stress":
            cpu += 35
            mem += 20
            proc += 40
            event = "System Stress"

        elif mode == "crypto_mining":
            cpu = random.uniform(85, 95)
            mem += 10
            disk = random.uniform(2, 5)
            event = "Crypto Mining Malware"

        elif mode == "memory_leak":
            self.mem_leak += random.uniform(0.8, 1.5)
            mem += self.mem_leak
            event = "Memory Leak"

        elif mode == "disk_flood":
            disk *= 10
            proc += 20
            event = "Disk Flood"

        elif mode == "fork_bomb":
            proc *= 4
            cpu += 20
            event = "Fork Bomb"

        return {
            "cpu_usage_pct": round(min(cpu, 100), 1),
            "memory_usage_pct": round(min(mem, 100), 1),
            "disk_io_mb": round(disk, 2),
            "process_count": proc,
            "event": event
        }

    def send(self, mode):
        msg = build_message("device", self.generate(mode))
        self.sock.sendall((json.dumps(msg) + "\n").encode())
