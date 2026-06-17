import streamlit as st
import pandas as pd
import re

# Page setup
st.set_page_config(page_title="SIEM Security Dashboard", layout="wide")

st.title("🛡️ SIEM Security Log Analyzer Dashboard")

LOG_FILE = "server_logs.txt"

# Log pattern
pattern = r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - IP: \[(?P<ip>.*?)\] - Status: \[(?P<status>.*?)\] - User: \[(?P<user>.*?)\]"


# Load logs
def load_logs():
    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()

        data = []

        for line in lines:
            match = re.search(pattern, line)
            if match:
                data.append(match.groupdict())

        df = pd.DataFrame(data)

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df

    except FileNotFoundError:
        st.error("❌ server_logs.txt not found!")
        return pd.DataFrame()


df = load_logs()

if df.empty:
    st.warning("No log data found.")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

status_filter = st.sidebar.multiselect(
    "Status",
    df["status"].unique(),
    default=df["status"].unique()
)

user_filter = st.sidebar.multiselect(
    "User",
    df["user"].unique(),
    default=df["user"].unique()
)

ip_filter = st.sidebar.multiselect(
    "IP Address",
    df["ip"].unique(),
    default=df["ip"].unique()
)

filtered_df = df[
    (df["status"].isin(status_filter)) &
    (df["user"].isin(user_filter)) &
    (df["ip"].isin(ip_filter))
]

# ---------------- TABLE ----------------
st.subheader("📄 Log Data")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- METRICS ----------------
st.subheader("📊 Quick Stats")

col1, col2, col3 = st.columns(3)

col1.metric("Total Logs", len(filtered_df))
col2.metric("SUCCESS", len(filtered_df[filtered_df["status"] == "SUCCESS"]))
col3.metric("FAILED", len(filtered_df[filtered_df["status"] == "FAILED"]))

# ---------------- CHARTS ----------------

st.subheader("📊 Login Status Distribution")
status_counts = filtered_df["status"].value_counts()
st.bar_chart(status_counts)

st.subheader("🚨 Failed Logins by User")

failed_df = filtered_df[filtered_df["status"] == "FAILED"]
failed_by_user = failed_df["user"].value_counts()

if not failed_by_user.empty:
    st.bar_chart(failed_by_user)
else:
    st.info("No failed logins found.")

st.subheader("⚠️ Failed Logins by IP")

failed_by_ip = failed_df["ip"].value_counts()

if not failed_by_ip.empty:
    st.bar_chart(failed_by_ip)
else:
    st.info("No failed login activity.")

st.subheader("📈 Login Activity Over Time (Hourly)")

time_series = filtered_df.groupby(filtered_df["timestamp"].dt.hour).size()
st.line_chart(time_series)