import streamlit as st
import time
import json
import sys
import os
from services.history_manager import get_stats
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.workout_generator import generate_workout_plan

# --- PAGE CONFIG ---
st.set_page_config(page_title="Daily Workout Planner", page_icon="📅", layout="wide")

# --- CSS STYLING (To match the clean look of the linked repo) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B; 
        color: white;
    }
    .workout-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #FF4B4B;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR INPUTS (Replicating brej-29 Logic) ---
with st.sidebar:
    st.header("⚙️ Plan Settings")
    
    user_name = st.text_input("Your Name", "Athlete")
    
    goal = st.selectbox(
        "Fitness Goal",
        ["Muscle Building", "Weight Loss", "Strength & Power", "Flexibility"]
    )
    
    env = st.radio("Environment", ["Home", "Gym"], horizontal=True)
    
    level = st.select_slider(
        "Difficulty Level", 
        options=["Beginner", "Intermediate", "Pro"]
    )
    
    duration = st.slider("Duration (Minutes)", 15, 90, 45, step=5)
    
    st.markdown("---")
    generate_btn = st.button("⚡ Generate Workout Plan")

# --- MAIN AREA ---
st.title("🏋️ Daily Workout Planner")
st.caption(f"AI-Powered generator tailored for {level} level.")

# Session State to hold the plan
if "current_plan" not in st.session_state:
    st.session_state.current_plan = None

if generate_btn:
    with st.spinner("🤖 AI is analyzing your profile... constructing routine..."):
        time.sleep(1.5) # UX effect
        plan = generate_workout_plan(user_name, goal, level, duration, env)
        st.session_state.current_plan = plan
        st.success("Plan Generated Successfully!")

# --- DISPLAY TABS ---
if st.session_state.current_plan:
    plan = st.session_state.current_plan
    
    tab1, tab2, tab3 = st.tabs(["📝 The Workout", "📊 Progress Dashboard", "💾 History"])
    
    # === TAB 1: THE PLAN ===
    with tab1:
        st.subheader(f"Today's Focus: {plan['meta']['goal']}")
        
        # Warmup Section
        with st.expander("🔥 Warm Up", expanded=True):
            for item in plan['plan']['warmup']:
                st.markdown(f"- **{item['name']}**: {item['duration']}")

        # Main Circuit
        st.markdown("### 💪 Main Circuit")
        for idx, ex in enumerate(plan['plan']['main']):
            # Render a "Card"
            with st.container():
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div class="workout-card">
                        <h4 style="margin:0">{ex['exercise']}</h4>
                        <p style="margin:0; color:#aaa">{ex['sets']} Sets | {ex['reps']} Reps | {ex['rest']} Rest</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # THE INTEGRATION: Button to launch YOUR Camera AI
                with cols[1]:
                    if ex.get('internal_key'):
                        st.write("") # Spacer
                        if st.button(f"📷 Start AI Tracking", key=f"btn_{idx}"):
                            # Set the session state for the Live Stream page
                            st.session_state["selected_exercise"] = ex['internal_key']
                            st.switch_page("pages/1_📷_Live_Stream.py") # Direct navigation

        # Cooldown
        with st.expander("❄️ Cool Down"):
            for item in plan['plan']['cooldown']:
                st.markdown(f"- **{item['name']}**: {item['duration']}")

    # === TAB 2: REAL DASHBOARD ===
    with tab2:
        # 1. Get Real Stats
        stats = get_stats()
        
        st.header("📊 Your Progress")
        
        # 2. Show Metrics (Real Data)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Workouts", stats["total_workouts"])
        with col2:
            st.metric("Last Session", stats["last_workout"])
        with col3:
            st.metric("Status", "Active" if stats["total_workouts"] > 0 else "New Member")

        # 3. Show History Table (if data exists)
        if stats["total_workouts"] > 0:
            st.subheader("📜 History Log")
            st.table(stats["history"])
        else:
            st.info("No workouts recorded yet. Go to 'The Workout' tab and start training!")

    # === TAB 3: JSON / SAVE ===
    with tab3:
        st.json(plan)
        st.download_button(
            "Download Plan (JSON)",
            data=json.dumps(plan, indent=2),
            file_name="daily_workout.json",
            mime="application/json"
        )

else:
    st.info("👈 Select your settings in the sidebar and click Generate!")