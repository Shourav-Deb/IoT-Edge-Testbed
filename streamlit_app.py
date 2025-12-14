# streamlit_app.py
# Streamlit frontend for EWAD Testbed
# Works in TWO modes:
# 1) Backend-connected (Flask + TCP)
# 2) Streamlit-only demo mode (GitHub repo scenarios)

import streamlit as st
import pandas as pd
import json, time, os
import requests

# --------------------------------
# Config
# --------------------------------
BACKEND = os.environ.get("EWAD_BACKEND", "http://localhost:5000")
SCENARIO_DIR = "scenarios"

st.set_page_config(page_title="Edge IoT Device Sensors", layout="wide")

# --------------------------------
# UI Theme (White & Blue)
# --------------------------------
st.markdown("""
<style>
body { background-color:#f4f7ff; }
h1,h2,h3 { color:#1a73e8; }
.attack { background:#ffe5e5; color:#b00020; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

st.title("Edge IoT Device Sensors")
st.caption("Scenario-driven IoT Edge Testbed (Streamlit)")

# --------------------------------
# Backend Safe Helpers
# --------------------------------
def backend_get(path):
    try:
        return requests.get(f"{BACKEND}{path}", timeout=2).json()
    except Exception:
        return None

def backend_post(path, **kwargs):
    try:
        return requests.post(f"{BACKEND}{path}", timeout=2, **kwargs).json()
    except Exception:
        return None

# --------------------------------
# Detect Backend
# --------------------------------
status = backend_get("/api/testbed/status")
backend_online = status is not None

# --------------------------------
# Scenario Selector (GitHub Repo)
# --------------------------------
st.subheader("Scenario Selection")

if not os.path.exists(SCENARIO_DIR):
    st.error("No scenarios folder found in repository.")
    st.stop()

scenario_files = sorted([
    f for f in os.listdir(SCENARIO_DIR)
    if f.endswith(".json")
])

scenario_name = st.selectbox(
    "Select Scenario",
    scenario_files
)

scenario_path = os.path.join(SCENARIO_DIR, scenario_name)

# --------------------------------
# Backend Mode Controls
# --------------------------------
if backend_online:
    st.success("Backend connected")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Start Testbed"):
            backend_post("/api/testbed/start",
                         json={"scenario_path": scenario_path})
            st.success("Testbed started")

    with col2:
        if st.button("■ Stop Testbed"):
            backend_post("/api/testbed/stop")
            st.warning("Testbed stopped")

else:
    st.warning("Backend not connected. Running in Streamlit-only mode.")
    st.info("Scenario will be simulated from repository files.")

# --------------------------------
# Load Scenario (for demo mode)
# --------------------------------
with open(scenario_path) as f:
    scenario = json.load(f)

duration = scenario["duration_seconds"]
phases = scenario["phases"]

# --------------------------------
# Demo Timeline Slider
# --------------------------------
st.divider()
st.subheader("Monitoring")

t = st.slider(
    "Simulation Time (seconds)",
    min_value=0,
    max_value=duration,
    value=0,
    step=1
)

# --------------------------------
# Get Active Phase
# --------------------------------
def get_state(t):
    for p in phases:
        if p["start"] <= t < p["end"]:
            return p
    return {"network":"normal","auth":"normal","device":"normal"}

state = get_state(t)

# --------------------------------
# Display Sensor States
# --------------------------------
def show_sensor(title, attack):
    st.subheader(title)
    if attack == "normal":
        st.success("Normal Operation")
    else:
        st.error(f"⚠ Attack Active: {attack}")

col1, col2, col3 = st.columns(3)
with col1:
    show_sensor("Network Sensor", state["network"])
with col2:
    show_sensor("Authentication Sensor", state["auth"])
with col3:
    show_sensor("Device Sensor", state["device"])

# --------------------------------
# Attack Summary Table
# --------------------------------
st.divider()
st.subheader("Current Attack Summary")

df = pd.DataFrame([
    {"Sensor":"Network", "Event":state["network"]},
    {"Sensor":"Authentication", "Event":state["auth"]},
    {"Sensor":"Device", "Event":state["device"]}
])

def style_row(row):
    if row["Event"] != "normal":
        return ["background:#ffe5e5; color:#b00020"]*len(row)
    return [""]*len(row)

st.dataframe(df.style.apply(style_row, axis=1),
             use_container_width=True)

# --------------------------------
# Footer
# --------------------------------
st.caption(
    "Streamlit-only mode uses scenario definitions from the GitHub repository. "
    "Live data generation requires the TCP backend."
)
