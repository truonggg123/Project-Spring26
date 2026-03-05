import os
import hashlib
from datetime import datetime

try:
    import pyodbc
except ImportError:
    pyodbc = None

def _get_connection():
    server = os.getenv("DICT_SQL_SERVER", r"localhost\SQLEXPRESS")
    database = os.getenv("DICT_SQL_DATABASE", "PronunciationDB")
    conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={server};"
        f"Database={database};"
        "Trusted_Connection=yes;"
    )
    if pyodbc is None:
        raise Exception("pyodbc is not installed. Application requires pyodbc for SQL Server connection.")
    return pyodbc.connect(conn_str)

def _hash_password(password):
    """Hash password using SHA-256 as required by the database."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register(username, password):
    """Registers a new user. Returns (success_bool, message, user_id)."""
    if not username or not password:
        return False, "Username and password cannot be empty.", None

    try:
        conn = _get_connection()
        cursor = conn.cursor()
        hashed_pw = _hash_password(password)
        
        # sp_RegisterUser returns: UserID, Message
        cursor.execute("EXEC sp_RegisterUser @Username=?, @Password=?", (username, hashed_pw))
        row = cursor.fetchone()
        conn.commit()
        conn.close()

        if row:
            user_id = row[0]
            message = row[1]
            if user_id == -1:
                return False, message, None
            return True, message, user_id
        return False, "Registration failed randomly.", None
    except Exception as e:
        return False, f"Database Error: {e}", None

def login(username, password):
    """Logs in user. Returns (success_bool, message, user_id)."""
    if not username or not password:
        return False, "Username and password cannot be empty.", None

    try:
        conn = _get_connection()
        cursor = conn.cursor()
        hashed_pw = _hash_password(password)
        
        # sp_LoginUser returns: UserID, Username, Message if success, empty if fail
        cursor.execute("EXEC sp_LoginUser @Username=?, @Password=?", (username, hashed_pw))
        row = cursor.fetchone()
        conn.close()

        if row:
            user_id = row[0]
            # row[1] is Username, row[2] is Message
            return True, row[2], user_id
        return False, "Invalid username or password.", None
    except Exception as e:
        return False, f"Database Error: {e}", None
