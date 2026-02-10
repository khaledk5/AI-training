import json
import os
from typing import List, Dict, Optional

class WorkoutManager:
    def __init__(self, db_file: str = "workout_db.json"):
        # This will create a file named 'workout_db.json' next to your code
        self.db_file = db_file
        self.plans = self._load_db()

    def _load_db(self) -> Dict:
        """Loads the workout database from a JSON file."""
        if not os.path.exists(self.db_file):
            # If the file doesn't exist yet, return an empty structure
            return {"active_plan": None, "routines": {}}
        
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"active_plan": None, "routines": {}}

    def _save_db(self):
        """Saves current state to JSON."""
        with open(self.db_file, 'w') as f:
            json.dump(self.plans, f, indent=4)

    def create_routine(self, routine_name: str, exercises: List[Dict]):
        """
        Creates a new routine.
        Example input: 'Leg Day', [{'name': 'bodyweight_squat', 'reps': 10, 'sets': 3}]
        """
        self.plans["routines"][routine_name] = exercises
        self._save_db()

    def get_routine(self, routine_name: str) -> Optional[List[Dict]]:
        return self.plans["routines"].get(routine_name)

    def get_all_routine_names(self) -> List[str]:
        return list(self.plans["routines"].keys())

    def set_active_plan(self, routine_name: str):
        """Sets the workout the user wants to do TODAY."""
        if routine_name in self.plans["routines"]:
            self.plans["active_plan"] = routine_name
            self._save_db()

    def get_active_plan(self):
        """Returns the name and data of the currently active plan."""
        name = self.plans.get("active_plan")
        if name and name in self.plans["routines"]:
            return name, self.plans["routines"][name]
        return None, None

    def delete_routine(self, routine_name: str):
        if routine_name in self.plans["routines"]:
            del self.plans["routines"][routine_name]
            # If we deleted the active plan, reset active plan to None
            if self.plans["active_plan"] == routine_name:
                self.plans["active_plan"] = None
            self._save_db()