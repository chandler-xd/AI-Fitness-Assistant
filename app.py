import streamlit as st
import pandas as pd
from db import create_tables, get_connection
from chatbot import get_response
import plotly.graph_objects as go

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

.block-container {
    max-width: 1200px;
    margin: auto;
    padding-top: 2rem;
}

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

div[data-testid="stMetric"] {
    background: white;
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 8px 24px rgba(15,23,42,0.08);
}

div[data-testid="stMetric"] label {
    font-size: 0.875rem;
    color: #64748b;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.875rem;
    font-weight: 600;
    color: #0f172a;
}

input, textarea, select {
    background-color: white !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}

div[data-baseweb="select"] > div {
    background-color: white !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    border: 1px solid #e2e8f0 !important;
}

.stDataFrame {
    background: white;
    border-radius: 14px;
    padding: 0.6rem;
    border: 1px solid #e2e8f0;
}

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

[data-testid="stVerticalBlock"] > div {
    background: transparent;
}

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

cur.execute("SELECT COUNT(DISTINCT DATE(date)) FROM workouts")
total_workouts = cur.fetchone()[0]

cur.execute("SELECT exercise FROM workouts ORDER BY date DESC LIMIT 1")
last = cur.fetchone()

cur.execute("SELECT exercise, weight FROM workouts ORDER BY weight DESC LIMIT 1")
best = cur.fetchone()

conn.close()

c1, c2, c3 = st.columns(3)
c1.metric("Total Workouts", total_workouts)
c2.metric("Last Workout", last[0] if last else "—")
c3.metric("Best Lift", f"{best[0]} – {int(best[1])} kg" if best and best[1] else "—")

# ---------------- PROGRESS ----------------
st.markdown("## 📈 Progress")

range_option = st.selectbox("Select Range", ["Last 7 Days", "Last 30 Days", "All Time"])

if range_option == "Last 7 Days":
    days_back = 7
elif range_option == "Last 30 Days":
    days_back = 30
else:
    days_back = 999999

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT DISTINCT exercise FROM workouts ORDER BY exercise")
exercises = [r[0] for r in cur.fetchall()]

if exercises:
    chosen = st.selectbox("Choose Exercise for Stats", exercises)

    cur.execute("""
        SELECT COUNT(DISTINCT DATE(date)), MAX(weight), AVG(weight), SUM(sets * reps * weight)
        FROM workouts WHERE exercise = ?
    """, (chosen,))
    stats = cur.fetchone()

    a, b, c, d = st.columns(4)
    a.metric("Sessions", stats[0] if stats[0] else 0)
    b.metric("Max Weight", f"{stats[1]:.1f} kg" if stats[1] else "—")
    c.metric("Avg Weight", f"{stats[2]:.1f} kg" if stats[2] else "—")
    d.metric("Total Volume", f"{int(stats[3]):,}" if stats[3] else "0")

    # Smooth progression chart
    cur.execute("""
        SELECT DATE(date) AS day, AVG(weight) AS avg_weight
        FROM workouts
        WHERE exercise = ? AND date >= datetime('now', '-' || ? || ' days')
        GROUP BY day
        ORDER BY day
    """, (chosen, days_back))
    data = cur.fetchall()

    if data:
        df = pd.DataFrame(data, columns=["Day", "Weight"])
        df['Day'] = pd.to_datetime(df['Day'])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Day'],
            y=df['Weight'],
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3, shape='spline'),
            marker=dict(size=8, color='#3b82f6'),
            hovertemplate='%{y:.1f} kg<extra></extra>'
        ))
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                showgrid=True,
                gridcolor='#f1f5f9',
                zeroline=False,
                tickformat='%b %d'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#f1f5f9',
                zeroline=False,
                ticksuffix=' kg'
            ),
            margin=dict(l=20, r=20, t=20, b=20),
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

conn.close()

# ---------------- ANALYTICS ----------------
st.markdown("### 📊 Training Analytics")

col_f, col_v = st.columns(2)

