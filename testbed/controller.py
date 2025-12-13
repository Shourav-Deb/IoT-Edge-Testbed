# testbed/controller.py
# Centralized testbed controller

import threading, time
from sensors.network_sensor import NetworkSensor
from sensors.auth_sensor import AuthSensor
from sensors.device_sensor import DeviceSensor

class TestbedController:
    def __init__(self, scenario):
        self.scenario = scenario
        self.running = False

        self.net = NetworkSensor("127.0.0.1", 9000)
        self.auth = AuthSensor("127.0.0.1", 9000)
        self.device = DeviceSensor("127.0.0.1", 9000)

    def start(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while self.running and not self.scenario.done():
            state = self.scenario.current_state()
            self.net.send(state["network"])
            self.auth.send(state["auth"])
            self.device.send(state["network"])
            time.sleep(1)
