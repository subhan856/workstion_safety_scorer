"""
Workstation Safety Scorer v4.0
ICT in Health & Ergonomics | UET Taxila Engineering
Enhanced: 30 questions, health profile, PDF auto-generation,
password reset, smart risk suggestions, professional UI
"""

import streamlit as st
import sqlite3
import hashlib
import json
import os
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from fpdf import FPDF
import io
import base64
import re

# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Workstation Safety Scorer",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# GLOBAL CSS  –  Luxe Medical / Precision-Tech aesthetic
# Fonts: Syne (display) + DM Sans (body) + JetBrains Mono (data)
# ---------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --bg:        #060B14;
  --bg2:       #0D1625;
  --bg3:       #121D30;
  --border:    rgba(99,179,237,0.18);
  --accent:    #38BDF8;
  --accent2:   #818CF8;
  --accent3:   #34D399;
  --danger:    #F87171;
  --warn:      #FBBF24;
  --text:      #F0F4FF;
  --muted:     #8899AA;
  --card-bg:   rgba(13,22,37,0.85);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Animated gradient mesh background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 15% 10%, rgba(56,189,248,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 80% at 85% 85%, rgba(129,140,248,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 40% 40% at 50% 50%, rgba(52,211,153,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: rgba(6,11,20,0.98) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ---- TYPOGRAPHY ---- */
h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.5px;
}

/* ---- CARDS ---- */
.glass-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 28px 32px;
    backdrop-filter: blur(24px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(99,179,237,0.08);
    margin-bottom: 20px;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.glass-card:hover {
    border-color: rgba(56,189,248,0.35);
    box-shadow: 0 12px 50px rgba(0,0,0,0.6), 0 0 0 1px rgba(56,189,248,0.1);
}

/* ---- KPI CARDS ---- */
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px 18px;
    text-align: center;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.kpi-card:hover::after { opacity: 1; }
.kpi-card:hover {
    border-color: rgba(56,189,248,0.4);
    transform: translateY(-2px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.5);
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    line-height: 1.1;
    text-shadow: 0 0 24px currentColor;
}
.kpi-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 2.5px;
    color: var(--muted);
    text-transform: uppercase;
    margin-top: 8px;
}
.kpi-sub { font-size: 0.75rem; color: var(--muted); margin-top: 4px; }

/* ---- BADGES ---- */
.badge-green { display:inline-flex;align-items:center;gap:5px;padding:5px 14px;border-radius:30px;font-family:'Syne',sans-serif;font-size:.72rem;font-weight:700;letter-spacing:1.5px;background:rgba(52,211,153,0.12);color:#34D399;border:1px solid rgba(52,211,153,0.35); }
.badge-amber { display:inline-flex;align-items:center;gap:5px;padding:5px 14px;border-radius:30px;font-family:'Syne',sans-serif;font-size:.72rem;font-weight:700;letter-spacing:1.5px;background:rgba(251,191,36,0.12);color:#FBBF24;border:1px solid rgba(251,191,36,0.35); }
.badge-red   { display:inline-flex;align-items:center;gap:5px;padding:5px 14px;border-radius:30px;font-family:'Syne',sans-serif;font-size:.72rem;font-weight:700;letter-spacing:1.5px;background:rgba(248,113,113,0.12);color:#F87171;border:1px solid rgba(248,113,113,0.35); }

/* ---- SECTION HEADING ---- */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 3.5px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

/* ---- WELCOME BANNER ---- */
.welcome-banner {
    background: linear-gradient(135deg, rgba(56,189,248,0.07) 0%, rgba(129,140,248,0.05) 50%, rgba(52,211,153,0.04) 100%);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 24px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.welcome-banner::before {
    content: '';
    position: absolute;
    top: -50%; right: -20%;
    width: 400px; height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56,189,248,0.05) 0%, transparent 70%);
}
.welcome-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.9rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1.2;
}
.welcome-title span { color: var(--accent); text-shadow: 0 0 30px rgba(56,189,248,0.5); }
.welcome-sub {
    font-size: 0.78rem;
    letter-spacing: 2.5px;
    color: var(--muted);
    margin-top: 8px;
    text-transform: uppercase;
    font-family: 'Syne', sans-serif;
}

/* ---- RISK BARS ---- */
.risk-bar-wrap { background:rgba(255,255,255,0.06);border-radius:4px;height:5px;margin-top:8px; }
.risk-bar-fill { height:100%;border-radius:4px;transition:width .8s cubic-bezier(.4,0,.2,1); }

/* ---- BUTTONS (ALL) ---- */
.stButton > button {
    background: linear-gradient(135deg, rgba(56,189,248,0.12), rgba(129,140,248,0.08)) !important;
    border: 1px solid rgba(56,189,248,0.45) !important;
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    text-transform: uppercase !important;
    transition: all 0.2s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(56,189,248,0.1), transparent);
    opacity: 0;
    transition: opacity 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(56,189,248,0.22), rgba(129,140,248,0.16)) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 25px rgba(56,189,248,0.3), 0 4px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-1px) !important;
    color: #fff !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 0 12px rgba(56,189,248,0.2) !important;
}

/* ---- INPUT LABELS ---- */
div[data-testid="stRadio"] > label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stNumberInput"] label {
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* Input boxes */
div[data-testid="stTextInput"] input,
div[data-testid="stPasswordInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input {
    background: rgba(13,22,37,0.9) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stPasswordInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
}