with col_f:
    st.markdown("#### 📅 Workout Frequency")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT strftime('%Y-%m', date) AS month, COUNT(DISTINCT DATE(date))
        FROM workouts
        WHERE date >= datetime('now', '-' || ? || ' days')
        GROUP BY month
        ORDER BY month
    """, (days_back,))
    freq = cur.fetchall()
    conn.close()

    if freq:
        df = pd.DataFrame(freq, columns=["Month", "Days"])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['Month'],
            y=df['Days'],
            marker=dict(color='#3b82f6'),
            hovertemplate='%{y} days<extra></extra>'
        ))
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', zeroline=False),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)

with col_v:
    st.markdown("#### 🧮 Total Training Volume")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT strftime('%Y-%m', date) AS month, SUM(sets * reps * weight)
        FROM workouts
        WHERE date >= datetime('now', '-' || ? || ' days')
        GROUP BY month
        ORDER BY month
    """, (days_back,))
    vol = cur.fetchall()
    conn.close()

    if vol:
        df = pd.DataFrame(vol, columns=["Month", "Volume"])
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Month'],
            y=df['Volume'],
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3, shape='spline'),
            marker=dict(size=8, color='#3b82f6'),
            hovertemplate='%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#f1f5f9', 
                zeroline=False,
                tickformat=','
            ),
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ---------------- ADD WORKOUT ----------------
st.markdown("## ➕ Add Workout")

exercise = st.text_input("Exercise Name")
sets = st.number_input("Sets", min_value=1, value=3)
reps = st.number_input("Reps", min_value=1, value=10)
weight = st.number_input("Weight (kg)", min_value=0.0, value=20.0)

if st.button("Add Workout"):
    if exercise.strip():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO workouts (exercise, sets, reps, weight) VALUES (?, ?, ?, ?)",
            (exercise, sets, reps, weight)
        )
        conn.commit()
        conn.close()
        st.success("Workout added!")
        st.rerun()
    else:
        st.error("Please enter an exercise name")

# ---------------- HISTORY ----------------
st.markdown("## 📋 Workout History")

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT id, exercise, sets, reps, weight, date FROM workouts ORDER BY date DESC LIMIT 50")
rows = cur.fetchall()
conn.close()

if rows:
    df = pd.DataFrame(rows, columns=["ID", "Exercise", "Sets", "Reps", "Weight", "Date"])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No workouts logged yet.")

# Export
st.markdown("### 📤 Export Workouts")
if rows:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT exercise, sets, reps, weight, date FROM workouts ORDER BY date DESC")
    all_rows = cur.fetchall()
    conn.close()
    
    export_df = pd.DataFrame(all_rows, columns=["Exercise", "Sets", "Reps", "Weight", "Date"])
    csv = export_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "workouts.csv", "text/csv")

# Delete
st.markdown("### 🗑️ Delete Workout")
if rows:
    delete_col1, delete_col2 = st.columns([3, 1])
    with delete_col1:
        delete_id = st.number_input("Workout ID", min_value=1, step=1, key="delete_id")
    with delete_col2:
        st.write("")
        st.write("")
        if st.button("Delete", key="delete_btn"):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM workouts WHERE id = ?", (delete_id,))
            conn.commit()
            conn.close()
            st.success("Deleted")
            st.rerun()

# Edit
st.markdown("### ✏️ Edit Workout")
if rows:
    edit_id = st.number_input("Edit ID", min_value=1, step=1, key="edit")
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT exercise, sets, reps, weight FROM workouts WHERE id = ?", (edit_id,))
    existing = cur.fetchone()
    conn.close()
    
    if existing:
        st.info(f"Current: {existing[0]} - {existing[1]} sets × {existing[2]} reps @ {existing[3]} kg")
    
    new_ex = st.text_input("New Exercise", value=existing[0] if existing else "")
    new_sets = st.number_input("New Sets", min_value=1, value=int(existing[1]) if existing else 3)
    new_reps = st.number_input("New Reps", min_value=1, value=int(existing[2]) if existing else 10)
    new_weight = st.number_input("New Weight", min_value=0.0, value=float(existing[3]) if existing else 20.0)

    if st.button("Update"):
        if new_ex.strip():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE workouts SET exercise=?, sets=?, reps=?, weight=? WHERE id=?
            """, (new_ex, new_sets, new_reps, new_weight, edit_id))
            conn.commit()
            conn.close()
            st.success("Updated")
            st.rerun()
        else:
            st.error("Please enter an exercise name")

# ---------------- AI ----------------
st.markdown("## 🤖 AI Fitness Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

msg = st.text_input("Ask me anything about fitness", key="chat_input")

if st.button("Send") and msg:
    reply = get_response(msg)
    st.session_state.chat.append(("You", msg))
    st.session_state.chat.append(("AI", reply))

for s, m in st.session_state.chat:
    if s == "You":
        st.markdown(f"**{s}:** {m}")
    else:
        st.markdown(f"**{s}:** {m}")