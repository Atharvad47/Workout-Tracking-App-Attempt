import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Page configuration
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide"
)

# Minimal, clean CSS
def apply_minimal_css():
    st.markdown("""
    <style>
    /* Clean typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Remove clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Spacing and readability */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Simple headers */
    h1 {
        font-weight: 700;
        font-size: 28px;
        margin-bottom: 1.5rem;
        color: #1a1a1a;
    }
    
    h2 {
        font-weight: 600;
        font-size: 20px;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2a2a2a;
    }
    
    h3 {
        font-weight: 600;
        font-size: 16px;
        color: #4a4a4a;
    }
    
    /* Clean inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea textarea {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 14px;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea textarea:focus {
        border-color: #4a4a4a;
        box-shadow: 0 0 0 1px #4a4a4a;
    }
    
    /* Minimal buttons */
    .stButton > button {
        background-color: #1a1a1a;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 24px;
        font-size: 14px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #2a2a2a;
    }
    
    /* Clean metrics */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 13px;
        font-weight: 500;
        color: #6a6a6a;
    }
    
    /* Minimal sidebar */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Clean dataframe */
    [data-testid="stDataFrame"] {
        font-size: 14px;
    }
    
    /* Simple alerts */
    .stSuccess, .stInfo, .stWarning, .stError {
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px;
        font-size: 14px;
        font-weight: 500;
        color: #6a6a6a;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1a1a1a;
        border-bottom: 2px solid #1a1a1a;
    }
    
    /* Radio buttons */
    .stRadio > div {
        gap: 16px;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

# File paths
WORKOUTS_FILE = "workouts_log.csv"
EXERCISES_FILE = "exercises_library.json"

DEFAULT_EXERCISES = {
    "Chest": ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-ups"],
    "Back": ["Pull-ups", "Lower Back", "Row", "Lat Pulldown"],
    "Shoulders": ["Overhead Press", "Lateral Raise", "Front Raise", "Shrugs"],
    "Legs": ["Squat", "Leg Press", "Leg Raise", "Leg Curl", "Calf Raise"],
    "Arms": ["Bicep Curl", "Tricep Extension", "Hammer Curl", "Tricep Dips"],
    "Core": ["Plank", "Crunches", "Leg Raises", "Russian Twist"]
}

def check_password():
    def password_entered():
        if st.session_state["password"] == "gymbuddy2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password")
        return False
    else:
        return True

def get_current_user():
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    if not st.session_state.username:
        username = st.text_input("Your name", placeholder="Enter your name")
        if username:
            st.session_state.username = username
            st.rerun()
        st.stop()
    
    return st.session_state.username

def initialize_files():
    if not os.path.exists(WORKOUTS_FILE):
        df = pd.DataFrame(columns=['date', 'time', 'user', 'muscle_group', 'exercise', 
                                    'sets', 'reps', 'weight', 'notes'])
        df.to_csv(WORKOUTS_FILE, index=False)
    
    if not os.path.exists(EXERCISES_FILE):
        with open(EXERCISES_FILE, 'w') as f:
            json.dump(DEFAULT_EXERCISES, f)

def load_workouts():
    if os.path.exists(WORKOUTS_FILE):
        df = pd.read_csv(WORKOUTS_FILE)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()

def save_workout(workout_data):
    df = load_workouts()
    new_row = pd.DataFrame([workout_data])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(WORKOUTS_FILE, index=False)

def load_exercises():
    with open(EXERCISES_FILE, 'r') as f:
        return json.load(f)

def main():
    apply_minimal_css()
    
    if not check_password():
        st.stop()
    
    initialize_files()
    current_user = get_current_user()
    
    # Minimal sidebar
    st.sidebar.text(f"Logged in: {current_user}")
    if st.sidebar.button("Logout"):
        st.session_state.username = ""
        st.session_state.password_correct = False
        st.rerun()
    
    st.sidebar.divider()
    page = st.sidebar.radio("", ["Log Workout", "History", "Stats", "Exercises"], label_visibility="collapsed")
    
    if page == "Log Workout":
        log_workout_page(current_user)
    elif page == "History":
        view_history_page(current_user)
    elif page == "Stats":
        statistics_page(current_user)
    elif page == "Exercises":
        manage_exercises_page()

def log_workout_page(username):
    st.title("Log Workout")
    
    exercises_lib = load_exercises()
    
    col1, col2 = st.columns(2)
    
    with col1:
        workout_date = st.date_input("Date", value=datetime.now())
        workout_time = st.time_input("Time", value=datetime.now().time())
        muscle_group = st.selectbox("Muscle Group", list(exercises_lib.keys()))
    
    with col2:
        exercise = st.selectbox("Exercise", exercises_lib[muscle_group])
        sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
        reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, value=0.0)
    
    notes = st.text_area("Notes", placeholder="Optional notes")
    
    if st.button("Save Workout", use_container_width=True):
        workout_data = {
            'date': workout_date,
            'time': workout_time.strftime("%H:%M"),
            'user': username,
            'muscle_group': muscle_group,
            'exercise': exercise,
            'sets': sets,
            'reps': reps,
            'weight': weight,
            'notes': notes
        }
        save_workout(workout_data)
        st.success("Workout saved")
        st.rerun()

def view_history_page(username):
    st.title("History")
    
    df = load_workouts()
    
    if df.empty:
        st.info("No workouts logged yet")
        return
    
    view_mode = st.radio("", ["My workouts", "All users"], horizontal=True, label_visibility="collapsed")
    
    if view_mode == "My workouts":
        df = df[df['user'] == username]
    
    if df.empty:
        st.info("No workouts found")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        exercises_lib = load_exercises()
        muscle_filter = st.selectbox("Muscle group", ["All"] + list(exercises_lib.keys()))
    with col2:
        days_back = st.selectbox("Period", ["7 Days", "30 Days", "90 Days", "All"])
    with col3:
        st.write("")  # Spacer
    
    # Apply filters
    filtered_df = df.copy()
    
    if muscle_filter != "All":
        filtered_df = filtered_df[filtered_df['muscle_group'] == muscle_filter]
    
    if days_back != "All":
        days = int(days_back.split()[0])
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_df = filtered_df[filtered_df['date'] >= cutoff_date]
    
    st.write(f"{len(filtered_df)} workouts")
    
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values('date', ascending=False)
        display_df = filtered_df[['date', 'time', 'user', 'muscle_group', 'exercise', 
                                   'sets', 'reps', 'weight', 'notes']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        csv = filtered_df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name=f"workouts_{datetime.now().strftime('%Y%m%d')}.csv", 
                          mime="text/csv")

def statistics_page(username):
    st.title("Stats")
    
    df = load_workouts()
    
    if df.empty:
        st.info("No data available")
        return
    
    view_mode = st.radio("", ["My stats", "All users"], horizontal=True, label_visibility="collapsed")
    
    if view_mode == "My stats":
        df = df[df['user'] == username]
    
    if df.empty:
        st.info("No workouts found")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Workouts", len(df))
    with col2:
        st.metric("Sets", int(df['sets'].sum()))
    with col3:
        st.metric("Volume (kg)", f"{(df['sets'] * df['reps'] * df['weight']).sum():,.0f}")
    with col4:
        st.metric("Exercises", df['exercise'].nunique())
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("By Muscle Group")
        muscle_counts = df['muscle_group'].value_counts()
        st.bar_chart(muscle_counts)
    
    with col2:
        st.subheader("Top Exercises")
        top_exercises = df['exercise'].value_counts().head(5)
        st.dataframe(top_exercises, use_container_width=True)
    
    # Progress tracker
    st.divider()
    st.subheader("Exercise Progress")
    
    all_exercises = sorted(df['exercise'].unique())
    selected_exercise = st.selectbox("Exercise", all_exercises, label_visibility="collapsed")
    
    exercise_df = df[df['exercise'] == selected_exercise].copy()
    exercise_df = exercise_df.sort_values('date')
    
    if not exercise_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Weight")
            weight_progress = exercise_df.groupby('date')['weight'].max()
            st.line_chart(weight_progress)
            max_weight = exercise_df['weight'].max()
            st.metric("PR", f"{max_weight} kg")
        
        with col2:
            st.write("Volume")
            exercise_df['volume'] = exercise_df['sets'] * exercise_df['reps'] * exercise_df['weight']
            volume_progress = exercise_df.groupby('date')['volume'].sum()
            st.line_chart(volume_progress)
            max_volume = exercise_df['volume'].max()
            st.metric("Max", f"{max_volume:,.0f} kg")
        
        st.write("Recent")
        recent = exercise_df[['date', 'sets', 'reps', 'weight']].tail(10).sort_values('date', ascending=False)
        recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent, use_container_width=True, hide_index=True)

def manage_exercises_page():
    st.title("Exercises")
    
    exercises_lib = load_exercises()
    
    tab1, tab2 = st.tabs(["View", "Add"])
    
    with tab1:
        for muscle_group, exercises in exercises_lib.items():
            with st.expander(f"{muscle_group} ({len(exercises)})"):
                for exercise in exercises:
                    st.write(f"• {exercise}")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            new_muscle_group = st.selectbox("Muscle Group", 
                                             list(exercises_lib.keys()) + ["+ New"])
            
            if new_muscle_group == "+ New":
                new_muscle_group = st.text_input("New muscle group")
        
        with col2:
            new_exercise = st.text_input("Exercise name")
        
        if st.button("Add", use_container_width=True):
            if new_muscle_group and new_exercise:
                if new_muscle_group not in exercises_lib:
                    exercises_lib[new_muscle_group] = []
                
                if new_exercise not in exercises_lib[new_muscle_group]:
                    exercises_lib[new_muscle_group].append(new_exercise)
                    
                    with open(EXERCISES_FILE, 'w') as f:
                        json.dump(exercises_lib, f)
                    
                    st.success(f"Added {new_exercise}")
                    st.rerun()
                else:
                    st.warning("Exercise already exists")
            else:
                st.error("Fill all fields")

if __name__ == "__main__":
    main()

