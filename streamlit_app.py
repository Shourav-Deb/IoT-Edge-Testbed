# streamlit_app.py
# EWAD Streamlit Demo Application


import streamlit as st
import json
import os
import pandas as pd

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Edge IoT Device Sensors",
    layout="wide"
)

# -------------------------------------------------
# UI Styling
# -------------------------------------------------
st.markdown("""
<style>
body { background-color:#f4f7ff; }
h1, h2, h3 { color:#1a73e8; }

.badge-live {
    background:#1a73e8;
    color:white;
    padding:6px 14px;
    border-radius:999px;
    font-weight:bold;
}

.badge-off {
    background:#cfd7e6;
    color:#1f2937;
    padding:6px 14px;
    border-radius:999px;
    font-weight:bold;
}

.attack-box {
    background:#ffe5e5;
    color:#b00020;
    padding:12px;
    border-radius:10px;
    font-weight:bold;
}

.normal-box {
    background:#eaf1ff;
    color:#0b296b;
    padding:12px;
    border-radius:10px;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Title
# -------------------------------------------------
st.title("Edge IoT Device Sensors")
st.caption("Scenario-Driven IoT Edge Testbed (Streamlit Demo Mode)")

# -------------------------------------------------
# Session State Initialization
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = False

if "t" not in st.session_state:
    st.session_state.t = 0

if "completed" not in st.session_state:
    st.session_state.completed = False

# -------------------------------------------------
# Load Scenarios from Repository
# -------------------------------------------------
SCENARIO_DIR = "scenarios"

if not os.path.exists(SCENARIO_DIR):
    st.error("❌ 'scenarios/' folder not found in repository.")
    st.stop()

scenario_files = sorted(
    [f for f in os.listdir(SCENARIO_DIR) if f.endswith(".json")]
)

st.subheader("Scenario Selection")
scenario_name = st.selectbox("Choose Scenario", scenario_files)

scenario_path = os.path.join(SCENARIO_DIR, scenario_name)

with open(scenario_path) as f:
    scenario = json.load(f)

duration = scenario["duration_seconds"]
phases = scenario["phases"]

# -------------------------------------------------
# Testbed Controls
# -------------------------------------------------
st.divider()
st.subheader("Testbed Control")

col1, col2, col3 = st.columns([2,2,2])

with col1:
    if st.button("▶ ON", disabled=st.session_state.running):
        st.session_state.running = True
        st.session_state.completed = False
        st.session_state.t = 0   # reset time

with col2:
    if st.button("■ OFF"):
        st.session_state.running = False

with col3:
    if st.session_state.running:
        st.markdown('<span class="badge-live">LIVE</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge-off">OFF</span>', unsafe_allow_html=True)

# -------------------------------------------------
# Auto Refresh (CORRECT way)
# -------------------------------------------------
if st.session_state.running:
    st.autorefresh(interval=1000, key="ewad_tick")

# -------------------------------------------------
# Time Progression
# -------------------------------------------------
if st.session_state.running:
    st.session_state.t += 1

    if st.session_state.t >= duration:
        st.session_state.t = duration
        st.session_state.running = False
        st.session_state.completed = True

# -------------------------------------------------
# Timeline Indicator (Read-only)
# -------------------------------------------------
st.slider(
    "Simulation Time (seconds)",
    min_value=0,
    max_value=duration,
    value=st.session_state.t,
    step=1,
    disabled=True
)

# -------------------------------------------------
# Completion Message
# -------------------------------------------------
if st.session_state.completed:
    st.success("✅ Scenario has been completed automatically.")

# -------------------------------------------------
# Determine Current Phase
# -------------------------------------------------
def get_state(t):
    for p in phases:
        if p["start"] <= t < p["end"]:
            return p
    return {"network":"normal","auth":"normal","device":"normal"}

state = get_state(st.session_state.t)

# -------------------------------------------------
# Monitoring Section
# -------------------------------------------------
st.divider()
st.subheader("Monitoring")

def show_sensor(title, attack):
    st.subheader(title)
    if attack == "normal":
        st.markdown(
            '<div class="normal-box">Normal Operation</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="attack-box">⚠ Attack Active: {attack}</div>',
            unsafe_allow_html=True
        )

c1, c2, c3 = st.columns(3)

with c1:
    show_sensor("Network Sensor", state["network"])

with c2:
    show_sensor("Authentication Sensor", state["auth"])

with c3:
    show_sensor("Device Sensor", state["device"])

# -------------------------------------------------
# Attack Summary Table
# -------------------------------------------------
st.divider()
st.subheader("Current Attack Summary")

df = pd.DataFrame([
    {"Sensor": "Network", "Event": state["network"]},
    {"Sensor": "Authentication", "Event": state["auth"]},
    {"Sensor": "Device", "Event": state["device"]}
])

def style_row(row):
    if row["Event"] != "normal":
        return ["background:#ffe5e5; color:#b00020; font-weight:bold"] * len(row)
    return [""] * len(row)

st.dataframe(
    df.style.apply(style_row, axis=1),
    use_container_width=True
)

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.caption(
    "Streamlit demo mode uses scenario definitions from the repository. "
    "Live TCP sensor generation runs in the Flask backend (local deployment)."
    "Shourav Deb"
)
