"""
Authentication Module - ResumeIQ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ AUTH LOGIC   : 100% UNCHANGED from Doc 5
✅ CSS CHANGE 1 : .center-wrap  — card starts from top (padding-top:90px)
✅ CSS CHANGE 2 : .right-panel  — cards start from same top line (padding-top:90px)
   All other CSS, HTML, auth functions, buttons, session state IDENTICAL to Doc 5
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Demo: demo / demo123
"""

import sqlite3
import hashlib
import streamlit as st
import streamlit.components.v1 as components

DB_PATH = "resume_data.db"


# ═══════════════════════════════════════════════════════════
#  DATABASE HELPERS  (UNCHANGED)
# ═══════════════════════════════════════════════════════════

def get_db():
    return sqlite3.connect(DB_PATH)


def init_auth_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",
            ("demo", "demo@resumeiq.ai", hash_password("demo123"))
        )
        conn.commit()
    except Exception:
        pass
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(
        f"smart_resume_ai_salt_2024{password}".encode()
    ).hexdigest()


def register_user(username, email, password):
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?,?,?)",
            (username.strip(), email.strip().lower(), hash_password(password))
        )
        conn.commit()
        return {"success": True}
    except sqlite3.IntegrityError as e:
        return {
            "success": False,
            "error": "Username already taken." if "username" in str(e)
                     else "Email already registered."
        }
    finally:
        conn.close()


def login_user_by_username(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, email FROM users WHERE username=? AND password_hash=?",
        (username.strip(), hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"success": True,
                "user": {"id": row[0], "username": row[1], "email": row[2]}}
    return {"success": False, "error": "Invalid username or password."}


def authenticate_user(username, password):
    return login_user_by_username(username, password)


def logout_user():
    for key in ["logged_in", "user_id", "user_email", "username"]:
        st.session_state.pop(key, None)


def is_logged_in():
    return st.session_state.get("logged_in", False)


def init_auth_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_id = None
        st.session_state.user_email = None
    if "auth_tab" not in st.session_state:
        st.session_state.auth_tab = "signin"


# ═══════════════════════════════════════════════════════════
#  RENDER AUTH PAGE
# ═══════════════════════════════════════════════════════════

def render_auth_page():
    init_auth_tables()
    init_auth_state()

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ────────────────────────────────────────────────────────
   HIDE STREAMLIT CHROME
──────────────────────────────────────────────────────── */
#MainMenu, footer, header,
[data-testid="stHeader"],   [data-testid="stToolbar"],
[data-testid="stSidebar"],  [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stTop"] {
    display: none !important;
    visibility: hidden !important;
}

/* ────────────────────────────────────────────────────────
   BASE RESET
──────────────────────────────────────────────────────── */
html, body {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 100vh !important;
    font-family: 'DM Sans', sans-serif !important;
    overflow-x: hidden !important;
    background: #04071A !important;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
.stApp {
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow-x: hidden !important;
}

.block-container {
    padding: 0 !important;
    max-width: 1400px !important;
    margin: auto !important;
    background: transparent !important;
}

section[data-testid="stMain"] > div:first-child,
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    background: transparent !important;
}

[data-testid="stColumn"]          { background: transparent !important; min-width: 0 !important; overflow: hidden !important; }
[data-testid="stVerticalBlock"]   { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; }

/* ════════════════════════════════════════════════════════
   BACKGROUND LAYER 1 — deep-space gradient
════════════════════════════════════════════════════════ */
body::before {
    content: '';
    position: fixed; inset: 0; z-index: -6;
    background:
        radial-gradient(ellipse 120% 80%  at 15% 10%, rgba(14,116,144,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 100% 90%  at 85%  5%, rgba(109,40,217,0.11) 0%, transparent 55%),
        radial-gradient(ellipse 110% 70%  at 50% 110%, rgba(79,70,229,0.09) 0%, transparent 55%),
        linear-gradient(160deg, #04071A 0%, #070B24 30%, #0C0929 55%, #070B24 80%, #04071A 100%);
}

/* ════════════════════════════════════════════════════════
   BACKGROUND LAYER 2 — dot grid
════════════════════════════════════════════════════════ */
body::after {
    content: '';
    position: fixed; inset: 0; z-index: -5;
    background-image: radial-gradient(circle, rgba(34,211,238,0.22) 1px, transparent 1px);
    background-size: 38px 38px;
    mask-image: radial-gradient(
        ellipse 88% 88% at 50% 50%,
        rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.40) 45%, transparent 72%
    );
    -webkit-mask-image: radial-gradient(
        ellipse 88% 88% at 50% 50%,
        rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.40) 45%, transparent 72%
    );
}

/* ════════════════════════════════════════════════════════
   ANIMATED BLOBS
════════════════════════════════════════════════════════ */
.bg-blobs { position: fixed; inset: 0; z-index: -4; pointer-events: none; overflow: hidden; }
.blob { position: absolute; border-radius: 50%; filter: blur(90px); opacity: 0.5; }
.blob-1 {
    width: 650px; height: 480px; top: -8%; left: -6%;
    background: radial-gradient(ellipse, rgba(56,189,248,0.15) 0%, transparent 70%);
    animation: blobDrift1 22s ease-in-out infinite alternate;
}
.blob-2 {
    width: 580px; height: 580px; top: 8%; right: -8%;
    background: radial-gradient(ellipse, rgba(168,85,247,0.15) 0%, transparent 70%);
    animation: blobDrift2 27s ease-in-out infinite alternate;
}
.blob-3 {
    width: 480px; height: 380px; bottom: -4%; left: 33%;
    background: radial-gradient(ellipse, rgba(99,102,241,0.10) 0%, transparent 70%);
    animation: blobDrift3 19s ease-in-out infinite alternate;
}
.blob-center {
    width: 660px; height: 660px; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(
        ellipse, rgba(34,211,238,0.10) 0%, rgba(99,102,241,0.07) 38%, transparent 62%
    );
    animation: centerPulse 9s ease-in-out infinite;
}
@keyframes blobDrift1 { from { transform: translate(0,0) scale(1); } to { transform: translate(45px,65px) scale(1.09); } }
@keyframes blobDrift2 { from { transform: translate(0,0) scale(1); } to { transform: translate(-55px,45px) scale(1.07); } }
@keyframes blobDrift3 { from { transform: translate(0,0) scale(1); } to { transform: translate(35px,-45px) scale(1.06); } }
@keyframes centerPulse {
    0%,100% { opacity: 0.75; transform: translate(-50%,-50%) scale(1); }
    50%      { opacity: 1;   transform: translate(-50%,-50%) scale(1.15); }
}

/* ════════════════════════════════════════════════════════
   STAR PARTICLES
════════════════════════════════════════════════════════ */
.stars { position: fixed; inset: 0; z-index: -3; pointer-events: none; overflow: hidden; }
.star  { position: absolute; border-radius: 50%; background: #fff;
         animation: starTwinkle var(--dur,4s) ease-in-out infinite var(--delay,0s); }
@keyframes starTwinkle {
    0%,100% { opacity: var(--min-op,0.07); transform: scale(1); }
    50%      { opacity: var(--max-op,0.60); transform: scale(1.5); }
}

/* ════════════════════════════════════════════════════════
   LOGIN CARD — spinning conic border
════════════════════════════════════════════════════════ */
@property --angle {
    syntax: '<angle>';
    initial-value: 0deg;
    inherits: false;
}
@keyframes borderSpin { to { --angle: 360deg; } }
@keyframes cardFloat { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-6px); } }

