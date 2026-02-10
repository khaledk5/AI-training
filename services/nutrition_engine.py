import pandas as pd
import os

# Load the Kaggle dataset
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'daily_food_nutrition_dataset.csv')

def get_recommendations(target_calories, goal):
    try:
        df = pd.read_csv(
            DATA_PATH, 
            on_bad_lines='skip', 
            engine='python', 
            encoding='utf-8'
        )
        
        # 1. CLEAN COLUMN NAMES (The most important step)
        # Removes spaces, makes lowercase, and removes units like (g) or (kcal)
        df.columns = df.columns.str.strip().str.lower().str.replace(r'\(.*\)', '', regex=True).str.strip()
        
        # Now columns are likely: 'food_item', 'calories', 'protein', 'category'
        # Let's map them to make sure we use the right ones
        col_map = {
            'food_item': [c for c in df.columns if 'food' in c][0],
            'calories': [c for c in df.columns if 'cal' in c][0],
            'protein': [c for c in df.columns if 'prot' in c][0],
            'category': [c for c in df.columns if 'cat' in c][0]
        }

    except Exception as e:
        return {"error": f"Dataset Error: {e}. Check if CSV has Food, Calories, and Protein columns."}

    # 2. FILTER BY GOAL (Using our mapped column names)
    if goal == "Muscle Building":
        recommendations = df.sort_values(by=col_map['protein'], ascending=False).head(5)
    elif goal == "Weight Loss":
        recommendations = df.sort_values(by=col_map['calories'], ascending=True).head(5)
    else:
        recommendations = df.sample(5)

    # 3. RETURN DATA
    # We rename them back to nice names for the table
    return recommendations[[col_map['food_item'], col_map['calories'], col_map['protein'], col_map['category']]].rename(
        columns={
            col_map['food_item']: 'Food Item',
            col_map['calories']: 'Calories',
            col_map['protein']: 'Protein',
            col_map['category']: 'Category'
        }
    ).to_dict('records')

def calculate_nutrition(weight, age, height, gender, goal):
    # Basic BMR (Mifflin-St Jeor)
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "Male" else -161)
    
    # Adjust for activity and goal
    target_cal = int(bmr * 1.2) # Sedentary multiplier for safety
    if goal == "Muscle Building":
        target_cal += 300
    elif goal == "Weight Loss":
        target_cal -= 500
        
    return target_cal