/* Selectbox */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(13,22,37,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--accent) !important;
}

/* Radio buttons */
div[data-testid="stRadio"] label {
    padding: 8px 16px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: background 0.2s, color 0.2s !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: var(--muted) !important;
}
div[data-testid="stRadio"] label:hover {
    background: rgba(56,189,248,0.1) !important;
    color: var(--accent) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,22,37,0.6) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 9px !important;
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(56,189,248,0.18), rgba(129,140,248,0.12)) !important;
    color: var(--accent) !important;
    border: 1px solid rgba(56,189,248,0.3) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: rgba(56,189,248,0.08) !important;
    color: var(--text) !important;
}

/* Dataframe */
.stDataFrame { border-radius: 14px !important; overflow: hidden !important; }

/* Expander */
.streamlit-expanderHeader {
    background: rgba(13,22,37,0.7) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    transition: background 0.2s !important;
}
.streamlit-expanderHeader:hover {
    background: rgba(56,189,248,0.08) !important;
    border-color: rgba(56,189,248,0.3) !important;
}

/* Question cards */
.q-card {
    background: rgba(13,22,37,0.7);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.q-card:hover {
    border-color: rgba(56,189,248,0.3);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
}
.q-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--accent);
    letter-spacing: 3px;
}
.q-text {
    font-size: 0.95rem;
    color: var(--text);
    margin: 6px 0 12px;
    line-height: 1.5;
    font-weight: 500;
}

/* Alert boxes */
.alert-danger {
    background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.4);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #FCA5A5;
    font-family: 'DM Sans', sans-serif;
}
.alert-success {
    background: rgba(52,211,153,0.1);
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #6EE7B7;
    font-family: 'DM Sans', sans-serif;
}
.alert-warn {
    background: rgba(251,191,36,0.1);
    border: 1px solid rgba(251,191,36,0.4);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #FDE68A;
    font-family: 'DM Sans', sans-serif;
}

/* Suggestion cards */
.suggest-card {
    background: linear-gradient(135deg, rgba(248,113,113,0.08), rgba(251,191,36,0.05));
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: 16px;
    padding: 20px 24px;
    margin: 8px 0;
}
.suggest-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 700;
    color: #FCA5A5;
    margin-bottom: 8px;
}
.suggest-item {
    font-size: 0.88rem;
    color: var(--muted);
    padding: 4px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.25); border-radius: 2px; }
::-webkit-scrollbar-track { background: transparent; }

/* Sidebar nav active */
.sidebar-nav-btn-active > button {
    background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(129,140,248,0.15)) !important;
    border-color: var(--accent) !important;
    color: #fff !important;
}

