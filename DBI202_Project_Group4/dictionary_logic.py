import os
from pathlib import Path

try:
    import pyodbc
except ImportError:
    pyodbc = None

def _is_truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

class DictionaryLogic:
    def __init__(self):
        # SQL configuration via environment variables or defaults
        self.server = os.getenv("DICT_SQL_SERVER", r"localhost\SQLEXPRESS03")
        self.database = os.getenv("DICT_SQL_DATABASE", "PronunciationDB")
        self.debug = _is_truthy(os.getenv("DICT_DEBUG", "false"))
        
        # Connection string using Windows Authentication
        self.conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            f"Server={self.server};"
            f"Database={self.database};"
            "Trusted_Connection=yes;"
        )

    def _log(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")

    def _get_connection(self):
        """Create and return a new SQL Server connection."""
        if pyodbc is None:
            raise ImportError("pyodbc module is not installed.")
        return pyodbc.connect(self.conn_str, timeout=2)

    def _lookup_sql(self, search_term):
        """Internal method to execute the SQL query."""
        query = """
            SELECT Word, Phonetic, Definition
            FROM Dictionary
            WHERE Word = ?
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (search_term,))
                row = cursor.fetchone()
                if row:
                    return {
                        "word": row[0].strip(),
                        "phonetic": f"[{row[1].strip()}]" if row[1] and row[1].strip() else "",
                        "definition": row[2] or "",
                    }
        except Exception as e:
            self._log(f"Database Error: {e}")
            return None
        return None

    def lookup(self, word):
        """
        Public interface to lookup a word.
        Returns a dictionary with word details or None if not found.
        """
        if not word:
            return None

        search_term = word.strip().lower()
        if not search_term:
            return None

        # Execute SQL lookup
        return self._lookup_sql(search_term)

# --- Test Block ---
if __name__ == "__main__":
    logic = DictionaryLogic()
    print("--- SpeakMaster Dictionary Logic (SQL Mode) ---")
    try:
        while True:
            query = input("\nEnter a word to search (or Ctrl+C to exit): ").strip()
            if not query:
                continue
                
            result = logic.lookup(query)
            if result:
                print(f"-> Found: {result['word']}")
                print(f"-> Phonetic: {result['phonetic']}")
                print(f"-> Definition: {result['definition']}")
            else:
                print(f"-> No entry found for '{query}'.")
    except KeyboardInterrupt:
        print("\nExiting dictionary...")