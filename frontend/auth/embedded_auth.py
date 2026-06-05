"""
embedded_auth.py
================
Self-contained authentication for Streamlit Cloud.

Bypasses the FastAPI backend entirely and reads/writes directly to the
SQLite database using the same schema as api/models.py.

No HTTP calls. No subprocess. Works on any platform.
"""

import os
import sqlite3
import time
import streamlit as st
from datetime import datetime, timedelta

# ── JWT & Crypto ──────────────────────────────────────────────────────────────
try:
    from jose import jwt
    import bcrypt
    _CRYPTO_AVAILABLE = True
except ImportError:
    _CRYPTO_AVAILABLE = False

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "clinicalai_secret_key_change_in_prod")
ALGORITHM  = "HS256"
TOKEN_TTL_MINUTES = 60

# ── Database path resolution ──────────────────────────────────────────────────
# Works locally (frontend/ subdir) and on Streamlit Cloud (repo root deployed)
_HERE     = os.path.dirname(os.path.abspath(__file__))
_ROOT     = os.path.dirname(os.path.dirname(_HERE))          # repo root
_DB_PATHS = [
    os.path.join(_ROOT, "health_app.db"),                    # local: repo root
    os.path.join(_ROOT, "frontend", "health_app.db"),        # alt local
    os.path.join(os.getcwd(), "health_app.db"),              # cwd
    "health_app.db",                                          # relative fallback
]

def _get_db_path() -> str:
    for p in _DB_PATHS:
        if os.path.exists(p):
            return p
    # Default: write next to repo root
    return _DB_PATHS[0]


# ── Cached DB connection ──────────────────────────────────────────────────────
@st.cache_resource
def _get_connection():
    """Single shared SQLite connection — initialised once per Streamlit session."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection):
    """Create tables if missing (idempotent)."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            hashed_password TEXT  NOT NULL,
            role          TEXT    DEFAULT 'patient',
            full_name     TEXT,
            hospital_name TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            username        TEXT NOT NULL,
            prediction_type TEXT,
            result          TEXT,
            probability     REAL,
            created_at      TEXT DEFAULT (datetime('now'))
        )
    """)
    # Apply schema migrations for existing DBs
    existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
    for col, defn in [
        ("role",          "TEXT DEFAULT 'patient'"),
        ("full_name",     "TEXT"),
        ("hospital_name", "TEXT"),
    ]:
        if col not in existing_cols:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} {defn}")
    conn.commit()


# ── Password helpers ──────────────────────────────────────────────────────────
def _hash_pw(plain: str) -> str:
    if _CRYPTO_AVAILABLE:
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
    # Fallback (no bcrypt): store sha256 — acceptable for demo
    import hashlib
    return "sha256:" + hashlib.sha256(plain.encode()).hexdigest()


def _verify_pw(plain: str, stored: str) -> bool:
    if stored.startswith("sha256:"):
        import hashlib
        return stored == "sha256:" + hashlib.sha256(plain.encode()).hexdigest()
    if _CRYPTO_AVAILABLE:
        try:
            return bcrypt.checkpw(plain.encode(), stored.encode())
        except Exception:
            return False
    return False


def _make_token(username: str, role: str) -> str:
    if _CRYPTO_AVAILABLE:
        payload = {
            "sub": username,
            "role": role,
            "exp": datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return f"demo_token_{username}_{int(time.time())}"


# ── Public API ────────────────────────────────────────────────────────────────
def authenticate(username: str, password: str, role: str):
    """
    Returns (success: bool, token: str | None, display_name: str)
    Fast path: demo user (admin / password) never touches the DB.
    """
    # Demo fast path
    if username == "admin" and password == "password":
        token = _make_token("admin", role)
        display_name = "Dr. Admin" if role == "doctor" else "Patient Admin"
        return True, token, display_name

    try:
        conn = _get_connection()
        row = conn.execute(
            "SELECT username, hashed_password, full_name, role "
            "FROM users WHERE username = ? OR email = ?",
            (username, username)
        ).fetchone()

        if row and _verify_pw(password, row["hashed_password"]):
            token = _make_token(row["username"], row["role"])
            display_name = row["full_name"] or row["username"]
            return True, token, display_name

        return False, None, username
    except Exception as e:
        st.session_state.get("audit_logs", []).append(
            f"Auth error at {time.ctime()}: {e}"
        )
        return False, None, username


def register_patient(full_name: str, email: str, password: str):
    """Register a patient directly into the local SQLite DB."""
    return _register(
        username=email,
        email=email,
        password=password,
        role="patient",
        full_name=full_name,
        hospital_name="",
    )


def register_doctor(clinical_id: str, hospital_name: str, doctor_name: str,
                    email: str, password: str):
    """Register a doctor / clinic directly into the local SQLite DB."""
    return _register(
        username=clinical_id,
        email=email,
        password=password,
        role="doctor",
        full_name=doctor_name,
        hospital_name=hospital_name,
    )


def _register(username, email, password, role, full_name, hospital_name):
    """Internal: insert a new user, return (ok, message)."""
    try:
        conn = _get_connection()
        # Duplicate checks
        dup = conn.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()
        if dup:
            return False, "Username or email already exists."

        hashed = _hash_pw(password)
        conn.execute(
            "INSERT INTO users (username, email, hashed_password, role, full_name, hospital_name) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, hashed, role, full_name, hospital_name),
        )
        conn.commit()
        return True, "Account created successfully"
    except sqlite3.IntegrityError as e:
        return False, "Username or email already exists."
    except Exception as e:
        return False, f"Registration error: {e}"


def log_prediction(username: str, pred_type: str, result: str, probability: float):
    """Append a prediction to history."""
    try:
        conn = _get_connection()
        conn.execute(
            "INSERT INTO prediction_history (username, prediction_type, result, probability) "
            "VALUES (?, ?, ?, ?)",
            (username, pred_type, result, probability),
        )
        conn.commit()
    except Exception:
        pass  # Non-critical


def get_history(username: str):
    """Return list of dicts for the user's prediction history."""
    try:
        conn = _get_connection()
        rows = conn.execute(
            "SELECT prediction_type, result, probability, created_at "
            "FROM prediction_history WHERE username = ? ORDER BY id DESC",
            (username,)
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []
