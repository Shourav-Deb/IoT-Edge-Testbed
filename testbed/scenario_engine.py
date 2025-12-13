# testbed/scenario_engine.py

import json, time

class ScenarioEngine:
    def __init__(self, path):
        with open(path) as f:
            self.scenario = json.load(f)
        self.start = time.time()

    def elapsed(self):
        return int(time.time() - self.start)

    def done(self):
        return self.elapsed() >= self.scenario["duration_seconds"]

    def current_state(self):
        t = self.elapsed()
        for p in self.scenario["phases"]:
            if p["start"] <= t < p["end"]:
                return {"network": p["network"], "auth": p["auth"]}
        return {"network": "normal", "auth": "normal"}
