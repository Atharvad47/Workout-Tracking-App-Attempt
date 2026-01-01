import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# ---------- CONFIG ----------

st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

WORKOUTS_FILE = "workouts_log.csv"
EXERCISES_FILE = "exercises_library.json"
BODYWEIGHT_FILE = "bodyweight_log.csv"

DEFAULT_EXERCISES = {
    "Chest": ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-ups"],
    "Back": ["Pull-ups", "Lower Back", "Row", "Lat Pulldown"],
    "Shoulders": ["Overhead Press", "Lateral Raise", "Front Raise", "Shrugs"],
    "Legs": ["Squat", "Leg Press", "Leg Raise", "Leg Curl", "Calf Raise"],
    "Arms": ["Bicep Curl", "Tricep Extension", "Hammer Curl", "Tricep Dips"],
    "Core": ["Plank", "Crunches", "Leg Raises", "Russian Twist"]
}

# ---------- MINIMAL MOBILE-FRIENDLY CSS ----------

def apply_minimal_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    .stButton > button {
        background-color: #1a1a1a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 24px;
        font-size: 16px;
        font-weight: 500;
        width: 100%;
        min-height: 48px;
        transition: background-color 0.2s;
    }
    .stButton > button:hover {
        background-color: #2a2a2a;
    }
    h1 {
        font-weight: 700;
        font-size: 24px;
        margin-bottom: 1rem;
        color: #1a1a1a;
    }
    h2 {
        font-weight: 600;
        font-size: 18px;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        color: #2a2a2a;
    }
    h3 {
        font-weight: 600;
        font-size: 16px;
        color: #4a4a4a;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea textarea {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 16px;
        min-height: 48px;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea textarea:focus {
        border-color: #4a4a4a;
        box-shadow: 0 0 0 2px rgba(74, 74, 74, 0.1);
    }
    [data-testid="stMetricValue"] {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
    }
    [data-testid="stMetricLabel"] {
        font-size: 12px;
        font-weight: 500;
        color: #6a6a6a;
    }
    .stRadio > div {
        gap: 12px;
    }
    .stRadio label {
        padding: 10px 16px;
        font-size: 15px;
    }
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    .month-card {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .month-title {
        font-weight: 600;
        font-size: 16px;
        color: #1a1a1a;
        margin-bottom: 8px;
    }
    .month-stat {
        font-size: 14px;
        color: #4a4a4a;
        margin: 4px 0;
    }
    .user-badge {
        background-color: #f0f0f0;
        padding: 8px 12px;
        border-radius: 6px;
        display: inline-block;
        font-size: 14px;
        font-weight: 500;
        color: #2a2a2a;
        margin-bottom: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------- FILE INIT & LOAD/SAVE ----------

def initialize_files():
    # Workouts
    if not os.path.exists(WORKOUTS_FILE):
        df = pd.DataFrame(columns=[
            'date', 'time', 'profile_id',
            'workout_type',
            'muscle_group', 'exercise',
            'sets', 'reps', 'weight',
            'duration_min', 'distance_km', 'calories',
            'intensity', 'elevation',
            'notes'
        ])
        df.to_csv(WORKOUTS_FILE, index=False)
    
    # Exercises library
    if not os.path.exists(EXERCISES_FILE):
        with open(EXERCISES_FILE, 'w') as f:
            json.dump(DEFAULT_EXERCISES, f)
    
    # Bodyweight
    if not os.path.exists(BODYWEIGHT_FILE):
        bw_df = pd.DataFrame(columns=['date', 'profile_id', 'bodyweight_kg'])
        bw_df.to_csv(BODYWEIGHT_FILE, index=False)

def load_workouts():
    if os.path.exists(WORKOUTS_FILE):
        df = pd.read_csv(WORKOUTS_FILE)
        if not df.empty:
            # Handle old data that might have 'time' column
            if 'time' in df.columns:
                df = df.drop(columns=['time'])
            
            # Safely convert date
            try:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            except:
                pass
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

def load_bodyweight():
    if os.path.exists(BODYWEIGHT_FILE):
        df = pd.read_csv(BODYWEIGHT_FILE)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()

def save_bodyweight(entry):
    df = load_bodyweight()
    new_row = pd.DataFrame([entry])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(BODYWEIGHT_FILE, index=False)

# ---------- PROFILE HANDLING ----------

def get_profile_id():
    if "profile_id" not in st.session_state:
        st.session_state.profile_id = ""
    
    st.subheader("Your Profile")
    profile_id = st.text_input(
        "Profile ID (use the same each time to see your data)",
        value=st.session_state.profile_id,
        placeholder="e.g., rohan, rohan123"
    )
    
    if st.button("Set Profile", use_container_width=True):
        if not profile_id.strip():
            st.error("Please enter a profile ID.")
        else:
            st.session_state.profile_id = profile_id.strip()
            st.rerun()
    
    if not st.session_state.profile_id:
        st.info("Set your Profile ID to start using the app.")
        st.stop()
    
    return st.session_state.profile_id

# ---------- STATS HELPERS ----------

def get_monthly_stats(df, profile_id=None):
    if df.empty:
        return []
    if profile_id:
        df = df[df['profile_id'] == profile_id]
    if df.empty:
        return []
    df['year_month'] = df['date'].dt.to_period('M')
    monthly_data = []
    for period in df['year_month'].unique():
        month_df = df[df['year_month'] == period]
        stats = {
            'period': period,
            'month_name': period.strftime('%B %Y'),
            'workouts': len(month_df),
            'total_sets': int(month_df['sets'].sum()),
            'total_volume': (month_df['sets'] * month_df['reps'] * month_df['weight']).sum(),
            'unique_exercises': month_df['exercise'].nunique(),
            'avg_workouts_per_week': len(month_df) / 4.33
        }
        monthly_data.append(stats)
    monthly_data.sort(key=lambda x: x['period'], reverse=True)
    return monthly_data

# ---------- PAGES ----------

def log_workout_page(profile_id):
    st.header("Log Workout")
    
    workout_type = st.radio(
        "Type",
        ["Strength", "Cardio"],
        horizontal=True
    )
    
    exercises_lib = load_exercises()
    workout_date = st.date_input("Date", value=datetime.now())
    workout_time = st.time_input("Time", value=datetime.now().time())
    
    if workout_type == "Strength":
        muscle_group = st.selectbox("Muscle Group", list(exercises_lib.keys()))
        exercise = st.selectbox("Exercise", exercises_lib[muscle_group])
        
        col1, col2 = st.columns(2)
        with col1:
            sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
            reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
        with col2:
            weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, value=0.0)
        
        duration_min = 0.0
        distance_km = 0.0
        calories = 0.0
        intensity = ""
        elevation = 0.0
    
    else:  # Cardio
        cardio_exercises = [
            "Treadmill",
            "Walking (outdoor)",
            "Jogging",
            "Running",
            "Marathon",
            "Cycling",
            "Cycling (outdoor)",
            "Trekking",
            "Elliptical",
            "Rowing"
        ]
        muscle_group = "Cardio"
        exercise = st.selectbox("Cardio Type", cardio_exercises)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            duration_min = st.number_input(
                "Duration (min)", min_value=1.0, max_value=600.0, value=30.0, step=1.0
            )
        with col2:
            distance_km = st.number_input(
                "Distance (km)", min_value=0.0, max_value=200.0, value=0.0, step=0.1
            )
        with col3:
            calories = st.number_input(
                "Calories", min_value=0.0, max_value=8000.0, value=0.0, step=10.0
            )
        
        intensity = st.selectbox(
            "Intensity",
            ["Easy", "Moderate", "Hard"],
            index=1
        )
        
        if exercise == "Treadmill":
            elevation = st.number_input(
                "Elevation / Incline (%)",
                min_value=0.0, max_value=30.0, value=0.0, step=0.5
            )
        else:
            elevation = 0.0
        
        sets = 0
        reps = 0
        weight = 0.0
    
    notes = st.text_area("Notes", placeholder="Optional notes", height=80)
    
    if st.button("Save Workout", use_container_width=True):
        workout_data = {
            'date': workout_date,
            'time': workout_time.strftime("%H:%M"),
            'profile_id': profile_id,
            'workout_type': workout_type.lower(),
            'muscle_group': muscle_group,
            'exercise': exercise,
            'sets': int(sets),
            'reps': int(reps),
            'weight': float(weight),
            'duration_min': float(duration_min),
            'distance_km': float(distance_km),
            'calories': float(calories),
            'intensity': intensity,
            'elevation': float(elevation),
            'notes': notes
        }
        save_workout(workout_data)
        st.success("Workout saved")
        st.rerun()

def view_history_page(profile_id):
    st.header("History")
    
    df = load_workouts()
    if df.empty:
        st.info("No workouts logged yet")
        return
    
    df = df[df['profile_id'] == profile_id]
    if df.empty:
        st.info("No workouts found for this profile")
        return
    
    exercises_lib = load_exercises()
    muscle_filter = st.selectbox("Muscle group", ["All"] + list(exercises_lib.keys()) + ["Cardio"])
    days_back = st.selectbox("Period", ["7 Days", "30 Days", "90 Days", "All"])
    
    filtered_df = df.copy()
    if muscle_filter != "All":
        if muscle_filter == "Cardio":
            filtered_df = filtered_df[filtered_df['muscle_group'] == "Cardio"]
        else:
            filtered_df = filtered_df[filtered_df['muscle_group'] == muscle_filter]
    
    if days_back != "All":
        days = int(days_back.split()[0])
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_df = filtered_df[filtered_df['date'] >= cutoff_date]
    
    st.write(f"{len(filtered_df)} workouts")
    
    if not filtered_df.empty:
        filtered_df = filtered_df.sort_values('date', ascending=False)
        
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df = display_df[[
            'date', 'workout_type', 'muscle_group', 'exercise',
            'sets', 'reps', 'weight',
            'duration_min', 'distance_km', 'calories',
            'intensity', 'elevation',
            'notes'
        ]]
        st.dataframe(display_df.head(50), use_container_width=True, hide_index=True)
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            file_name=f"workouts_{profile_id}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def statistics_page(profile_id):
    st.header("Stats")
    
    df = load_workouts()
    if df.empty:
        st.info("No data available")
        return
    
    df = df[df['profile_id'] == profile_id]
    if df.empty:
        st.info("No workouts found for this profile")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Workouts", len(df))
        st.metric("Volume (kg)", f"{(df['sets'] * df['reps'] * df['weight']).sum():,.0f}")
    with col2:
        st.metric("Sets", int(df['sets'].sum()))
        st.metric("Exercises", df['exercise'].nunique())
    
    st.divider()
    
    st.subheader("Top Exercises")
    top_exercises = df['exercise'].value_counts().head(5)
    st.dataframe(top_exercises, use_container_width=True)
    
    st.divider()
    st.subheader("Exercise Progress")
    
    all_exercises = sorted(df['exercise'].unique())
    if not all_exercises:
        st.info("No exercises logged yet")
        return
    selected_exercise = st.selectbox("Exercise", all_exercises, label_visibility="collapsed")
    
    exercise_df = df[df['exercise'] == selected_exercise].copy()
    exercise_df = exercise_df.sort_values('date')
    
    if not exercise_df.empty:
        st.write("Weight Progress")
        weight_progress = exercise_df.groupby('date')['weight'].max()
        st.line_chart(weight_progress)
        
        max_weight = exercise_df['weight'].max()
        st.metric("PR", f"{max_weight} kg")
        
        st.write("Recent")
        recent = exercise_df[['date', 'sets', 'reps', 'weight']].tail(5).sort_values('date', ascending=False)
        recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent, use_container_width=True, hide_index=True)

def monthly_progress_page(profile_id):
    st.header("Monthly Progress")
    
    df = load_workouts()
    if df.empty:
        st.info("No data available")
        return
    
    monthly_stats = get_monthly_stats(df, profile_id)
    if not monthly_stats:
        st.info("No workouts found for this profile")
        return
    
    current_month = monthly_stats[0]
    st.subheader(current_month['month_name'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Workouts", current_month['workouts'])
        st.metric("Volume", f"{current_month['total_volume']:,.0f} kg")
    with col2:
        st.metric("Sets", current_month['total_sets'])
        st.metric("Exercises", current_month['unique_exercises'])
    
    st.divider()
    st.subheader("Past Months")
    
    for month_stat in monthly_stats:
        st.markdown(f"""
        <div class="month-card">
            <div class="month-title">{month_stat['month_name']}</div>
            <div class="month-stat">Workouts: {month_stat['workouts']} ({month_stat['avg_workouts_per_week']:.1f}/week)</div>
            <div class="month-stat">Sets: {month_stat['total_sets']} | Volume: {month_stat['total_volume']:,.0f} kg</div>
            <div class="month-stat">Exercises: {month_stat['unique_exercises']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Workout Trend")
    
    chart_data = pd.DataFrame([
        {'Month': stat['month_name'][:3], 'Workouts': stat['workouts']} 
        for stat in reversed(monthly_stats[-6:])
    ])
    st.bar_chart(chart_data.set_index('Month'))

def log_bodyweight_page(profile_id):
    st.header("Bodyweight (Weekly)")
    
    today = datetime.now().date()
    bw_df = load_bodyweight()
    
    entry_date = st.date_input("Date", value=today)
    bodyweight_kg = st.number_input(
        "Bodyweight (kg)",
        min_value=30.0, max_value=300.0,
        value=70.0, step=0.1
    )
    
    st.caption("Tip: Log once a week, same day/time for consistency.")
    
    if st.button("Save Bodyweight", use_container_width=True):
        entry = {
            'date': entry_date,
            'profile_id': profile_id,
            'bodyweight_kg': float(bodyweight_kg)
        }
        save_bodyweight(entry)
        st.success("Bodyweight entry saved")
        st.rerun()
    
    user_bw = bw_df[bw_df['profile_id'] == profile_id].sort_values('date', ascending=False)
    if not user_bw.empty:
        st.subheader("Recent Entries")
        recent = user_bw.head(10).copy()
        recent['date'] = recent['date'].dt.strftime('%Y-%m-%d')
        st.dataframe(recent, use_container_width=True, hide_index=True)
        
        st.subheader("Trend")
        trend = user_bw.sort_values('date')
        st.line_chart(trend.set_index('date')['bodyweight_kg'])

def manage_exercises_page():
    st.header("Exercises")
    
    exercises_lib = load_exercises()
    
    tab1, tab2 = st.tabs(["View", "Add"])
    
    with tab1:
        for muscle_group, exercises in exercises_lib.items():
            with st.expander(f"{muscle_group} ({len(exercises)})"):
                for exercise in exercises:
                    st.write(f"• {exercise}")
    
    with tab2:
        new_muscle_group = st.selectbox(
            "Muscle Group", 
            list(exercises_lib.keys()) + ["+ New"]
        )
        
        if new_muscle_group == "+ New":
            new_muscle_group = st.text_input("New muscle group")
        
        new_exercise = st.text_input("Exercise name")
        
        if st.button("Add Exercise", use_container_width=True):
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

# ---------- MAIN ----------

def main():
    apply_minimal_css()
    initialize_files()
    
    st.title("Workout Tracker")
    
    profile_id = get_profile_id()
    st.markdown(f'<div class="user-badge">Profile: {profile_id}</div>', unsafe_allow_html=True)
    st.divider()
    
    page = st.radio(
        "",
        ["Log", "History", "Stats", "Monthly", "Bodyweight", "Exercises"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    if page == "Log":
        log_workout_page(profile_id)
    elif page == "History":
        view_history_page(profile_id)
    elif page == "Stats":
        statistics_page(profile_id)
    elif page == "Monthly":
        monthly_progress_page(profile_id)
    elif page == "Bodyweight":
        log_bodyweight_page(profile_id)
    elif page == "Exercises":
        manage_exercises_page()

if __name__ == "__main__":
    main()
