import streamlit as st
import pandas as pd
from db import create_tables, get_connection
from chatbot import get_response

st.set_page_config(page_title="AI Fitness Assistant", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #f8fafc;
}

/* Page width */
.block-container {
    max-width: 1200px;
    margin: auto;
    padding-top: 2rem;
}

/* Headings */
h1 {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0f172a;
}

h2 {
    color: #0f172a;
    margin-top: 2rem;
}

h3, h4 {
    color: #334155;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: white;
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 24px rgba(15,23,42,0.08);
}

/* Inputs */
input, textarea, select {
    background-color: white !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}

/* Dropdowns */
div[data-baseweb="select"] > div {
    background-color: white !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}

/* DataFrame */
.stDataFrame {
    background: white;
    border-radius: 14px;
    padding: 0.6rem;
    border: 1px solid #e2e8f0;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.5rem 1.4rem;
    border: none;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb);
}

/* Remove white block feeling */
[data-testid="stVerticalBlock"] > div {
    background: transparent;
}

/* Divider */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #e2e8f0, transparent);
}
</style>
""", unsafe_allow_html=True)

create_tables()

st.title("🏋️ AI Fitness Assistant")

# ---------------- DASHBOARD ----------------
st.markdown("## 📊 Dashboard Overview")
st.caption("Quick summary of your training journey")

conn = get_connection()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM workouts")
total_workouts = cur.fetchone()[0]

cur.execute("SELECT exercise FROM workouts ORDER BY date DESC LIMIT 1")
last = cur.fetchone()

cur.execute("SELECT exercise, MAX(weight) FROM workouts")
best = cur.fetchone()

conn.close()

c1, c2, c3 = st.columns(3)
c1.metric("Total Workouts", total_workouts)
c2.metric("Last Workout", last[0] if last else "—")
c3.metric("Best Lift", f"{best[0]} – {best[1]} kg" if best and best[1] else "—")

# ---------------- PROGRESS ----------------
st.markdown("## 📈 Progress")

range_option = st.selectbox("Select Range", ["Last 7 Days", "Last 30 Days", "All Time"])

if range_option == "Last 7 Days":
    date_condition = "date >= datetime('now', '-7 days')"
elif range_option == "Last 30 Days":
    date_condition = "date >= datetime('now', '-30 days')"
else:
    date_condition = "1=1"

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT DISTINCT exercise FROM workouts")
exercises = [r[0] for r in cur.fetchall()]

# Per-Exercise Stats Panel
if exercises:
    chosen = st.selectbox("Choose Exercise for Stats", exercises)

    cur.execute("""
        SELECT COUNT(*), MAX(weight), AVG(weight), SUM(sets * reps * weight)
        FROM workouts WHERE exercise = ?
    """, (chosen,))
    stats = cur.fetchone()

    a, b, c, d = st.columns(4)
    a.metric("Sessions", stats[0])
    b.metric("Max Weight", f"{stats[1]:.1f} kg" if stats[1] else "—")
    c.metric("Avg Weight", f"{stats[2]:.1f} kg" if stats[2] else "—")
    d.metric("Total Volume", int(stats[3]) if stats[3] else 0)

    cur.execute("""
        SELECT date, weight FROM workouts
        WHERE exercise = ? AND """ + date_condition + """
        ORDER BY date
    """, (chosen,))
    data = cur.fetchall()

    if data:
        df = pd.DataFrame(data, columns=["Date", "Weight"])
        df["Date"] = pd.to_datetime(df["Date"])
        st.line_chart(df.set_index("Date"))

conn.close()

# Frequency
st.markdown("### 📅 Workout Frequency")
conn = get_connection()
cur = conn.cursor()
cur.execute(f"""
    SELECT DATE(date), COUNT(*) FROM workouts
    WHERE {date_condition}
    GROUP BY DATE(date)
""")
freq = cur.fetchall()
conn.close()

if freq:
    df = pd.DataFrame(freq, columns=["Date", "Workouts"])
    df["Date"] = pd.to_datetime(df["Date"])
    st.bar_chart(df.set_index("Date"))

# Volume
st.markdown("### 🧮 Total Training Volume")
conn = get_connection()
cur = conn.cursor()
cur.execute(f"""
    SELECT DATE(date), SUM(sets * reps * weight) FROM workouts
    WHERE {date_condition}
    GROUP BY DATE(date)
""")
vol = cur.fetchall()
conn.close()

if vol:
    df = pd.DataFrame(vol, columns=["Date", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"])
    st.line_chart(df.set_index("Date"))

# ---------------- ADD WORKOUT ----------------
st.markdown("## ➕ Add Workout")

exercise = st.text_input("Exercise Name")
sets = st.number_input("Sets", min_value=1)
reps = st.number_input("Reps", min_value=1)
weight = st.number_input("Weight (kg)", min_value=0.0)

if st.button("Add Workout"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO workouts (exercise, sets, reps, weight) VALUES (?, ?, ?, ?)",
        (exercise, sets, reps, weight)
    )
    conn.commit()
    conn.close()
    st.success("Workout added!")

# ---------------- HISTORY ----------------
st.markdown("## 📋 Workout History")

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, exercise, sets, reps, weight, date FROM workouts ORDER BY date DESC")
rows = cur.fetchall()
conn.close()

if rows:
    df = pd.DataFrame(rows, columns=["ID", "Exercise", "Sets", "Reps", "Weight", "Date"])
    st.dataframe(df, use_container_width=True)

# Export
st.markdown("### 📤 Export Workouts")
if rows:
    export_df = df.drop(columns=["ID"])
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "workouts.csv", "text/csv")

# Delete
st.markdown("### 🗑️ Delete Workout")
delete_id = st.number_input("Workout ID", min_value=1, step=1)
if st.button("Delete"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM workouts WHERE id = ?", (delete_id,))
    conn.commit()
    conn.close()
    st.success("Deleted")

# Edit
st.markdown("### ✏️ Edit Workout")
edit_id = st.number_input("Edit ID", min_value=1, step=1, key="edit")
new_ex = st.text_input("New Exercise")
new_sets = st.number_input("New Sets", min_value=1)
new_reps = st.number_input("New Reps", min_value=1)
new_weight = st.number_input("New Weight", min_value=0.0)

if st.button("Update"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE workouts SET exercise=?, sets=?, reps=?, weight=? WHERE id=?
    """, (new_ex, new_sets, new_reps, new_weight, edit_id))
    conn.commit()
    conn.close()
    st.success("Updated")

# ---------------- AI ----------------
st.markdown("## 🤖 AI Fitness Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

msg = st.text_input("Ask me anything about fitness")

if st.button("Send") and msg:
    reply = get_response(msg)
    st.session_state.chat.append(("You", msg))
    st.session_state.chat.append(("AI", reply))

for s, m in st.session_state.chat:
    st.write(f"**{s}:** {m}")
