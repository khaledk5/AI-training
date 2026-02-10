import json
import os
from datetime import datetime

HISTORY_FILE = "workout_history.json"

def get_history():
    """Loads the workout history from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return [] # Return empty list if no file exists
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_workout(exercise_name, reps, duration_sec, difficulty):
    """Saves a completed workout session."""
    history = get_history()
    
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "exercise": exercise_name,
        "reps": reps,
        "duration": f"{duration_sec}s",
        "difficulty": difficulty
    }
    
    history.append(entry)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)

def get_stats():
    """Calculates real stats from the history file."""
    history = get_history()
    
    if not history:
        return {"total_workouts": 0, "last_workout": "Never"}
    
    return {
        "total_workouts": len(history),
        "last_workout": history[-1]['date'],
        "history": history
    }