import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def load_data():
    """Load history from JSON file"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure compatibility with Dataframe (convert dict to list of values)
            return [[item["date"], item["target"], item["transcribed"], item["score"], item["similarity"]] for item in data]
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_attempt(target, transcribed, score, similarity):
    """Save attempt to history file"""
    try:
        # Load raw data first
        current_history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                current_history = json.load(f)
        
        # New entry
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "target": target,
            "transcribed": transcribed,
            "score": round(score, 1),
            "similarity": f"{round(similarity * 100, 1)}%"
        }
        
        # Prepend new entry
        current_history.insert(0, entry)
        
        # Save back to file
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(current_history, f, ensure_ascii=False, indent=2)
            
        # Return formatted data for Dataframe
        return [[item["date"], item["target"], item["transcribed"], item["score"], item["similarity"]] for item in current_history]
    except Exception as e:
        print(f"Error saving history: {e}")
        return []