/* Number input */
[data-testid="stNumberInput"] button {
    background: rgba(56,189,248,0.1) !important;
    border-color: var(--border) !important;
    color: var(--accent) !important;
    transition: background 0.2s !important;
}
[data-testid="stNumberInput"] button:hover {
    background: rgba(56,189,248,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------
DB_PATH = "workstation_safety.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        username     TEXT UNIQUE NOT NULL,
        password     TEXT NOT NULL,
        full_name    TEXT NOT NULL,
        email        TEXT DEFAULT '',
        dept         TEXT DEFAULT 'Engineering',
        role         TEXT DEFAULT 'user',
        age          INTEGER DEFAULT 0,
        gender       TEXT DEFAULT '',
        height_cm    REAL DEFAULT 0,
        weight_kg    REAL DEFAULT 0,
        bmi          REAL DEFAULT 0,
        activity     TEXT DEFAULT '',
        medical_hist TEXT DEFAULT '',
        reset_token  TEXT DEFAULT '',
        created      TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS assessments (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER,
        username   TEXT,
        score      REAL,
        risk_level TEXT,
        answers    TEXT,
        cat_scores TEXT,
        notes      TEXT DEFAULT '',
        created    TEXT DEFAULT (datetime('now')),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
    # Migrations – add columns if they don't exist
    for col_def in [
        ("age",          "INTEGER DEFAULT 0"),
        ("gender",       "TEXT DEFAULT ''"),
        ("height_cm",    "REAL DEFAULT 0"),
        ("weight_kg",    "REAL DEFAULT 0"),
        ("bmi",          "REAL DEFAULT 0"),
        ("activity",     "TEXT DEFAULT ''"),
        ("medical_hist", "TEXT DEFAULT ''"),
        ("reset_token",  "TEXT DEFAULT ''"),
    ]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_def[0]} {col_def[1]}")
        except Exception:
            pass

    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    demo_pw  = hashlib.sha256("demo123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username,password,full_name,email,dept,role) VALUES (?,?,?,?,?,?)",
              ("admin", admin_pw, "Administrator", "admin@uet.edu.pk", "IT", "admin"))
    c.execute("INSERT OR IGNORE INTO users (username,password,full_name,email,dept,role,age,gender,height_cm,weight_kg,activity) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
              ("asnan", demo_pw, "Muhammad Asnan", "asnan@uet.edu.pk", "Engineering", "user", 22, "Male", 175, 70, "Moderate"))
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def login_user(username, password):
    conn = get_conn()
    row = conn.execute(
        "SELECT id,username,full_name,dept,role,age,gender,height_cm,weight_kg,bmi,activity,medical_hist FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    ).fetchone()
    conn.close()
    if row:
        return {
            "id": row[0], "username": row[1], "full_name": row[2],
            "dept": row[3], "role": row[4], "age": row[5],
            "gender": row[6], "height_cm": row[7], "weight_kg": row[8],
            "bmi": row[9], "activity": row[10], "medical_hist": row[11]
        }
    return None

def register_user(username, password, full_name, email, dept):
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO users (username,password,full_name,email,dept) VALUES (?,?,?,?,?)",
            (username, hash_pw(password), full_name, email, dept)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def save_health_profile(username, age, gender, height_cm, weight_kg, activity, medical_hist):
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1) if height_cm > 0 else 0
    conn = get_conn()
    conn.execute(
        "UPDATE users SET age=?,gender=?,height_cm=?,weight_kg=?,bmi=?,activity=?,medical_hist=? WHERE username=?",
        (age, gender, height_cm, weight_kg, bmi, activity, medical_hist, username)
    )
    conn.commit()
    conn.close()
    return bmi

def update_password(username, new_password):
    conn = get_conn()
    conn.execute("UPDATE users SET password=?, reset_token='' WHERE username=?",
                 (hash_pw(new_password), username))
    conn.commit()
    conn.close()

def username_exists(username):
    conn = get_conn()
    row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row is not None

# ---------------------------------------------------------------------
# ASSESSMENT DATA – 30 QUESTIONS
# ---------------------------------------------------------------------
# format: (id, category, question_text, weight, type, options)
# type = "likert" | "mcq"
QUESTIONS = [
    # Chair & Posture (5)
    (1,  "Chair & Posture",   "Is your chair height adjusted so your feet rest flat on the floor or on a footrest?", 12, "likert", None),
    (2,  "Chair & Posture",   "Does your chair provide adequate lumbar (lower-back) support?",                        10, "likert", None),
    (3,  "Chair & Posture",   "Are your knees at approximately 90 degrees while seated?",                             9, "likert", None),
    (4,  "Chair & Posture",   "How would you describe your typical sitting posture during work?",                      9, "mcq",
         ["Upright with back fully supported", "Slightly slouched forward", "Heavily slouched / hunched", "Leaning to one side", "I change posture frequently"]),
    (5,  "Chair & Posture",   "Does your seat pan depth allow a 2-3 finger gap behind your knees?",                   7, "likert", None),

    # Screen & Display (4)
    (6,  "Screen & Display",  "Is the top of your monitor at or slightly below eye level?",                          11, "likert", None),
    (7,  "Screen & Display",  "Is the viewing distance between 50–70 cm from your eyes?",                            10, "likert", None),
    (8,  "Screen & Display",  "Is the screen free from glare and reflections?",                                       9, "likert", None),
    (9,  "Screen & Display",  "How many hours per day do you spend looking at a screen?",                             8, "mcq",
         ["Less than 2 hours", "2–4 hours", "4–6 hours", "6–8 hours", "More than 8 hours"]),

    # Keyboard & Mouse (4)
    (10, "Keyboard & Mouse",  "Are your wrists in a neutral (flat) position while typing?",                          11, "likert", None),
    (11, "Keyboard & Mouse",  "Is your mouse within easy reach without extending or stretching your arm?",            8, "likert", None),
    (12, "Keyboard & Mouse",  "Are your elbows at roughly 90 degrees and close to your body while typing?",           8, "likert", None),
    (13, "Keyboard & Mouse",  "Which best describes your keyboard/mouse setup?",                                      7, "mcq",
         ["Standard keyboard on desk level", "Keyboard tray below desk level", "Laptop keyboard only", "External keyboard with laptop stand", "Split/ergonomic keyboard"]),

    # Lighting (3)
    (14, "Lighting",          "Is ambient lighting adequate and not causing eye strain?",                             9, "likert", None),
    (15, "Lighting",          "Is direct sunlight or artificial light avoided on your screen?",                       8, "likert", None),
    (16, "Lighting",          "Do you use blue-light filtering (glasses/software) for prolonged screen use?",         7, "likert", None),

    # Environment (4)
    (17, "Environment",       "Is the room temperature comfortable (approx. 20–24 degrees C)?",                      8, "likert", None),
    (18, "Environment",       "Is background noise at an acceptable level for focused work?",                         7, "likert", None),
    (19, "Environment",       "Is your workspace free from excessive clutter and disorganisation?",                   6, "likert", None),
    (20, "Environment",       "How would you rate the air quality / ventilation in your workspace?",                  6, "mcq",
         ["Excellent – fresh air circulation", "Good – occasionally stuffy", "Moderate – often stuffy", "Poor – stale / polluted air", "I work outdoors"]),

    # Work Habits (4)
    (21, "Work Habits",       "Do you take a short break (5–10 min) every 45–60 minutes?",                           10, "likert", None),
    (22, "Work Habits",       "Do you perform light stretching or movement during breaks?",                            9, "likert", None),
    (23, "Work Habits",       "Do you blink regularly and apply the 20-20-20 rule for eye health?",                   8, "likert", None),
    (24, "Work Habits",       "How often do you experience musculoskeletal pain (neck/back/wrist) after work?",        9, "mcq",
         ["Never", "Rarely (once a month)", "Sometimes (weekly)", "Often (several times a week)", "Always (daily)"]),

    # Accessories (3)
    (25, "Accessories",       "Do you use a document holder when referencing printed papers?",                         6, "likert", None),
    (26, "Accessories",       "Is a wrist rest available and used correctly during keyboard/mouse use?",               6, "likert", None),
    (27, "Accessories",       "Which ergonomic accessories do you currently use?",                                     6, "mcq",
         ["None", "Wrist rest only", "Monitor stand + wrist rest", "Full ergonomic setup (stand, wrist rest, foot rest)", "Standing desk / sit-stand arrangement"]),

    # Psychosocial (3)
    (28, "Psychosocial",      "Do you feel comfortable with your current workload and stress level?",                  8, "likert", None),
    (29, "Psychosocial",      "Do you feel that your employer supports your health and wellbeing at work?",             6, "likert", None),
    (30, "Psychosocial",      "How would you describe your overall mental wellbeing during a typical workday?",         7, "mcq",
         ["Excellent – calm and focused", "Good – mostly positive", "Moderate – some anxiety/stress", "Poor – frequently stressed", "Very poor – overwhelmed daily"]),
]

# Likert scoring map
LIKERT = {
    "Never (0%)":      0,
    "Rarely (25%)":    1,
    "Sometimes (50%)": 2,
    "Often (75%)":     3,
    "Always (100%)":   4,
}

# MCQ scoring: index 0 = best = 4, last = worst = 0 (reversed for pain/hours questions)
# We handle per-question below in compute_scores

# Questions where HIGHER index = WORSE (reverse score)
REVERSE_MCQ = {4, 9, 24, 30}   # posture, screen hours, pain frequency, mental wellbeing

CATEGORIES = [
    "Chair & Posture", "Screen & Display", "Keyboard & Mouse",
    "Lighting", "Environment", "Work Habits", "Accessories", "Psychosocial",
]

CAT_COLORS = {
    "Chair & Posture":  "#38BDF8",
    "Screen & Display": "#818CF8",
    "Keyboard & Mouse": "#34D399",
    "Lighting":         "#FBBF24",
    "Environment":      "#F87171",
    "Work Habits":      "#A78BFA",
    "Accessories":      "#FB923C",
    "Psychosocial":     "#F472B6",
}

CAT_ICONS = {
    "Chair & Posture":  "🪑",
    "Screen & Display": "🖥️",
    "Keyboard & Mouse": "⌨️",
    "Lighting":         "💡",
    "Environment":      "🌡️",
    "Work Habits":      "⏱️",
    "Accessories":      "🎧",
    "Psychosocial":     "🧠",
}

RECOMMENDATIONS = {
    "Chair & Posture": [
        "Adjust chair height so feet rest flat; use a footrest if needed.",
        "Position lumbar support at the curve of your lower back (waist level).",
        "Set seat depth with a 2-3 finger gap between seat edge and back of knees.",
        "Keep thighs roughly parallel to the floor; avoid crossing legs.",
        "Try a chair with adjustable armrests to reduce shoulder tension.",
    ],
    "Screen & Display": [
        "Mount monitor so the top bezel aligns with eye level.",
        "Maintain a 50–70 cm viewing distance — arm's length is a good guide.",
        "Apply an anti-glare filter and angle screen away from windows.",
        "Increase font size rather than leaning forward to read.",
        "Use the 20-20-20 rule: every 20 min, look 20 ft away for 20 seconds.",
    ],
    "Keyboard & Mouse": [
        "Keep wrists flat; avoid bending up, down or sideways while typing.",
        "Place mouse directly beside the keyboard at the same height.",
        "Consider a split or ergonomic keyboard if wrist discomfort persists.",
        "Use keyboard shortcuts to reduce repetitive mouse movements.",
        "Rest wrists on a padded rest only during pauses, not actively typing.",
    ],
    "Lighting": [
        "Use indirect or diffused ambient lighting; avoid overhead fluorescent glare.",
        "Enable night/blue-light mode on all screens after 6 PM.",
        "Position desk perpendicular to windows to avoid direct glare.",
        "Ensure task lighting is adjustable and doesn't reflect on the screen.",
        "Blink consciously and use lubricating eye drops if eyes feel dry.",
    ],
    "Environment": [
        "Maintain 20–24°C using a fan, heater or HVAC to avoid fatigue.",
        "Use noise-cancelling headphones or white noise apps in loud environments.",
        "Ensure fresh air circulation — open a window or use an air purifier.",
        "Keep desk surface clean and organised to reduce cognitive load.",
        "Add indoor plants for improved air quality and mental wellbeing.",
    ],
    "Work Habits": [
        "Set a 45-minute recurring timer for movement breaks.",
        "During breaks: shoulder rolls, neck tilts, wrist circles, calf raises.",
        "Walk for at least 5 minutes every hour — even a short lap helps.",
        "Avoid eating lunch at your desk; a proper break resets focus.",
        "Hydrate regularly — dehydration worsens concentration and headaches.",
    ],
    "Accessories": [
        "Use a document holder at the same height and distance as your monitor.",
        "A padded wrist rest reduces pressure during mouse-intensive tasks.",
        "A laptop stand + external keyboard raises the screen to eye level.",
        "A sit-stand desk alternates posture and reduces prolonged sitting.",
        "Invest in a quality chair mat if your floor causes rolling resistance.",
    ],
    "Psychosocial": [
        "Break large tasks into smaller milestones to reduce overwhelm.",
        "Practise 5-minute breathing exercises (box breathing) between meetings.",
        "Communicate workload concerns to your supervisor proactively.",
        "Digital detox during lunch: no screens for at least 20 minutes.",
        "Use task-management tools to externalise mental to-do lists.",
    ],
}

# Smart high-risk alternatives (triggered when score < 40)
HIGH_RISK_ALTERNATIVES = {
    "Chair & Posture": [
        "🛋️ If you cannot adjust your chair, use a rolled towel as a lumbar support.",
        "📦 Place a box or footrest under your desk if feet don't touch the floor.",
        "🧘 Try seated yoga stretches every 30 minutes to counteract poor posture.",
        "💻 Use a standing desk converter if prolonged sitting is unavoidable.",
        "🏥 Consider a physiotherapy assessment if you experience regular back pain.",
    ],
    "Screen & Display": [
        "📚 Stack books under your monitor temporarily until you get a stand.",
        "🕶️ Blue-light glasses are an affordable way to reduce digital eye strain.",
        "📱 Enable Night Shift (iOS) or Night Mode (Android/Windows) immediately.",
        "🖼️ Move your monitor so no window is directly behind or in front of it.",
        "👁️ Download f.lux (free) to auto-adjust screen warmth based on time of day.",
    ],
    "Keyboard & Mouse": [
        "🖱️ Switch to a vertical mouse — prices start from ~$20 and drastically cut wrist strain.",
        "📱 Use voice dictation (built-in on Windows/Mac) to reduce typing time.",
        "💪 Squeeze a stress ball for 5 minutes daily to strengthen wrist tendons.",
        "🧤 Wear wrist compression sleeves if you already feel pain.",
        "⚕️ See a hand therapist if tingling or numbness occurs — may indicate carpal tunnel.",
    ],
    "Lighting": [
        "💡 Replace overhead bulbs with warm (3000K) LED panels to reduce harsh light.",
        "🌙 Enable Dark Mode on all apps immediately to cut screen brightness.",
        "🪟 Use blackout blinds or position your monitor facing away from windows.",
        "👓 Anti-reflective coating glasses are worthwhile for heavy screen users.",
        "💧 Preservative-free artificial tears (eye drops) relieve dry eyes from screen glare.",
    ],
    "Environment": [
        "🌡️ A small desk fan or portable heater costs under $20 and fixes thermal discomfort.",
        "🎧 Free apps like Noisli provide white noise to mask distracting sounds.",
        "🪟 Even 10 minutes outside during breaks dramatically improves air quality intake.",
        "🌿 A small desk plant (snake plant, pothos) naturally improves air quality.",
        "⚕️ Chronic noise exposure above 70 dB causes hearing fatigue — get an assessment.",
    ],
    "Work Habits": [
        "⏰ Install 'Stretchly' (free app) — it forces micro-breaks with guided stretches.",
        "🚶 Walk while on phone calls — this alone adds thousands of steps daily.",
        "💧 Set a water reminder every 30 minutes — dehydration is a leading cause of fatigue.",
        "🧘 The Headspace or Calm app offers 5-minute guided breaks for stress relief.",
        "⚕️ Persistent musculoskeletal pain warrants an occupational health referral.",
    ],
    "Accessories": [
        "📖 A $5 document holder saves significant neck strain during data-entry work.",
        "🖥️ A $15 laptop stand paired with a budget keyboard is a game-changer.",
        "🦶 A rolled towel under feet works as a free footrest alternative.",
        "🖱️ Use a mouse pad with built-in wrist gel rest for immediate relief.",
        "⚕️ If you experience repetitive strain, a formal ergonomic assessment is recommended.",
    ],
    "Psychosocial": [
        "📝 Write 3 priorities each morning — focus prevents cognitive overwhelm.",
        "🤝 Talk to your line manager about workload redistribution if stress is chronic.",
        "📵 Set phone-free periods using Do Not Disturb mode for deep work.",
        "🧠 MindShift and Wysa are free mental wellness apps designed for work stress.",
        "⚕️ If stress affects sleep or physical health, consult a GP or counsellor.",
    ],
}

# ---------------------------------------------------------------------
# SCORING ENGINE
# ---------------------------------------------------------------------
def mcq_score(q_id, answer_index, num_options):
    """Return 0-4 normalised score for MCQ questions."""
    if q_id in REVERSE_MCQ:
        # Higher index = worse outcome
        return round((1 - answer_index / (num_options - 1)) * 4, 2)
    else:
        # Higher index = better outcome
        return round((answer_index / (num_options - 1)) * 4, 2)

def compute_scores(answers):
    total_weight = sum(q[3] for q in QUESTIONS)
    weighted_sum = 0
    for q in QUESTIONS:
        raw = answers.get(q[0], 0)
        weighted_sum += raw * q[3]
    overall = round((weighted_sum / (4 * total_weight)) * 100, 1)

    cat_scores = {}
    for cat in CATEGORIES:
        qs = [q for q in QUESTIONS if q[1] == cat]
        w  = sum(q[3] for q in qs)
        s  = sum(answers.get(q[0], 0) * q[3] for q in qs)
        cat_scores[cat] = round((s / (4 * w)) * 100, 1) if w else 0.0
    return overall, cat_scores

def risk_label(score):
    if score >= 75: return "Low Risk",      "#34D399", "Low"
    if score >= 50: return "Moderate Risk", "#FBBF24", "Moderate"
    return                 "High Risk",     "#F87171", "High"

def risk_badge_class(score):
    if score >= 75: return "badge-green"
    if score >= 50: return "badge-amber"
    return "badge-red"

# ---------------------------------------------------------------------
# DATABASE I/O
# ---------------------------------------------------------------------
def save_assessment(user_id, username, score, risk, answers, cat_scores, notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO assessments (user_id,username,score,risk_level,answers,cat_scores,notes) VALUES (?,?,?,?,?,?,?)",
        (user_id, username, score, risk, json.dumps(answers), json.dumps(cat_scores), notes)
    )
    conn.commit()
    conn.close()

def load_user_assessments(username):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id,score,risk_level,cat_scores,notes,created FROM assessments WHERE username=? ORDER BY created DESC",
        (username,)
    ).fetchall()
    conn.close()
    return rows

def load_all_assessments():
    conn = get_conn()
    rows = conn.execute(
        "SELECT a.id,a.username,u.full_name,u.dept,a.score,a.risk_level,a.created "
        "FROM assessments a LEFT JOIN users u ON a.user_id=u.id ORDER BY a.created DESC"
    ).fetchall()
    conn.close()
    return rows

def load_all_users():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id,username,full_name,email,dept,role,created FROM users ORDER BY created DESC"
    ).fetchall()
    conn.close()
    return rows

