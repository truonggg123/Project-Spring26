import csv
import os
import re
from pathlib import Path

try:
    import pyodbc
except ImportError:
    pyodbc = None


def _is_truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class DictionaryLogic:
    def __init__(self):
        # SQL config can be overridden by environment variables.
        self.server = os.getenv("DICT_SQL_SERVER", r"localhost\SQLEXPRESS03")
        self.database = os.getenv("DICT_SQL_DATABASE", "PronunciationDB")
        self.use_sql = _is_truthy(os.getenv("DICT_USE_SQL", "true"))
        self.debug = _is_truthy(os.getenv("DICT_DEBUG", "false"))
        base_dir = Path(__file__).resolve().parent
        csv_setting = os.getenv("DICT_CSV_FILE", "English - Vietnamese.csv")
        csv_candidate = Path(csv_setting)
        self.csv_path = csv_candidate if csv_candidate.is_absolute() else base_dir / csv_candidate
        self.conn_str = (
            "Driver={ODBC Driver 17 for SQL Server};"
            f"Server={self.server};"
            f"Database={self.database};"
            "Trusted_Connection=yes;"
        )

        self._sql_failed = False
        self._csv_cache = None

    def _log(self, message):
        if self.debug:
            print(message)

    def _get_connection(self):
        """Create a new SQL Server connection."""
        return pyodbc.connect(self.conn_str, timeout=2)

    @staticmethod
    def _format_definition(text):
        if not text:
            return ""
        text = text.replace("|*  ", "\\n\\n")
        text = text.replace("|*", "\\n\\n")
        text = text.replace("|-", "\\n- ")
        text = text.replace("|=", "\\n   Example: ")
        text = text.replace("|+", " -> ")
        text = text.replace("||@", "\\n@ ")
        return text.strip()

    @staticmethod
    def _parse_word_and_phonetic(raw_word):
        token = (raw_word or "").strip().lower()
        if not token:
            return "", ""
        match = re.search(r"\[(.*?)\]", token)
        if match:
            phonetic = match.group(1).strip()
            word = re.sub(r"\[.*?\]", "", token).strip()
            return word, phonetic
        return token, ""

    def _load_csv_cache(self):
        if not self.csv_path.exists():
            self._log(f"Dictionary CSV not found: {self.csv_path}")
            return {}

        cache = {}
        try:
            with self.csv_path.open("r", encoding="utf-16", newline="") as csv_file:
                reader = csv.reader(csv_file)
                next(reader, None)  # Skip header
                for row in reader:
                    if not row:
                        continue

                    raw_word = row[0]
                    raw_definition = ",".join(row[1:]).strip() if len(row) > 1 else ""
                    word, phonetic = self._parse_word_and_phonetic(raw_word)
                    if not word:
                        continue
                    if word in cache:
                        continue

                    cache[word] = {
                        "word": word,
                        "phonetic": f"[{phonetic}]" if phonetic else "",
                        "definition": self._format_definition(raw_definition),
                    }
            return cache
        except Exception as exc:
            self._log(f"Failed to load dictionary CSV: {exc}")
            return {}

    def _lookup_sql(self, search_term):
        query = """
            SELECT Word, Phonetic, Definition
            FROM Dictionary
            WHERE Word = ?
        """
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
        return None

    def _lookup_csv(self, search_term):
        if self._csv_cache is None:
            self._csv_cache = self._load_csv_cache()
        result = self._csv_cache.get(search_term)
        return result.copy() if result else None

    def lookup(self, word):
        """Lookup a word from CSV by default. SQL is optional via DICT_USE_SQL=true."""
        if not word:
            return None

        search_term = word.strip().lower()
        if not search_term:
            return None

        if not self.use_sql:
            return self._lookup_csv(search_term)

        if pyodbc is not None and not self._sql_failed:
            try:
                result = self._lookup_sql(search_term)
                if result:
                    return result
            except Exception:
                self._sql_failed = True
                self._log("SQL dictionary unavailable, switching to CSV fallback.")

        return self._lookup_csv(search_term)


if __name__ == "__main__":
    logic = DictionaryLogic()
    while True:
        print("Press Ctrl+C to exit.")
        query = input("Enter a word: ")
        result = logic.lookup(query)
        if result:
            print(f"Found: {result['word']}")
            print(f"Phonetic: {result['phonetic']}")
            print(f"Definition:\n{result['definition']}")
        else:
            print(f"No entry found for '{query}'.")