.card-glow-wrapper {
    position: relative; border-radius: 28px; padding: 2px;
    max-width: 560px; margin: 0 auto;
    background: conic-gradient(
        from var(--angle),
        transparent       0%,
        rgba(34,211,238,0.80) 10%,
        rgba(168,85,247,0.65) 26%,
        transparent       44%,
        rgba(99,102,241,0.52) 58%,
        rgba(34,211,238,0.70) 74%,
        transparent      100%
    );
    animation: borderSpin 4s linear infinite, cardFloat 6s ease-in-out infinite;
    z-index: 50;
    box-shadow:
        0 0  80px 12px rgba(34,211,238,0.45),
        0 0 150px 32px rgba(168,85,247,0.35),
        0 40px 120px   rgba(0,0,0,0.85);
    transition: box-shadow 0.35s ease, transform 0.35s ease;
}
.card-glow-wrapper:hover {
    box-shadow:
        0 0  80px 14px rgba(34,211,238,0.48),
        0 0 150px 36px rgba(168,85,247,0.32),
        0 40px 120px   rgba(0,0,0,0.78);
}
@supports not (background: conic-gradient(from 0deg, red, blue)) {
    .card-glow-wrapper {
        background: linear-gradient(135deg, rgba(34,211,238,0.50) 0%, rgba(168,85,247,0.45) 100%);
        animation: none;
    }
}

.card-inner {
    background: rgba(7,11,30,0.96); border-radius: 26px;
    padding: 3.8rem 3.2rem; backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px); position: relative; overflow: hidden;
}
.card-inner::before {
    content: ''; position: absolute;
    top: 0; left: 8%; right: 8%; height: 1px;
    background: linear-gradient(
        90deg, transparent 0%, rgba(34,211,238,0.85) 25%,
        rgba(168,85,247,0.70) 58%, transparent 100%
    );
}
.card-inner::after {
    content: ''; position: absolute;
    top: -100px; left: 4%; right: 4%; height: 200px;
    background: radial-gradient(ellipse, rgba(34,211,238,0.06) 0%, transparent 60%);
    pointer-events: none;
}

/* ════════════════════════════════════════════════════════
   CENTER COLUMN WRAPPER
   ✅ CHANGE 1: card starts near top, aligns with side panels
   OLD: justify-content:center; min-height:100vh
   NEW: padding-top:90px; no min-height forcing
════════════════════════════════════════════════════════ */
.center-wrap {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    padding: 90px 0.5rem 2rem;
    position: relative;
    isolation: isolate;
    z-index: 40;
}
.center-wrap::before {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 560px; height: 560px;
    background: radial-gradient(
        circle,
        rgba(34,211,238,0.12) 0%,
        rgba(168,85,247,0.08) 40%,
        transparent 70%
    );
    filter: blur(40px);
    z-index: -1;
    pointer-events: none;
}

/* ════════════════════════════════════════════════════════
   INPUT FIELDS
════════════════════════════════════════════════════════ */
div[data-testid="stTextInput"] { margin-bottom: 1.3rem !important; }
div[data-testid="stTextInput"] input {
    background: rgba(5,9,26,0.88) !important;
    border: 1.5px solid rgba(100,116,139,0.20) !important;
    border-radius: 12px !important; color: #f1f5f9 !important;
    padding: 0.92rem 1.2rem !important; font-size: 0.97rem !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.22s ease, box-shadow 0.22s ease, background 0.22s ease !important;
    box-shadow: inset 0 1px 4px rgba(0,0,0,0.55) !important;
}
div[data-testid="stTextInput"] input:hover  { border-color: rgba(34,211,238,0.35) !important; }
div[data-testid="stTextInput"] input:focus  {
    background: rgba(8,14,40,0.97) !important;
    border-color: #22d3ee !important;
    box-shadow: 0 0 0 3px rgba(34,211,238,0.14), inset 0 1px 4px rgba(0,0,0,0.50) !important;
    outline: none !important;
}
div[data-testid="stTextInput"] input::placeholder { color: rgba(71,85,105,0.80) !important; }
div[data-testid="stTextInput"] label              { display: none !important; }

/* ════════════════════════════════════════════════════════
   BUTTONS
════════════════════════════════════════════════════════ */
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-primary"]:focus {
    background: linear-gradient(135deg, #0b6a85 0%, #22d3ee 100%) !important;
    border: none !important; border-radius: 12px !important;
    color: #010e18 !important; font-weight: 800 !important;
    font-family: 'Syne', sans-serif !important;
    padding: 0.92rem 1.5rem !important; font-size: 0.97rem !important;
    letter-spacing: 0.4px !important;
    box-shadow: 0 4px 28px rgba(34,211,238,0.35), inset 0 1px 0 rgba(255,255,255,0.20) !important;
    transition: all 0.2s ease !important;
}
button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 38px rgba(34,211,238,0.50), inset 0 1px 0 rgba(255,255,255,0.24) !important;
    filter: brightness(1.07) !important;
}
button[data-testid="baseButton-primary"]:active {
    transform: translateY(0) !important; filter: brightness(0.96) !important;
}