def get_user_profile(username):
    conn = get_conn()
    row = conn.execute(
        "SELECT age,gender,height_cm,weight_kg,bmi,activity,medical_hist FROM users WHERE username=?",
        (username,)
    ).fetchone()
    conn.close()
    return row

# ---------------------------------------------------------------------
# PDF GENERATOR
# ---------------------------------------------------------------------
def _s(text):
    if not isinstance(text, str): text = str(text)
    return text.encode("ascii", errors="replace").decode("ascii")

def generate_pdf(user, score, risk, cat_scores, notes, timestamp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_fill_color(8, 18, 40)
    pdf.rect(0, 0, 210, 48, "F")
    pdf.set_fill_color(0, 160, 210)
    pdf.rect(0, 44, 210, 3, "F")

    pdf.set_text_color(0, 188, 235)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(15, 10)
    pdf.cell(0, 9, _s("WORKSTATION SAFETY SCORER v4.0"), ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 160, 185)
    pdf.set_x(15)
    pdf.cell(0, 5, _s("ICT in Health & Ergonomics  |  UET Taxila Engineering"), ln=True)
    pdf.set_x(15)
    pdf.cell(0, 5, _s("Report Generated: " + str(timestamp)), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 58)

    def section(title, color=(20, 50, 120)):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_x(15)
        pdf.cell(0, 8, _s("  " + title), ln=True, fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)

    def score_bar(val, r, g, b, x=15, width=180, h=5):
        y = pdf.get_y()
        pdf.set_fill_color(220, 230, 240)
        pdf.rect(x, y, width, h, "F")
        pdf.set_fill_color(r, g, b)
        pdf.rect(x, y, width * val / 100, h, "F")
        pdf.ln(h + 4)

    # Assessment Details
    section("ASSESSMENT DETAILS", (15, 35, 90))
    pdf.set_font("Helvetica", "", 10)
    details = [
        ("Name", user.get("full_name", "")),
        ("Username", user.get("username", "")),
        ("Department", user.get("dept", "")),
        ("Date", str(timestamp)[:10]),
    ]
    if user.get("age"):
        details += [
            ("Age", f"{user.get('age','')} yrs  |  Gender: {user.get('gender','')}"),
            ("Height / Weight", f"{user.get('height_cm','')} cm  |  {user.get('weight_kg','')} kg  |  BMI: {user.get('bmi','')}"),
        ]
    for i in range(0, len(details), 2):
        pdf.set_x(15)
        pdf.cell(90, 6, _s(details[i][0] + ":  " + str(details[i][1])))
        if i+1 < len(details):
            pdf.cell(90, 6, _s(details[i+1][0] + ":  " + str(details[i+1][1])))
        pdf.ln()
    pdf.ln(4)

    # Overall Score
    section("OVERALL ERGONOMIC SCORE", (20, 80, 160))
    r_c, g_c, b_c = (0, 185, 90) if score >= 75 else (210, 140, 0) if score >= 50 else (200, 50, 50)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(r_c, g_c, b_c)
    pdf.set_x(15)
    pdf.cell(0, 14, _s(f"{score}%  —  {risk}"), ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    score_bar(score, r_c, g_c, b_c, width=180, h=8)
    pdf.ln(2)

    # Health Interpretation
    if score >= 75:
        interp = "Your workstation setup is well-optimised. Maintain current habits and review quarterly."
    elif score >= 50:
        interp = "Your setup is adequate but has notable areas for improvement. Address amber categories promptly."
    else:
        interp = "Your workstation poses significant ergonomic risks. Immediate corrective actions are strongly recommended."
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(60, 60, 60)
    pdf.set_x(15)
    pdf.multi_cell(0, 6, _s(interp))
    pdf.ln(4)

    # Category Breakdown
    section("CATEGORY BREAKDOWN", (20, 80, 160))
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(190, 215, 245)
    pdf.set_text_color(20, 40, 100)
    pdf.set_x(15)
    pdf.cell(75, 7, _s("Category"), fill=True)
    pdf.cell(25, 7, _s("Score"), fill=True)
    pdf.cell(50, 7, _s("Risk Level"), fill=True)
    pdf.cell(35, 7, _s("Priority"), fill=True, ln=True)
    pdf.set_text_color(0, 0, 0)
    for idx, (cat, s) in enumerate(sorted(cat_scores.items(), key=lambda x: x[1])):
        rl, _, _ = risk_label(s)
        fill = (idx % 2 == 0)
        priority = "URGENT" if s < 40 else ("HIGH" if s < 60 else ("MEDIUM" if s < 75 else "OK"))
        pdf.set_fill_color(248, 252, 255)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_x(15)
        pdf.cell(75, 6, _s(cat), fill=fill)
        pdf.cell(25, 6, _s(f"{s}%"), fill=fill)
        pdf.cell(50, 6, _s(rl), fill=fill)
        pdf.cell(35, 6, _s(priority), fill=fill, ln=True)
        sc_r, sc_g, sc_b = (0,180,90) if s>=75 else (210,140,0) if s>=50 else (200,50,50)
        score_bar(s, sc_r, sc_g, sc_b, width=155, h=3)
    pdf.ln(4)

    # Recommendations
    section("PERSONALISED RECOMMENDATIONS", (20, 80, 160))
    any_rec = False
    for cat, s in sorted(cat_scores.items(), key=lambda x: x[1]):
        if s < 75:
            any_rec = True
            pdf.set_x(15)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(20, 70, 160)
            pdf.cell(0, 7, _s(f"{cat}  ({s}%)"), ln=True)
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("Helvetica", "", 8)
            for rec in RECOMMENDATIONS.get(cat, [])[:3]:
                pdf.set_x(20)
                pdf.multi_cell(0, 5, _s("• " + rec))
            pdf.ln(2)
    if not any_rec:
        pdf.set_x(15)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 140, 80)
        pdf.cell(0, 7, _s("All categories are in the low-risk zone. Excellent ergonomic awareness!"), ln=True)
        pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # High-Risk Alternatives
    urgent_cats = {c: s for c, s in cat_scores.items() if s < 50}
    if urgent_cats:
        section("IMMEDIATE ACTION ALTERNATIVES (High Risk Areas)", (140, 30, 30))
        for cat, s in sorted(urgent_cats.items(), key=lambda x: x[1]):
            pdf.set_x(15)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(180, 40, 40)
            pdf.cell(0, 7, _s(f"{cat}  ({s}%) — Alternative Solutions:"), ln=True)
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("Helvetica", "", 8)
            for alt in HIGH_RISK_ALTERNATIVES.get(cat, [])[:3]:
                clean_alt = re.sub(r'[^\x00-\x7F]+', '', alt)
                pdf.set_x(20)
                pdf.multi_cell(0, 5, _s(clean_alt))
            pdf.ln(2)

    # Notes
    if notes and notes.strip():
        section("ASSESSOR NOTES", (50, 50, 80))
        pdf.set_font("Helvetica", "", 9)
        pdf.set_x(15)
        pdf.multi_cell(0, 6, _s(notes))

    # Footer
    pdf.set_y(-18)
    pdf.set_draw_color(0, 188, 235)
    pdf.set_line_width(0.4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 130, 145)
    pdf.cell(0, 5,
        _s("Generated by Workstation Safety Scorer v4.0  |  ICT in Health & Ergonomics  |  UET Taxila"),
        align="C"
    )
    return bytes(pdf.output())

# ---------------------------------------------------------------------
# PLOTLY CHARTS
# ---------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#8899AA"),
    margin=dict(l=20, r=20, t=30, b=20),
)

