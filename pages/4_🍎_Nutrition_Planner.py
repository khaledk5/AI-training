import streamlit as st
from services.nutrition_engine import calculate_nutrition, get_recommendations

st.set_page_config(page_title="AI Nutrition", page_icon="🍎")
st.title("🍎 Personalized Nutrition Dashboard")

# 1. Inputs
with st.sidebar:
    st.header("User Stats")
    age = st.number_input("Age", 18, 100, 25)
    weight = st.number_input("Weight (kg)", 40, 200, 70)
    height = st.number_input("Height (cm)", 120, 220, 175)
    gender = st.selectbox("Gender", ["Male", "Female"])
    goal = st.selectbox("Goal", ["Muscle Building", "Weight Loss", "General Health"])

# 2. Results
if st.button("Generate My Plan"):
    target_cal = calculate_nutrition(weight, age, height, gender, goal)
    foods = get_recommendations(target_cal, goal)
    
    st.success(f"Target: {target_cal} Calories per day")
    
    st.subheader("📋 Recommended Foods from Database")
    if isinstance(foods, list):
        # Create a nice table for the Kaggle data
        st.table(foods)
    else:
        st.error(foods["error"])

    st.info("These suggestions are based on high-density nutritional analysis from the Kaggle Daily Food dataset.")