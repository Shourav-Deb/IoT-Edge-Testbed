# streamlit_app.py



import streamlit as st
import pandas as pd
import json
import time
import os

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Edge IoT Device Sensors",
    layout="wide"
)

# -------------------------------------------------
# UI Styling (White & Blue)
# -------------------------------------------------
st.markdown("""
<style>
body { background-color:#f4f7ff; }
h1, h2, h3 { color:#1a73e8; }
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
# Session State
# -------------------------------------------------
if "running" not in st.session_state:
    st.session_state.running = False

if "t" not in st.session_state:
    st.session_state.t = 0

if "completed" not in st.session_state:
    st.session_state.completed = False

# -------------------------------------------------
# Load Scenarios from Repo
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
    if st.button("▶ ON"):
        st.session_state.running = True
        st.session_state.completed = False

with col2:
    if st.button("■ OFF"):
        st.session_state.running = False

with col3:
    if st.session_state.running:
        st.markdown("🟢 **LIVE**")
    else:
        st.markdown("⚪ **OFF**")

# -------------------------------------------------
# Timeline Logic
# -------------------------------------------------
if st.session_state.running:
    time.sleep(1)
    st.session_state.t += 1

    if st.session_state.t >= duration:
        st.session_state.running = False
        st.session_state.completed = True
        st.session_state.t = duration

t = st.slider(
    "Simulation Time (seconds)",
    min_value=0,
    max_value=duration,
    value=st.session_state.t,
    step=1
)

# -------------------------------------------------
# Scenario Completion Popup
# -------------------------------------------------
if st.session_state.completed:
    st.success("✅ Scenario has been completed.")

# -------------------------------------------------
# Get Current Phase
# -------------------------------------------------
def get_state(t):
    for p in phases:
        if p["start"] <= t < p["end"]:
            return p
    return {
        "network": "normal",
        "auth": "normal",
        "device": "normal"
    }

state = get_state(t)

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

col1, col2, col3 = st.columns(3)

with col1:
    show_sensor("Network Sensor", state["network"])

with col2:
    show_sensor("Authentication Sensor", state["auth"])

with col3:
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
    "Streamlit-only demo mode | Shourav Deb "
    "Live TCP sensor generation runs in the Flask backend (local deployment)."
)
