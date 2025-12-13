# streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import json
import time
import os

BACKEND = os.environ.get("EWAD_BACKEND", "http://localhost:5000")

st.set_page_config(
    page_title="Edge IoT Device Sensors",
    layout="wide"
)


# -----------------------------
st.markdown("""
<style>
body { background-color: #f4f7ff; }
h1, h2, h3 { color: #1a73e8; }
.attack { background-color: #ffe5e5; color: #b00020; }
.status { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Header
# -----------------------------
st.title("Edge IoT Device Sensors")
st.caption("Centralized TCP Scenario-Driven Testbed (Streamlit UI)")

# -----------------------------
# Testbed Controls
# -----------------------------
col1, col2, col3 = st.columns([2,2,2])

with col1:
    if st.button("▶ Start Testbed"):
        requests.post(f"{BACKEND}/api/testbed/start")
        st.success("Testbed started")

with col2:
    if st.button("■ Stop Testbed"):
        requests.post(f"{BACKEND}/api/testbed/stop")
        st.warning("Testbed stopped")

with col3:
    uploaded = st.file_uploader("Upload Scenario (JSON)", type=["json"])
    if uploaded:
        files = {"file": uploaded}
        requests.post(f"{BACKEND}/api/scenario/upload", files=files)
        st.success("Scenario uploaded")

# -----------------------------
# Status
# -----------------------------
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


status = backend_get("/api/testbed/status")

if status is None:
    st.warning("Backend not connected. Running in Streamlit-only mode.")
    st.stop()

if status.get("running"):
    st.markdown("🟢 **LIVE — Testbed Running**")
else:
    st.markdown("⚪ **Idle**")

st.divider()

# -----------------------------
# Load Latest Testbed File
# -----------------------------
files_resp = requests.get(f"{BACKEND}/api/testbed/files").json()
files = files_resp.get("files", [])

if not files:
    st.info("Currently Sleeping — No testbed data yet.")
    st.stop()

latest = files[-1]["path"]

rows = requests.post(
    f"{BACKEND}/api/testbed/load",
    json={"path": latest}
).json().get("rows", [])

if not rows:
    st.stop()

# -----------------------------
# Convert to DataFrames
# -----------------------------
def to_df(sensor):
    data = []
    for r in rows:
        if r["sensor"] == sensor:
            row = r["values"].copy()
            row["time"] = time.strftime("%H:%M:%S", time.localtime(r["timestamp"]))
            data.append(row)
    return pd.DataFrame(data)

df_net = to_df("network")
df_auth = to_df("auth")
df_dev = to_df("device")

# -----------------------------
# Display Tables
# -----------------------------
def show_table(title, df):
    st.subheader(title)
    if df.empty:
        st.write("No data")
        return

    def style(row):
        if row.get("event") != "Normal":
            return ["background-color:#ffe5e5; color:#b00020; font-weight:bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df.tail(25).style.apply(style, axis=1),
        use_container_width=True,
        height=320
    )

show_table("Network", df_net)
show_table("Authentication", df_auth)
show_table("Device", df_dev)

# -----------------------------
# Attack Alert
# -----------------------------
for r in rows[-5:]:
    if r["values"].get("event") != "Normal":
        st.error(f"⚠ Attack Detected: {r['values']['event']}")
        break

