import os
from datetime import datetime

# Optional fallback logic, but primarily we depend on auth.py connection
try:
    import auth
except ImportError:
    auth = None

def load_data(user_id=None):
    """Load history from SQL using sp_LoadHistory. Returns [['Date', 'Target', 'Transcribed', score, 'Similarity']]"""
    if not user_id:
        return []

    try:
        conn = auth._get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_LoadHistory @UserID=?", (user_id,))
        rows = cursor.fetchall()
        conn.close()

        # sp_LoadHistory returns: HistoryID, PracticedAt, TargetText, UserText, Score, Similarity
        data = [[row[1], row[2], row[3], row[4], row[5]] for row in rows]
        return data
    except Exception as e:
        print(f"Error loading history from SQL: {e}")
        return []

def save_attempt(user_id, target, transcribed, score, similarity):
    """Save attempt to SQL using sp_SavePracticeResult"""
    if not user_id:
        print("save_attempt: Cannot save history without a logged-in UserID")
        return load_data(None)

    try:
        conn = auth._get_connection()
        cursor = conn.cursor()
        
        sim_str = f"{round(similarity * 100, 1)}%"
        # @UserID, @Target, @UserText, @Score, @Similarity
        cursor.execute(
            "EXEC sp_SavePracticeResult @UserID=?, @Target=?, @UserText=?, @Score=?, @Similarity=?", 
            (user_id, target, transcribed, round(score, 1), sim_str)
        )
        conn.commit()
        conn.close()

        return load_data(user_id)
    except Exception as e:
        print(f"Error saving history to SQL: {e}")
        return load_data(user_id)