def radar_chart(cat_scores):
    cats  = list(cat_scores.keys())
    vals  = list(cat_scores.values())
    cats_r = cats + cats[:1]
    vals_r = vals + vals[:1]
    fig = go.Figure(go.Scatterpolar(
        r=vals_r, theta=cats_r, fill="toself",
        fillcolor="rgba(56,189,248,0.1)",
        line=dict(color="#38BDF8", width=2.5),
        marker=dict(color="#38BDF8", size=7, line=dict(width=2, color="#FFFFFF")),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=350,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="rgba(56,189,248,0.12)",
                            tickfont=dict(size=9, color="#8899AA")),
            angularaxis=dict(gridcolor="rgba(56,189,248,0.08)",
                             tickfont=dict(size=10)),
        ),
    )
    return fig

def history_chart(rows):
    dates  = [r[5][:10] for r in rows][::-1]
    scores = [r[1]       for r in rows][::-1]
    colors = ["#34D399" if s >= 75 else "#FBBF24" if s >= 50 else "#F87171" for s in scores]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores, mode="lines+markers",
        line=dict(color="#38BDF8", width=2.5, shape="spline"),
        marker=dict(color=colors, size=9, line=dict(width=2, color="#0D1625")),
        fill="tozeroy", fillcolor="rgba(56,189,248,0.06)",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=250,
        xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
        yaxis=dict(range=[0, 105], gridcolor="rgba(255,255,255,0.04)", ticksuffix="%"),
    )
    return fig

