import random
import datetime

# This "Local AI" maps user goals to your specific camera-capable exercises
EXERCISE_DB = {
    "legs": [
        {"name": "Bodyweight Squat", "key": "bodyweight_squat", "reps": "12-15", "sets": 3},
        {"name": "Lunge", "key": "lunge", "reps": "10/leg", "sets": 3},
    ],
    "arms": [
        {"name": "Bicep Curl", "key": "bicep_curl", "reps": "10-12", "sets": 3},
        {"name": "Hammer Curl", "key": "hammer_curl", "reps": "10-12", "sets": 3},
    ],
    "core": [
        {"name": "Plank Hold", "key": "plank", "reps": "30-45s", "sets": 3},
    ],
    "strength": [
        {"name": "Overhead Press", "key": "press", "reps": "8-10", "sets": 4},
        {"name": "Deadlift / Hinge", "key": "hinge", "reps": "8-10", "sets": 4},
    ]
}

def generate_workout_plan(name, goal, level, duration, equipment):
    """
    Simulates the AI generation from the 'brej-29' repo.
    Returns a structured dictionary (JSON-like).
    """
    
    # 1. Determine Focus Area
    plan_focus = []
    if "Strength" in goal:
        plan_focus = EXERCISE_DB['strength'] + EXERCISE_DB['legs']
    elif "Cardio" in goal or "Weight Loss" in goal:
        plan_focus = EXERCISE_DB['legs'] + EXERCISE_DB['core']
    else: # General / Muscle Building
        plan_focus = EXERCISE_DB['arms'] + EXERCISE_DB['strength']

    # 2. Adjust for Level
    multiplier = 1.0
    if level == "Beginner": multiplier = 0.8
    elif level == "Pro": multiplier = 1.5

    # 3. Build the "Warmup" (Generic)
    warmup = [
        {"name": "Jumping Jacks", "duration": "2 mins"},
        {"name": "Arm Circles", "duration": "1 min"}
    ]

    # 4. Build Main Workout
    # Select exercises based on duration (approx 5 mins per exercise including rest)
    num_exercises = int(duration / 7) 
    selected_exercises = random.sample(plan_focus, k=min(len(plan_focus), num_exercises))
    
    # Add logic to "smartly" adjust reps based on level
    main_circuit = []
    for ex in selected_exercises:
        main_circuit.append({
            "exercise": ex["name"],
            "internal_key": ex.get("key"), # This links to your Camera Processor!
            "sets": ex["sets"],
            "reps": ex["reps"],
            "rest": "60s" if level == "Beginner" else "45s"
        })

    # 5. Build Cool Down
    cooldown = [
        {"name": "Static Stretching", "duration": "3 mins"}
    ]

    return {
        "meta": {
            "generated_for": name,
            "date": str(datetime.date.today()),
            "goal": goal,
            "difficulty": level
        },
        "plan": {
            "warmup": warmup,
            "main": main_circuit,
            "cooldown": cooldown
        }
    }