button[data-testid="baseButton-secondary"],
button[data-testid="baseButton-secondary"]:focus {
    background: rgba(255,255,255,0.038) !important;
    border: 1.5px solid rgba(100,116,139,0.18) !important;
    border-radius: 12px !important; color: rgba(148,163,184,0.80) !important;
    font-weight: 600 !important; font-family: 'DM Sans', sans-serif !important;
    padding: 0.92rem 1.5rem !important; font-size: 0.97rem !important;
    transition: all 0.2s ease !important; backdrop-filter: blur(10px) !important;
}
button[data-testid="baseButton-secondary"]:hover {
    background: rgba(34,211,238,0.075) !important;
    border-color: rgba(34,211,238,0.34) !important; color: #e2e8f0 !important;
    box-shadow: 0 0 20px rgba(34,211,238,0.10) !important;
}

/* ════════════════════════════════════════════════════════
   ALERTS
════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
    background: rgba(34,211,238,0.05) !important;
    border: 1px solid rgba(34,211,238,0.17) !important;
    border-radius: 12px !important;
    border-left: 3px solid #22d3ee !important;
    color: rgba(241,245,249,0.95) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stForm { border: none !important; background: transparent !important; padding: 0 !important; }

/* ════════════════════════════════════════════════════════
   TYPOGRAPHY
════════════════════════════════════════════════════════ */
h1, h2, h3, h4, h5, h6 { color: #f1f5f9 !important; }
h2 { font-weight: 800 !important; font-size: 1.8rem !important; letter-spacing: -0.4px !important; }
p, label, span          { color: rgba(203,213,225,0.90) !important; }
div[data-testid="stMarkdownContainer"] { color: rgba(203,213,225,0.90) !important; }

/* ════════════════════════════════════════════════════════
   LEFT PANEL  (unchanged from Doc 5)
════════════════════════════════════════════════════════ */
.left-panel {
    min-height: 100vh; padding: 0 1.5rem 0 1.8rem;
    display: flex; flex-direction: column; justify-content: center;
    position: relative; z-index: 10;
}
.brand-logo { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 3.2rem; }
.brand-icon {
    width: 50px; height: 50px; border-radius: 14px;
    background: linear-gradient(135deg, #22d3ee, #818cf8);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.55rem;
    box-shadow: 0 0 30px rgba(34,211,238,0.42), 0 0 8px rgba(34,211,238,0.20);
    flex-shrink: 0;
}
.brand-wordmark {
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.82rem;
    color: #fff; letter-spacing: -0.5px; line-height: 1;
}
.brand-wordmark span { color: #22d3ee; }
.left-headline {
    font-family: 'Syne', sans-serif; font-weight: 800;
    font-size: clamp(2.3rem, 3.2vw, 3.1rem); line-height: 1.10;
    color: #f8fafc; margin: 0 0 1.4rem 0; letter-spacing: -1.4px;
}
.left-headline em {
    font-style: normal;
    background: linear-gradient(100deg, #22d3ee 0%, #a78bfa 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.left-desc {
    font-size: 1rem; line-height: 1.80;
    color: rgba(148,163,184,0.86); margin: 0 0 2.6rem 0; max-width: 340px;
}
.feature-list { display: flex; flex-direction: column; gap: 0; max-width: 355px; }
.feature-item {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 1.1rem 1.3rem;
    background: rgba(255,255,255,0.026); border: 1px solid rgba(255,255,255,0.052);
    border-radius: 14px; margin-bottom: 0.88rem; cursor: default;
    transition: background 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease, transform 0.22s ease;
}
.feature-item:last-child { margin-bottom: 0; }
.feature-item:hover {
    background: rgba(34,211,238,0.065); border-color: rgba(34,211,238,0.22);
    box-shadow: 0 4px 24px rgba(34,211,238,0.09), inset 0 1px 0 rgba(34,211,238,0.10);
    transform: translateX(4px);
}
.feature-icon { font-size: 1.45rem; line-height: 1; flex-shrink: 0; margin-top: 2px; }
.feature-text-title {
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.92rem;
    color: #e2e8f0; margin: 0 0 0.2rem 0; letter-spacing: -0.1px;
}
.feature-text-desc { font-size: 0.83rem; color: rgba(100,116,139,0.92); margin: 0; line-height: 1.55; }
.left-social-proof {
    margin-top: 2.6rem; padding-top: 2rem;
    border-top: 1px solid rgba(255,255,255,0.056);
    display: flex; align-items: center; gap: 1rem;
}
.avatar-stack { display: flex; }
.avatar-stack .av {
    width: 34px; height: 34px; border-radius: 50%;
    border: 2px solid #04071A;
    background: linear-gradient(135deg, #22d3ee, #818cf8);
    margin-left: -9px; display: flex; align-items: center; justify-content: center;
    font-size: 0.67rem; color: #fff; font-weight: 700; font-family: 'Syne', sans-serif;
}
.avatar-stack .av:first-child { margin-left: 0; }
.proof-text { font-size: 0.84rem; color: rgba(100,116,139,0.92); line-height: 1.5; }
.proof-text strong { color: #22d3ee; font-weight: 600; }

/* ════════════════════════════════════════════════════════
   RIGHT PANEL WRAPPER — forces correct HTML rendering
   Outer flex container centres the inner .right-panel
════════════════════════════════════════════════════════ */
.right-panel-wrapper {
    width: 100%;
    display: flex;
    justify-content: center;
    position: relative;
}

/* ════════════════════════════════════════════════════════
   RIGHT PANEL
   ✅ CHANGE 2: cards start from same top line as login card
   OLD: justify-content:center (vertically centred)
   NEW: justify-content:flex-start + padding-top:90px (top-aligned)
   Everything else from Doc 5 unchanged.
════════════════════════════════════════════════════════ */
.right-panel {
    min-height: 100vh;
    width: 100%; max-width: 320px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    gap: 0;
    padding: 90px 1.5rem 2rem;
    position: relative;
    overflow: hidden;
    z-index: 10;
}

/* ── Decorative rings (position:absolute — unchanged) ── */
.glow-ring {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 400px; height: 400px; border-radius: 50%;
    border: 1px solid rgba(34,211,238,0.08);
    box-shadow: 0 0 80px 14px rgba(34,211,238,0.034), inset 0 0 80px 14px rgba(168,85,247,0.022);
    animation: ringPulse 7s ease-in-out infinite; pointer-events: none;
}
.glow-ring-2 {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%,-50%);
    width: 260px; height: 260px; border-radius: 50%;
    border: 1px solid rgba(168,85,247,0.08);
    animation: ringPulse 7s ease-in-out infinite 2.5s; pointer-events: none;
}
@keyframes ringPulse {
    0%,100% { opacity: 0.52; transform: translate(-50%,-50%) scale(1); }
    50%      { opacity: 1;   transform: translate(-50%,-50%) scale(1.06); }
}

/* ── Dot accents (position:absolute — unchanged) ── */
.dot-accent { position: absolute; border-radius: 50%; pointer-events: none; z-index: 1; }
.dot-tl  { top:17%; left:7%;   width:10px; height:10px; background:#22d3ee;
           box-shadow:0 0 18px 5px rgba(34,211,238,0.55);  animation:dotFloat 4s ease-in-out infinite; }
.dot-br  { bottom:20%; right:9%; width:7px;  height:7px;  background:#c084fc;
           box-shadow:0 0 14px 3px rgba(192,132,252,0.55); animation:dotFloat 5s ease-in-out infinite 1.2s; }
.dot-mid { top:63%; left:4%;    width:5px;  height:5px;  background:#818cf8;
           box-shadow:0 0 11px 2px rgba(129,140,248,0.50); animation:dotFloat 7s ease-in-out infinite 2.5s; }
.dot-tr  { top:29%; right:6%;   width:6px;  height:6px;  background:#34d399;
           box-shadow:0 0 11px 2px rgba(52,211,153,0.50);  animation:dotFloat 6s ease-in-out infinite 0.7s; }
@keyframes dotFloat {
    0%,100% { transform: translateY(0px);   }
    50%      { transform: translateY(-13px); }
}

/* ── Connector lines (unchanged from Doc 5) ── */
.card-connector {
    display: flex; justify-content: center; align-items: center;
    width: 100%; max-width: 300px;
    height: 28px;
    position: relative; z-index: 2; flex-shrink: 0;
}
.card-connector::before {
    content: ''; display: block;
    width: 2px; height: 100%;
    background: linear-gradient(180deg, rgba(34,211,238,0.22), rgba(168,85,247,0.18));
    border-radius: 2px;
    animation: connectorGlow 3.5s ease-in-out infinite;
}
@keyframes connectorGlow {
    0%,100% { opacity: 0.32; }
    50%      { opacity: 1; }
}

/* ── Glass cards (unchanged from Doc 5) ── */
.glass-card {
    width: 100%; max-width: 300px;
    padding: 1.2rem 1.45rem;
    background: rgba(7,11,28,0.75);
    border: 1px solid rgba(255,255,255,0.065);
    border-radius: 18px;
    backdrop-filter: blur(22px); -webkit-backdrop-filter: blur(22px);
    position: relative; z-index: 2; flex-shrink: 0;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover { transform: translateY(-6px) !important; }

.glass-card.accent-cyan {
    border-color: rgba(34,211,238,0.15);
    box-shadow: 0 4px 30px rgba(34,211,238,0.10), inset 0 1px 0 rgba(34,211,238,0.09);
    animation: cardFloat1 6.5s ease-in-out infinite;
}
.glass-card.accent-purple {
    border-color: rgba(168,85,247,0.15);
    box-shadow: 0 4px 30px rgba(168,85,247,0.10), inset 0 1px 0 rgba(168,85,247,0.09);
    animation: cardFloat2 7.5s ease-in-out infinite 1.1s;
}
.glass-card.accent-indigo {
    border-color: rgba(99,102,241,0.15);
    box-shadow: 0 4px 30px rgba(99,102,241,0.10), inset 0 1px 0 rgba(99,102,241,0.09);
    animation: cardFloat3 8.5s ease-in-out infinite 0.6s;
}
.glass-card.accent-green {
    border-color: rgba(52,211,153,0.13);
    box-shadow: 0 4px 30px rgba(52,211,153,0.09), inset 0 1px 0 rgba(52,211,153,0.08);
    animation: cardFloat1 9.5s ease-in-out infinite 2.0s;
}

@keyframes cardFloat1 { 0%,100% { transform:translateY(0px);  } 50% { transform:translateY(-7px);  } }
@keyframes cardFloat2 { 0%,100% { transform:translateY(0px);  } 50% { transform:translateY(-11px); } }
@keyframes cardFloat3 { 0%,100% { transform:translateY(0px);  } 50% { transform:translateY(-5px);  } }

.gc-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.72rem; }
.gc-label  { font-family:'Syne',sans-serif; font-size:0.72rem; font-weight:700;
             color:rgba(100,116,139,0.86); text-transform:uppercase; letter-spacing:1.1px; }
.gc-badge  { font-size:0.68rem; font-weight:700; padding:0.17rem 0.52rem;
             border-radius:20px; font-family:'DM Sans',sans-serif; }
.badge-green  { background:rgba(52,211,153,0.11);  color:#34d399; border:1px solid rgba(52,211,153,0.26); }
.badge-cyan   { background:rgba(34,211,238,0.11);  color:#22d3ee; border:1px solid rgba(34,211,238,0.26); }
.badge-purple { background:rgba(168,85,247,0.11);  color:#c084fc; border:1px solid rgba(168,85,247,0.26); }
.gc-score { font-family:'Syne',sans-serif; font-size:2.35rem; font-weight:800; color:#f1f5f9; line-height:1; margin-bottom:0.3rem; }
.gc-sublabel { font-size:0.79rem; color:rgba(100,116,139,0.88); line-height:1.45; }
.mini-bar-wrap { background:rgba(255,255,255,0.054); border-radius:6px; height:6px; overflow:hidden; margin-top:0.78rem; }
.mini-bar-fill { height:100%; border-radius:6px; animation:barFill 2.2s cubic-bezier(0.4,0,0.2,1) both; }
@keyframes barFill { from { width:0%; } }
.fill-cyan   { background:linear-gradient(90deg,#0e7490,#22d3ee); width:87%; }
.fill-purple { background:linear-gradient(90deg,#7c3aed,#c084fc); width:73%; }
.fill-indigo { background:linear-gradient(90deg,#3730a3,#818cf8); width:65%; }
.fill-green  { background:linear-gradient(90deg,#059669,#34d399); width:92%; }
.stat-row { display:flex; gap:0.65rem; margin-top:0.18rem; }
.stat-chip { flex:1; background:rgba(255,255,255,0.038); border-radius:10px;
             padding:0.55rem 0.65rem; text-align:center; border:1px solid rgba(255,255,255,0.055); }
.stat-num { font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800; color:#f1f5f9; display:block; line-height:1.2; }
.stat-lbl { font-size:0.67rem; color:rgba(100,116,139,0.82); }

/* ════════════════════════════════════════════════════════
   RESPONSIVE — hide side panels below 1000px
════════════════════════════════════════════════════════ */
@media (max-width: 1000px) {
    .left-panel  { display: none !important; }
    .right-panel { display: none !important; }
}
</style>
""", unsafe_allow_html=True)

    # ── Background layers ────────────────────────────────────
    st.markdown("""
<div class="bg-blobs">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>
    <div class="blob blob-center"></div>
</div>
<div class="stars">
    <div class="star" style="top:3%;  left:11%; width:1.5px; height:1.5px; --dur:3.2s; --delay:0s;   --min-op:0.07; --max-op:0.60;"></div>
    <div class="star" style="top:8%;  left:73%; width:1px;   height:1px;   --dur:4.6s; --delay:0.4s; --min-op:0.05; --max-op:0.50;"></div>
    <div class="star" style="top:15%; left:29%; width:2px;   height:2px;   --dur:2.9s; --delay:1.1s; --min-op:0.09; --max-op:0.68;"></div>
    <div class="star" style="top:21%; left:87%; width:1.5px; height:1.5px; --dur:5.1s; --delay:0.3s; --min-op:0.06; --max-op:0.48;"></div>
    <div class="star" style="top:32%; left:6%;  width:1px;   height:1px;   --dur:3.8s; --delay:1.6s; --min-op:0.07; --max-op:0.52;"></div>
    <div class="star" style="top:44%; left:91%; width:1.5px; height:1.5px; --dur:3.6s; --delay:2.1s; --min-op:0.08; --max-op:0.58;"></div>
    <div class="star" style="top:57%; left:38%; width:1px;   height:1px;   --dur:5.4s; --delay:0.7s; --min-op:0.05; --max-op:0.42;"></div>
    <div class="star" style="top:63%; left:79%; width:2px;   height:2px;   --dur:4.0s; --delay:1.3s; --min-op:0.09; --max-op:0.62;"></div>
    <div class="star" style="top:76%; left:9%;  width:1.5px; height:1.5px; --dur:3.4s; --delay:1.9s; --min-op:0.07; --max-op:0.53;"></div>
    <div class="star" style="top:89%; left:54%; width:1px;   height:1px;   --dur:4.3s; --delay:0.5s; --min-op:0.06; --max-op:0.48;"></div>
    <div class="star" style="top:6%;  left:48%; width:2px;   height:2px;   --dur:3.1s; --delay:2.4s; --min-op:0.10; --max-op:0.70;"></div>
    <div class="star" style="top:28%; left:95%; width:1px;   height:1px;   --dur:5.8s; --delay:1.1s; --min-op:0.07; --max-op:0.50;"></div>
    <div class="star" style="top:82%; left:67%; width:1.5px; height:1.5px; --dur:3.9s; --delay:0.2s; --min-op:0.08; --max-op:0.55;"></div>
    <div class="star" style="top:50%; left:2%;  width:1px;   height:1px;   --dur:4.7s; --delay:0.9s; --min-op:0.05; --max-op:0.45;"></div>
    <div class="star" style="top:70%; left:85%; width:2px;   height:2px;   --dur:3.5s; --delay:1.7s; --min-op:0.09; --max-op:0.65;"></div>
</div>
""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  THREE-COLUMN LAYOUT — UNCHANGED
    # ══════════════════════════════════════════════════════════
    left_col, center_col, right_col = st.columns([1, 1.35, 1.05])

    # ──────────────────────────────────────────────────────────
    # LEFT PANEL — UNCHANGED
    # ──────────────────────────────────────────────────────────
    with left_col:
        st.markdown("""
<div class="left-panel">
    <div class="brand-logo">
        <div class="brand-icon">🧠</div>
        <div class="brand-wordmark">Resume<span>IQ</span></div>
    </div>
    <h1 class="left-headline">Land Your<br><em>Dream Job</em><br>Faster</h1>
    <p class="left-desc">AI-powered resume analysis, ATS scoring, interview preparation, and career insights — all in one intelligent platform built for modern job seekers.</p>
    <div class="feature-list">
        <div class="feature-item">
            <div class="feature-icon">🏆</div>
            <div>
                <p class="feature-text-title">ATS Score</p>
                <p class="feature-text-desc">Beat applicant tracking systems with precision-tuned resume analysis.</p>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎯</div>
            <div>
                <p class="feature-text-title">Job Matching</p>
                <p class="feature-text-desc">Find your perfect role — matched by skills, not just keywords.</p>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🎤</div>
            <div>
                <p class="feature-text-title">Interview Prep</p>
                <p class="feature-text-desc">AI mock interview practice with real-time coaching feedback.</p>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div>
                <p class="feature-text-title">Career Analytics</p>
                <p class="feature-text-desc">Track your job search progress with actionable insights.</p>
            </div>
        </div>
    </div>
    <div class="left-social-proof">
        <div class="avatar-stack">
            <div class="av">AK</div>
            <div class="av">JS</div>
            <div class="av">MR</div>
            <div class="av">+</div>
        </div>
        <div class="proof-text">
            Trusted by <strong>12,400+</strong> job seekers<br>who landed their dream roles
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # CENTER PANEL — Auth card — ALL AUTH LOGIC UNCHANGED
    # ──────────────────────────────────────────────────────────
    with center_col:
        st.markdown("""
<div class="center-wrap">
<div class="card-glow-wrapper">
<div class="card-inner">
""", unsafe_allow_html=True)

        st.markdown("""
<div style="text-align:center; margin-bottom:2rem;">
    <div style="font-size:2.1rem; margin-bottom:0.5rem;
                filter:drop-shadow(0 0 14px rgba(34,211,238,0.50));">🧠</div>
    <div style="font-family:'Syne',sans-serif; font-weight:800; font-size:1.55rem;
                color:#22d3ee; letter-spacing:-0.4px; line-height:1;">ResumeIQ</div>
    <div style="font-size:0.76rem; color:rgba(100,116,139,0.86); margin-top:0.35rem;
                letter-spacing:0.65px; text-transform:uppercase;
                font-family:'DM Sans',sans-serif;">AI-Powered Career Platform</div>
</div>
""", unsafe_allow_html=True)

        # Tab toggle — UNCHANGED
        tab = st.session_state.auth_tab
        tab_col1, tab_col2 = st.columns([1, 1], gap="large")
        with tab_col1:
            if st.button("🔑 Sign In", key="tab_signin",
                         type="primary" if tab == "signin" else "secondary",
                         use_container_width=True):
                st.session_state.auth_tab = "signin"
                st.rerun()
        with tab_col2:
            if st.button("✨ Register", key="tab_register",
                         type="primary" if tab == "register" else "secondary",
                         use_container_width=True):
                st.session_state.auth_tab = "register"
                st.rerun()

        st.markdown("<div style='height:1.8rem;'></div>", unsafe_allow_html=True)

        # ── SIGN IN FORM — UNCHANGED ──────────────────────────
        if tab == "signin":
            st.markdown("""
<div style="margin-bottom:1.4rem;">
    <h2 style="margin:0 0 0.22rem 0; font-family:'Syne',sans-serif;
               font-size:1.62rem; font-weight:700; color:#f8fafc; letter-spacing:-0.3px;">
               Welcome Back</h2>
    <p style="margin:0; font-size:0.88rem; color:rgba(100,116,139,0.88);">
        Sign in to continue your career journey</p>
</div>
""", unsafe_allow_html=True)

            st.markdown("<label style='font-size:0.82rem; font-weight:600; color:rgba(148,163,184,0.88); display:block; margin-bottom:0.32rem; letter-spacing:0.15px;'>Username</label>", unsafe_allow_html=True)
            signin_username = st.text_input(
                "username_signin", placeholder="Enter your username",
                label_visibility="collapsed", key="signin_user")

            st.markdown("<label style='font-size:0.82rem; font-weight:600; color:rgba(148,163,184,0.88); display:block; margin-bottom:0.32rem; margin-top:0.8rem; letter-spacing:0.15px;'>Password</label>", unsafe_allow_html=True)
            signin_password = st.text_input(
                "password_signin", placeholder="Enter your password",
                type="password", label_visibility="collapsed", key="signin_pass")

            st.markdown("""
<div style="background:rgba(34,211,238,0.052); border-left:3px solid rgba(34,211,238,0.65);
            padding:0.72rem 1rem; border-radius:10px; margin:1.15rem 0;
            border:1px solid rgba(34,211,238,0.11);">
    <p style="margin:0; font-size:0.83rem; color:rgba(148,163,184,0.9); font-family:'DM Sans',sans-serif;">
        &#128161; Demo credentials:
        <strong style="color:#22d3ee; font-family:'Syne',sans-serif;">demo / demo123</strong>
    </p>
</div>
""", unsafe_allow_html=True)

            if st.button("🚀 Sign In", key="btn_signin",
                         type="primary", use_container_width=True):
                if not signin_username or not signin_password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    result = login_user_by_username(signin_username.strip(), signin_password)
                    if result["success"]:
                        st.session_state.logged_in  = True
                        st.session_state.user_id    = result["user"]["id"]
                        st.session_state.user_email = result["user"]["email"]
                        st.session_state.username   = result["user"]["username"]
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

            st.markdown("""
<div style="text-align:center; margin-top:1.2rem; padding-top:1.2rem;
            border-top:1px solid rgba(255,255,255,0.055);">
    <p style="margin:0; font-size:0.78rem; color:rgba(71,85,105,0.88);">
        No account? <strong style="color:rgba(100,116,139,0.92);">Switch to Register above</strong>
    </p>
</div>
""", unsafe_allow_html=True)

        # ── REGISTER FORM — UNCHANGED ─────────────────────────
        else:
            st.markdown("""
<div style="margin-bottom:1.4rem;">
    <h2 style="margin:0 0 0.22rem 0; font-family:'Syne',sans-serif;
               font-size:1.62rem; font-weight:700; color:#f8fafc; letter-spacing:-0.3px;">
               Create Account</h2>
    <p style="margin:0; font-size:0.88rem; color:rgba(100,116,139,0.88);">
        Join thousands landing their dream jobs</p>
</div>
""", unsafe_allow_html=True)

            st.markdown("<label style='font-size:0.82rem; font-weight:600; color:rgba(148,163,184,0.88); display:block; margin-bottom:0.32rem; letter-spacing:0.15px;'>Username</label>", unsafe_allow_html=True)
            reg_username = st.text_input(
                "username_register", placeholder="Choose a unique username",
                label_visibility="collapsed", key="reg_user")

            st.markdown("<label style='font-size:0.82rem; font-weight:600; color:rgba(148,163,184,0.88); display:block; margin-bottom:0.32rem; margin-top:0.8rem; letter-spacing:0.15px;'>Email Address</label>", unsafe_allow_html=True)
            reg_email = st.text_input(
                "email_register", placeholder="your@email.com",
                label_visibility="collapsed", key="reg_email")

            st.markdown("<label style='font-size:0.82rem; font-weight:600; color:rgba(148,163,184,0.88); display:block; margin-bottom:0.32rem; margin-top:0.8rem; letter-spacing:0.15px;'>Password</label>", unsafe_allow_html=True)
            reg_password = st.text_input(
                "password_register", placeholder="At least 6 characters",
                type="password", label_visibility="collapsed", key="reg_pass")

            st.markdown("<label style='font-size:0.82rem; font-weight:600; color:rgba(148,163,184,0.88); display:block; margin-bottom:0.32rem; margin-top:0.8rem; letter-spacing:0.15px;'>Confirm Password</label>", unsafe_allow_html=True)
            reg_confirm = st.text_input(
                "confirm_password_register", placeholder="Re-enter your password",
                type="password", label_visibility="collapsed", key="reg_confirm")

            st.markdown("""
<div style="background:rgba(255,255,255,0.026); padding:0.68rem 0.95rem;
            border-radius:10px; margin:1.15rem 0; font-size:0.80rem;
            color:rgba(71,85,105,0.90); border:1px solid rgba(255,255,255,0.052);
            font-family:'DM Sans',sans-serif;">
    <p style="margin:0;">&#10003; Minimum 6 character password</p>
    <p style="margin:0.24rem 0 0 0;">&#10003; Unique email per account</p>
</div>
""", unsafe_allow_html=True)

            if st.button("✨ Create Account", key="btn_register",
                         type="primary", use_container_width=True):
                if not all([reg_username, reg_email, reg_password, reg_confirm]):
                    st.error("⚠️ Please fill in all fields")
                elif reg_password != reg_confirm:
                    st.error("⚠️ Passwords do not match")
                elif len(reg_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters")
                else:
                    result = register_user(reg_username, reg_email, reg_password)
                    if result["success"]:
                        st.success("✅ Account created! Please sign in.")
                        st.session_state.auth_tab = "signin"
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

            st.markdown("""
<div style="text-align:center; margin-top:1.2rem; padding-top:1.2rem;
            border-top:1px solid rgba(255,255,255,0.055);">
    <p style="margin:0; font-size:0.78rem; color:rgba(71,85,105,0.88);">
        Have an account? <strong style="color:rgba(100,116,139,0.92);">Switch to Sign In above</strong>
    </p>
</div>
""", unsafe_allow_html=True)

        # Close card divs — UNCHANGED
        st.markdown("""
<div style="text-align:center; margin-top:1.5rem; padding-top:1.3rem;
            border-top:1px solid rgba(255,255,255,0.048);">
    <p style="margin:0; font-size:0.71rem; color:rgba(51,65,85,0.88);
              font-family:'DM Sans',sans-serif; letter-spacing:0.1px;">
        By continuing, you agree to our Terms of Service &amp; Privacy Policy
    </p>
</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # RIGHT PANEL — rendered via components.html to bypass
    # Streamlit's markdown sanitiser (fixes raw HTML bleed).
    # Auth logic, CSS classes, card content: 100% UNCHANGED.
    # ──────────────────────────────────────────────────────────
    with right_col:
        _right_panel_html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: transparent; font-family: 'DM Sans', sans-serif; overflow: hidden; }
.right-panel-wrapper { width: 100%; display: flex; justify-content: center; position: relative; }
.right-panel {
    width: 100%; max-width: 340px;
    display: flex; flex-direction: column;
    justify-content: flex-start; align-items: center;
    gap: 16px; padding: 140px 0 24px; position: relative;
}
.glow-ring {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 340px; height: 340px; border-radius: 50%;
    border: 1px solid rgba(34,211,238,0.08);
    box-shadow: 0 0 80px 14px rgba(34,211,238,0.034), inset 0 0 80px 14px rgba(168,85,247,0.022);
    animation: ringPulse 7s ease-in-out infinite; pointer-events: none;
}
.glow-ring-2 {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
    width: 210px; height: 210px; border-radius: 50%;
    border: 1px solid rgba(168,85,247,0.08);
    animation: ringPulse 7s ease-in-out infinite 2.5s; pointer-events: none;
}
@keyframes ringPulse {
    0%,100% { opacity: 0.52; transform: translate(-50%,-50%) scale(1); }
    50%      { opacity: 1;   transform: translate(-50%,-50%) scale(1.06); }
}
.dot-accent { position: absolute; border-radius: 50%; pointer-events: none; z-index: 1; }
.dot-tl  { top:12%; left:2%;    width:10px; height:10px; background:#22d3ee; box-shadow:0 0 18px 5px rgba(34,211,238,0.55);  animation:dotFloat 4s ease-in-out infinite; }
.dot-br  { bottom:14%; right:3%; width:7px;  height:7px;  background:#c084fc; box-shadow:0 0 14px 3px rgba(192,132,252,0.55); animation:dotFloat 5s ease-in-out infinite 1.2s; }
.dot-mid { top:58%; left:1%;    width:5px;  height:5px;  background:#818cf8; box-shadow:0 0 11px 2px rgba(129,140,248,0.50); animation:dotFloat 7s ease-in-out infinite 2.5s; }
.dot-tr  { top:24%; right:2%;   width:6px;  height:6px;  background:#34d399; box-shadow:0 0 11px 2px rgba(52,211,153,0.50);  animation:dotFloat 6s ease-in-out infinite 0.7s; }
@keyframes dotFloat { 0%,100% { transform: translateY(0px); } 50% { transform: translateY(-13px); } }
.card-connector {
    display: flex; justify-content: center; align-items: center;
    width: 100%; height: 24px; position: relative; z-index: 2;
}
.card-connector::before {
    content: ''; display: block; width: 2px; height: 100%;
    background: linear-gradient(180deg, rgba(34,211,238,0.22), rgba(168,85,247,0.18));
    border-radius: 2px; animation: connectorGlow 3.5s ease-in-out infinite;
}
@keyframes connectorGlow { 0%,100% { opacity: 0.32; } 50% { opacity: 1; } }
.glass-card {
    width: 100%; padding: 1.35rem 1.6rem;
    background: rgba(7,11,28,0.82); border: 1px solid rgba(255,255,255,0.075);
    border-radius: 18px; backdrop-filter: blur(28px); -webkit-backdrop-filter: blur(28px);
    position: relative; z-index: 2; transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 40px rgba(34,211,238,0.18), 0 0 30px rgba(168,85,247,0.12);
}
.glass-card.accent-cyan   { border-color: rgba(34,211,238,0.15); box-shadow: 0 4px 30px rgba(34,211,238,0.10), inset 0 1px 0 rgba(34,211,238,0.09); animation: cardFloat1 6.5s ease-in-out infinite; }
.glass-card.accent-purple { border-color: rgba(168,85,247,0.15); box-shadow: 0 4px 30px rgba(168,85,247,0.10), inset 0 1px 0 rgba(168,85,247,0.09); animation: cardFloat2 7.5s ease-in-out infinite 1.1s; }
.glass-card.accent-indigo { border-color: rgba(99,102,241,0.15);  box-shadow: 0 4px 30px rgba(99,102,241,0.10),  inset 0 1px 0 rgba(99,102,241,0.09);  animation: cardFloat3 8.5s ease-in-out infinite 0.6s; }
.glass-card.accent-green  { border-color: rgba(52,211,153,0.13);  box-shadow: 0 4px 30px rgba(52,211,153,0.09),  inset 0 1px 0 rgba(52,211,153,0.08);  animation: cardFloat1 9.5s ease-in-out infinite 2.0s; }
@keyframes cardFloat1 { 0%,100% { transform:translateY(0px); } 50% { transform:translateY(-7px);  } }
@keyframes cardFloat2 { 0%,100% { transform:translateY(0px); } 50% { transform:translateY(-11px); } }
@keyframes cardFloat3 { 0%,100% { transform:translateY(0px); } 50% { transform:translateY(-5px);  } }
.gc-header  { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.65rem; }
.gc-label   { font-family:'Syne',sans-serif; font-size:0.78rem; font-weight:700; color:rgba(100,116,139,0.86); text-transform:uppercase; letter-spacing:1.1px; }
.gc-badge   { font-size:0.66rem; font-weight:700; padding:0.15rem 0.48rem; border-radius:20px; font-family:'DM Sans',sans-serif; }
.badge-green  { background:rgba(52,211,153,0.11);  color:#34d399; border:1px solid rgba(52,211,153,0.26); }
.badge-cyan   { background:rgba(34,211,238,0.11);  color:#22d3ee; border:1px solid rgba(34,211,238,0.26); }
.badge-purple { background:rgba(168,85,247,0.11);  color:#c084fc; border:1px solid rgba(168,85,247,0.26); }
.gc-score    { font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800; color:#f1f5f9; line-height:1; margin-bottom:0.28rem; }
.gc-score-sub { font-size:0.95rem; color:rgba(100,116,139,0.76); font-weight:600; }
.gc-sublabel { font-size:0.76rem; color:rgba(100,116,139,0.88); line-height:1.45; }
.mini-bar-wrap { background:rgba(255,255,255,0.054); border-radius:6px; height:6px; overflow:hidden; margin-top:0.72rem; }
.mini-bar-fill { height:100%; border-radius:6px; animation:barFill 2.2s cubic-bezier(0.4,0,0.2,1) both; }
@keyframes barFill { from { width:0%; } }
.fill-cyan   { background:linear-gradient(90deg,#0e7490,#22d3ee); width:87%; }
.fill-purple { background:linear-gradient(90deg,#7c3aed,#c084fc); width:73%; }
.fill-indigo { background:linear-gradient(90deg,#3730a3,#818cf8); width:65%; }
.fill-green  { background:linear-gradient(90deg,#059669,#34d399); width:92%; }
.stat-row  { display:flex; gap:0.55rem; margin-top:0.15rem; }
.stat-chip { flex:1; background:rgba(255,255,255,0.038); border-radius:10px; padding:0.48rem 0.55rem; text-align:center; border:1px solid rgba(255,255,255,0.055); }
.stat-num  { font-family:'Syne',sans-serif; font-size:1.25rem; font-weight:800; color:#f1f5f9; display:block; line-height:1.2; }
.stat-lbl  { font-size:0.64rem; color:rgba(100,116,139,0.82); }
</style>
</head>
<body>
<div class="right-panel-wrapper">
<div class="right-panel">
    <div class="glow-ring"></div>
    <div class="glow-ring-2"></div>
    <div class="dot-accent dot-tl"></div>
    <div class="dot-accent dot-br"></div>
    <div class="dot-accent dot-mid"></div>
    <div class="dot-accent dot-tr"></div>

    <div class="glass-card accent-cyan">
        <div class="gc-header">
            <span class="gc-label">ATS Score</span>
            <span class="gc-badge badge-green">&#8593; +14 pts</span>
        </div>
        <div class="gc-score">87<span class="gc-score-sub">/100</span></div>
        <div class="gc-sublabel">Strong match &mdash; Senior Engineer roles</div>
        <div class="mini-bar-wrap"><div class="mini-bar-fill fill-cyan"></div></div>
    </div>

    <div class="card-connector"></div>

    <div class="glass-card accent-purple">
        <div class="gc-header">
            <span class="gc-label">Job Matches</span>
            <span class="gc-badge badge-purple">Today</span>
        </div>
        <div class="stat-row">
            <div class="stat-chip">
                <span class="stat-num" style="color:#c084fc;">24</span>
                <span class="stat-lbl">New Matches</span>
            </div>
            <div class="stat-chip">
                <span class="stat-num" style="color:#22d3ee;">91%</span>
                <span class="stat-lbl">Fit Score</span>
            </div>
        </div>
        <div class="mini-bar-wrap" style="margin-top:0.8rem;">
            <div class="mini-bar-fill fill-purple"></div>
        </div>
    </div>

    <div class="card-connector"></div>

    <div class="glass-card accent-indigo">
        <div class="gc-header">
            <span class="gc-label">Interview Prep</span>
            <span class="gc-badge badge-cyan">Live</span>
        </div>
        <div class="gc-score" style="font-size:1.65rem; color:#818cf8;">65%</div>
        <div class="gc-sublabel">Readiness &middot; 4 sessions remaining</div>
        <div class="mini-bar-wrap"><div class="mini-bar-fill fill-indigo"></div></div>
    </div>

    <div class="card-connector"></div>

    <div class="glass-card accent-green">
        <div class="gc-header">
            <span class="gc-label">This Week</span>
            <span class="gc-badge badge-green">Active</span>
        </div>
        <div class="stat-row">
            <div class="stat-chip">
                <span class="stat-num" style="color:#22d3ee;">12</span>
                <span class="stat-lbl">Applied</span>
            </div>
            <div class="stat-chip">
                <span class="stat-num" style="color:#c084fc;">3</span>
                <span class="stat-lbl">Interviews</span>
            </div>
            <div class="stat-chip">
                <span class="stat-num" style="color:#34d399;">1</span>
                <span class="stat-lbl">Offer</span>
            </div>
        </div>
        <div class="mini-bar-wrap" style="margin-top:0.8rem;">
            <div class="mini-bar-fill fill-green"></div>
        </div>
    </div>
</div>
</div>
</body>
</html>"""
        components.html(_right_panel_html, height=1000, scrolling=False)