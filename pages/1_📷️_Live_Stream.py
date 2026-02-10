
import av
import os
import sys
import streamlit as st
import time
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder

# --- PATH SETUP (Crucial for imports) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from utils import get_mediapipe_pose
from process_frame import ProcessFrame
from thresholds import get_thresholds_beginner, get_thresholds_pro
from services.history_manager import save_workout  # <--- NEW: Import the saver

st.set_page_config(page_title="AI Fitness Stream", page_icon="📷")

st.title('AI Fitness Trainer: Live Analysis')

# --- 1. SETTINGS & INPUTS ---
mode = st.radio('Select Mode', ['Beginner', 'Pro'], horizontal=True)

thresholds = get_thresholds_beginner() if mode == 'Beginner' else get_thresholds_pro()

# --- 2. EXERCISE SELECTION (Integrated with Planner) ---
if "selected_exercise" in st.session_state:
    target_exercise = st.session_state["selected_exercise"]
    st.success(f"🎯 Target: **{target_exercise.replace('_', ' ').title()}**")
else:
    target_exercise = "bodyweight_squat"
    st.info("Default: Bodyweight Squat (Go to Planner to change)")

# --- 3. PERSISTENT PROCESSOR (The "Brain") ---
# We store the processor in session_state so it doesn't reset reps when the app refreshes
if 'live_process_frame' not in st.session_state or st.session_state.get('last_exercise') != target_exercise:
    # Initialize a fresh processor
    st.session_state.live_process_frame = ProcessFrame(exercise_name=target_exercise, thresholds=thresholds, flip_frame=True)
    st.session_state.last_exercise = target_exercise
    st.session_state.start_time = time.time()
    st.session_state.is_recording = False

# Helper to access the persistent processor
processor_ref = st.session_state.live_process_frame

# Initialize MediaPipe (Pose Detector)
pose = get_mediapipe_pose()

# --- 4. VIDEO PROCESSING CALLBACK ---
def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="rgb24")  # Decode
    
    # Process the frame (Count reps, draw skeleton)
    # Note: We use the PERSISTENT 'processor_ref' here
    frame, _ = processor_ref.process(frame, pose)
    
    return av.VideoFrame.from_ndarray(frame, format="rgb24")  # Encode

# --- 5. STREAMER & AUTO-SAVE LOGIC ---
ctx = webrtc_streamer(
    key="Squats-pose-analysis",
    video_frame_callback=video_frame_callback,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    media_stream_constraints={"video": {"width": {'min': 480, 'ideal': 480}}, "audio": False},
    video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False)
)

# --- THE MAGIC: DETECT "FINISH" ---
if ctx.state.playing:
    # If camera is ON, mark us as "Recording"
    st.session_state.is_recording = True
    
    # Show real-time stats outside the video
    try:
        reps = processor_ref.processor.reps
        st.metric("Live Rep Counter", reps)
    except:
        pass

else:
    # If camera is OFF (Finished) ... AND we were just recording...
    if st.session_state.get('is_recording', False):
        st.session_state.is_recording = False # Reset flag
        
        # 1. Gather Data
        final_reps = processor_ref.processor.reps
        final_improper = processor_ref.processor.improper_reps
        duration = int(time.time() - st.session_state.start_time)
        
        # 2. SAVE AUTOMATICALLY if there is data
        if final_reps > 0 or duration > 10:
            save_workout(target_exercise, final_reps, duration, mode)
            
            st.balloons() # Celebration!
            st.success(f"""
            ✅ **Workout Saved!**
            - **Exercise:** {target_exercise}
            - **Reps:** {final_reps}
            - **Duration:** {duration}s
            """)
            
            # 3. Optional: Reset for next set?
            # st.session_state.live_process_frame = ProcessFrame(...) 
        else:
            st.warning("Session too short - not saved.")

# --- MANUAL SAVE BUTTON (Just in case) ---
if st.button("💾 Force Save Current Session"):
    reps = processor_ref.processor.reps
    duration = int(time.time() - st.session_state.start_time)
    save_workout(target_exercise, reps, duration, mode)
    st.success(f"Manually Saved {reps} reps!")