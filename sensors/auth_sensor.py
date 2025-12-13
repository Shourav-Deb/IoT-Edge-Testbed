# sensors/auth_sensor.py
import socket, json, math, random
from server.protocol import build_message

class AuthSensor:
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.sock.connect((host, port))
        self.t = 0

    def generate(self, mode):
        self.t += 1

        base = 2 + 1.2 * math.sin(2 * math.pi * self.t / 200)
        attempts = max(1, int(base + random.uniform(-0.5, 0.5)))
        success_rate = 0.85
        event = "Normal"

        if mode == "bruteforce":
            attempts *= 30
            success_rate = 0.05
            event = "Bruteforce Attack"

        elif mode == "credential_stuffing":
            attempts *= 25
            success_rate = 0.10
            event = "Credential Stuffing"

        elif mode == "password_spray":
            attempts *= 20
            success_rate = 0.15
            event = "Password Spray"

        elif mode == "session_hijack":
            attempts *= 10
            success_rate = 0.90
            event = "Session Hijacking"

        elif mode == "admin_abuse":
            attempts *= 15
            success_rate = 0.30
            event = "Suspicious Admin Access"

        success = int(attempts * success_rate)

        return {
            "login_attempts": attempts,
            "successful_logins": success,
            "failed_logins": attempts - success,
            "event": event
        }

    def send(self, mode):
        msg = build_message("auth", self.generate(mode))
        self.sock.sendall((json.dumps(msg) + "\n").encode())
