"""
database.py - Member 1: Python connector (Hiếu)
================================================
This file does NOT define the database structure.
All tables and stored procedures live in setup_database.sql.

This file only connects to SQL Server and calls those stored procedures.

Setup order:
    1. Run setup_database.sql in SSMS or sqlcmd  ← build the DB first
    2. pip install pyodbc
    3. Update DB_CONFIG below
    4. Import this module in app.py / logic.py
"""

import pyodbc
import hashlib
import os

# ==========================================
# DATABASE CONFIGURATION
# ==========================================
DB_CONFIG = {
    "driver":   os.getenv("DB_DRIVER",   "ODBC Driver 17 for SQL Server"),
    "server":   os.getenv("DB_SERVER",   "localhost"),        # e.g. "localhost\\SQLEXPRESS"
    "database": os.getenv("DB_NAME",     "PronunciationDB"),
    "username": os.getenv("DB_USER",     "sa"),
    "password": os.getenv("DB_PASSWORD", "YourPassword123"),  # change this!
    "trusted":  os.getenv("DB_TRUSTED",  "no"),               # "yes" = Windows Auth
}


def _get_connection() -> pyodbc.Connection:
    if DB_CONFIG["trusted"].lower() == "yes":
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"Trusted_Connection=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']};"
        )
    return pyodbc.connect(conn_str, autocommit=False)


def _hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


# ==========================================
# USER MANAGEMENT
# ==========================================
def register_user(username: str, password: str) -> dict:
    """Calls sp_RegisterUser. Returns {success, message, user_id}."""
    if not username or not password or len(password) < 6:
        return {"success": False, "message": "Invalid input.", "user_id": None}
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC sp_RegisterUser ?, ?", username.strip(), _hash_password(password))
            row = cursor.fetchone()
            conn.commit()
        if row and row[0] != -1:
            return {"success": True,  "message": row[1], "user_id": int(row[0])}
        return {"success": False, "message": row[1] if row else "Unknown error.", "user_id": None}
    except Exception as e:
        return {"success": False, "message": str(e), "user_id": None}


def login_user(username: str, password: str) -> dict:
    """Calls sp_LoginUser. Returns {success, message, user_id, username}."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC sp_LoginUser ?, ?", username.strip(), _hash_password(password))
            row = cursor.fetchone()
        if row:
            return {"success": True, "message": row[2], "user_id": int(row[0]), "username": row[1]}
        return {"success": False, "message": "Invalid username or password.", "user_id": None, "username": None}
    except Exception as e:
        return {"success": False, "message": str(e), "user_id": None, "username": None}


# ==========================================
# PRACTICE HISTORY
# ==========================================
def save_practice_result(user_id: int, target: str, user_text: str, score: float, similarity: float) -> bool:
    """Calls sp_SavePracticeResult."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_SavePracticeResult ?, ?, ?, ?, ?",
                user_id, target, user_text, round(score, 1), f"{round(similarity * 100, 1)}%"
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB] save_practice_result error: {e}")
        return False


def load_history(user_id: int) -> list:
    """Calls sp_LoadHistory. Returns list of lists for Gradio Dataframe."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC sp_LoadHistory ?", user_id)
            rows = cursor.fetchall()
        return [[r[1], r[2], r[3], r[4], r[5]] for r in rows]  # skip HistoryID
    except Exception as e:
        print(f"[DB] load_history error: {e}")
        return []


def get_user_stats(user_id: int) -> dict:
    """Calls sp_GetUserStats."""
    try:
        with _get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("EXEC sp_GetUserStats ?", user_id)
            row = cursor.fetchone()
        if row:
            return {"total_attempts": row[0], "average_score": row[1], "best_score": row[2], "last_practiced": row[3]}
        return {}
    except Exception as e:
        print(f"[DB] get_user_stats error: {e}")
        return {}