def category_bar(cat_scores):
    cats   = list(cat_scores.keys())
    vals   = list(cat_scores.values())
    colors = [CAT_COLORS.get(c, "#38BDF8") for c in cats]
    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker=dict(color=colors, opacity=0.88,
                    line=dict(color="rgba(255,255,255,0.05)", width=1)),
        text=[f"{v}%" for v in vals], textposition="outside",
        textfont=dict(color="#F0F4FF", size=11, family="JetBrains Mono"),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT, height=380,
        xaxis=dict(range=[0, 118], gridcolor="rgba(255,255,255,0.04)", ticksuffix="%"),
        yaxis=dict(autorange="reversed"),
        bargap=0.35,
    )
    return fig

def dept_bar(rows):
    df = pd.DataFrame(rows, columns=["id", "username", "name", "dept", "score", "risk", "created"])
    if df.empty: return None
    avg = df.groupby("dept")["score"].mean().reset_index()
    avg.columns = ["dept", "avg_score"]
    fig = px.bar(avg, x="dept", y="avg_score",
                 color="avg_score",
                 color_continuous_scale=["#F87171", "#FBBF24", "#34D399"],
                 range_color=[0, 100], text_auto=".1f")
    fig.update_traces(textfont_color="#FFFFFF", marker_line_width=0)
    fig.update_layout(**PLOTLY_LAYOUT, height=300, coloraxis_showscale=False,
                      xaxis_title="", yaxis=dict(range=[0, 105], ticksuffix="%"))
    return fig

# ---------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------
defaults = {
    "logged_in": False, "user": None, "page": "dashboard",
    "answers": {}, "assessment_done": False,
    "last_score": None, "last_cat_scores": None, "last_risk": None,
    "show_health_profile": False, "auth_tab": "login",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------------
# LOGIN / REGISTER PAGE
# ---------------------------------------------------------------------
def login_page():
    # Centered layout
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown("""
        <div style='text-align:center;padding:32px 0 20px;'>
            <div style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
                        background:linear-gradient(135deg,#38BDF8,#818CF8);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        text-shadow:none;'>WSS</div>
            <div style='font-family:Syne,sans-serif;font-size:.7rem;letter-spacing:4px;
                        color:#8899AA;margin-top:4px;'>WORKSTATION SAFETY SCORER</div>
            <div style='font-family:DM Sans,sans-serif;font-size:.65rem;letter-spacing:2px;
                        color:#445566;margin-top:4px;'>ICT IN HEALTH & ERGONOMICS | UET TAXILA</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg, tab_reset = st.tabs(["Sign In", "Register", "Reset Password"])

        # ── SIGN IN ──
        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            uname = st.text_input("Username", placeholder="e.g. asnan", key="li_user")
            passw = st.text_input("Password", type="password", placeholder="Enter password", key="li_pass")
            if st.button("SIGN IN", use_container_width=True, key="btn_signin"):
                user = login_user(uname.strip(), passw)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    # Check if health profile is complete
                    if not user.get("age"):
                        st.session_state.show_health_profile = True
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            st.markdown("""
            <div style='margin-top:16px;padding:14px 16px;
                        background:rgba(56,189,248,0.05);
                        border:1px solid rgba(56,189,248,0.15);
                        border-radius:12px;font-family:DM Sans,sans-serif;
                        font-size:.82rem;color:#8899AA;line-height:1.8;'>
                <span style='color:#38BDF8;font-family:Syne,sans-serif;font-weight:700;'>
                Demo Accounts</span><br>
                User &nbsp;: <code style='color:#F0F4FF;'>asnan</code> /
                             <code style='color:#F0F4FF;'>demo123</code><br>
                Admin : <code style='color:#F0F4FF;'>admin</code> /
                        <code style='color:#F0F4FF;'>admin123</code>
            </div>
            """, unsafe_allow_html=True)

        # ── REGISTER ──
        with tab_reg:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            r_name  = st.text_input("Full Name",         key="r_name")
            r_user  = st.text_input("Username",          key="r_user")
            r_email = st.text_input("Email (optional)",  key="r_email")
            r_dept  = st.selectbox("Department",
                ["Engineering", "Computer Science", "Management", "Sciences", "Other"],
                key="r_dept")
            r_pw    = st.text_input("Password",          type="password", key="r_pw")
            r_pw2   = st.text_input("Confirm Password",  type="password", key="r_pw2")

            if st.button("CREATE ACCOUNT", use_container_width=True, key="btn_reg"):
                if not all([r_name, r_user, r_pw]):
                    st.warning("Full name, username and password are required.")
                elif r_pw != r_pw2:
                    st.error("Passwords do not match.")
                elif len(r_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                elif register_user(r_user.strip(), r_pw, r_name.strip(), r_email.strip(), r_dept):
                    st.success("✅ Account created! Please sign in and complete your health profile.")
                    st.session_state["redirect_to_login"] = True
                    st.rerun()
                else:
                    st.error("Username already taken. Please choose another.")

            if st.session_state.get("redirect_to_login"):
                st.session_state["redirect_to_login"] = False
                st.info("👆 Click the **Sign In** tab to log in.")

        # ── RESET PASSWORD ──
        with tab_reset:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class='alert-warn'>
                🔒 Enter your username and set a new password below.
                This is a self-service reset — keep your new password safe.
            </div>
            """, unsafe_allow_html=True)
            rst_user = st.text_input("Username",      key="rst_user")
            rst_new  = st.text_input("New Password",  type="password", key="rst_new")
            rst_new2 = st.text_input("Confirm New Password", type="password", key="rst_new2")
            if st.button("RESET PASSWORD", use_container_width=True, key="btn_reset"):
                if not rst_user or not rst_new:
                    st.warning("All fields are required.")
                elif rst_new != rst_new2:
                    st.error("Passwords do not match.")
                elif len(rst_new) < 6:
                    st.error("Password must be at least 6 characters.")
                elif not username_exists(rst_user.strip()):
                    st.error("Username not found.")
                else:
                    update_password(rst_user.strip(), rst_new)
                    st.success("✅ Password updated! Please sign in with your new password.")

# ---------------------------------------------------------------------
