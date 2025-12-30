import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import calendar

# Page configuration
st.set_page_config(
    page_title="Workout Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
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
    
    /* Mobile-optimized spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Larger touch targets for mobile */
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
    
    /* Mobile-friendly headers */
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
    
    /* Larger inputs for mobile */
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
    
    /* Compact metrics for mobile */
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
    
    /* Mobile-optimized sidebar */
    [data-testid="stSidebar"] {
        background-color: #fafafa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Better mobile dataframe */
    [data-testid="stDataFrame"] {
        font-size: 13px;
    }
    
    /* Touch-friendly radio buttons */
    .stRadio > div {
        gap: 12px;
    }
    
    .stRadio label {
        padding: 10px 16px;
        font-size: 15px;
    }
    
    /* Alerts */
    .stSuccess, .stInfo, .stWarning, .stError {
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 15px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 14px 20px;
        font-size: 15px;
        font-weight: 500;
        color: #6a6a6a;
        border: none;
        min-height: 48px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1a1a1a;
        border-bottom: 2px solid #1a1a1a;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 1px solid #e0e0e0;
    }
    
    /* Monthly calendar cards */
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
    
    /* User badge styling */
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

# File paths
WORKOUTS_FILE = "workouts_log.csv"
EXERCISES_FILE = "exercises_library.json"
USERS_FILE = "users.json"

DEFAULT_EXERCISES = {
    "Chest": ["Bench Press", "Incline Dumbbell Press", "Chest Fly", "Push-ups"],
    "Back": ["Pull-ups", "Deadlift", "Barbell Row", "Lat Pulldown"],
    "Shoulders": ["Overhead Press", "Lateral Raise", "Front Raise", "Face Pull"],
    "Legs": ["Squat", "Leg Press", "Lunges", "Leg Curl", "Calf Raise"],
    "Arms": ["Bicep Curl", "Tricep Extension", "Hammer Curl", "Tricep Dips"],
    "Core": ["Plank", "Crunches", "Leg Raises", "Russian Twist"]
}

def load_users():
    """Load user credentials"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users_dict):
    """Save user credentials"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_dict, f)

def authenticate_user():
    """Handle user login and registration"""
    
    if "authenticated_user" in st.session_state and st.session_state.authenticated_user:
        return st.session_state.authenticated_user
    
    users = load_users()
    
    st.title("Workout Tracker")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if username in users and users[username] == password:
                st.session_state.authenticated_user = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Create Account")
        new_username = st.text_input("Choose Username", key="signup_username")
        new_password = st.text_input("Choose Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Sign Up", use_container_width=True):
            if not new_username or not new_password:
                st.error("Please fill all fields")
            elif new_username in users:
                st.error("Username already exists")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            elif len(new_password) < 4:
                st.error("Password must be at least 4 characters")
            else:
                users[new_username] = new_password
                save_users(users)
                st.success("Account created! Please login")
    
    st.stop()

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

def get_monthly_stats(df, username=None):
    """Calculate monthly statistics"""
    if df.empty:
        return []
    
    if username:
        df = df[df['user'] == username]
    
    if df.empty:
        return []
    
    # Group by year-month
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

def main():
    apply_minimal_css()
    
    # Authenticate user first
    current_user = authenticate_user()
    
    initialize_files()
    
    # Title with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Workout Tracker")
        st.markdown(f'<div class="user-badge">Logged in as: {current_user}</div>', unsafe_allow_html=True)
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated_user = None
            st.rerun()
    
    st.divider()
    
    # Main navigation
    page = st.radio("", ["Log", "History", "Stats", "Monthly", "Exercises"], 
                   horizontal=True, label_visibility="collapsed")
    
    if page == "Log":
        log_workout_page(current_user)
    elif page == "History":
        view_history_page(current_user)
    elif page == "Stats":
        statistics_page(current_user)
    elif page == "Monthly":
        monthly_progress_page(current_user)
    elif page == "Exercises":
        manage_exercises_page()

def log_workout_page(username):
    st.header("Log Workout")
    
    exercises_lib = load_exercises()
    
    # Stacked layout for mobile
    workout_date = st.date_input("Date", value=datetime.now())
    workout_time = st.time_input("Time", value=datetime.now().time())
    muscle_group = st.selectbox("Muscle Group", list(exercises_lib.keys()))
    exercise = st.selectbox("Exercise", exercises_lib[muscle_group])
    
    # Number inputs in two columns to save space
    col1, col2 = st.columns(2)
    with col1:
        sets = st.number_input("Sets", min_value=1, max_value=10, value=3)
        reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
    with col2:
        weight = st.number_input("Weight (kg)", min_value=0.0, step=2.5, value=0.0)
    
    notes = st.text_area("Notes", placeholder="Optional notes", height=80)
    
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
    st.header("History")
    
    df = load_workouts()
    
    if df.empty:
        st.info("No workouts logged yet")
        return
    
    # Only show current user's workouts
    df = df[df['user'] == username]
    
    if df.empty:
        st.info("No workouts found")
        return
    
    # Filters - stacked for mobile
    exercises_lib = load_exercises()
    muscle_filter = st.selectbox("Muscle group", ["All"] + list(exercises_lib.keys()))
    days_back = st.selectbox("Period", ["7 Days", "30 Days", "90 Days", "All"])
    
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
        
        # Mobile-optimized display
        display_df = filtered_df[['date', 'exercise', 'sets', 'reps', 'weight']].head(20).copy()
        display_df['date'] = display_df['date'].dt.strftime('%m/%d')
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        csv = filtered_df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name=f"workouts_{datetime.now().strftime('%Y%m%d')}.csv", 
                          mime="text/csv", use_container_width=True)

def statistics_page(username):
    st.header("Stats")
    
    df = load_workouts()
    
    if df.empty:
        st.info("No data available")
        return
    
    # Only show current user's stats
    df = df[df['user'] == username]
    
    if df.empty:
        st.info("No workouts found")
        return
    
    # Compact metrics for mobile - 2x2 grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Workouts", len(df))
        st.metric("Volume (kg)", f"{(df['sets'] * df['reps'] * df['weight']).sum():,.0f}")
    with col2:
        st.metric("Sets", int(df['sets'].sum()))
        st.metric("Exercises", df['exercise'].nunique())
    
    st.divider()
    
    # Top exercises
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
        # Weight progress
        st.write("Weight Progress")
        weight_progress = exercise_df.groupby('date')['weight'].max()
        st.line_chart(weight_progress)
        
        max_weight = exercise_df['weight'].max()
        st.metric("PR", f"{max_weight} kg")
        
        # Recent sessions
        st.write("Recent")
        recent = exercise_df[['date', 'sets', 'reps', 'weight']].tail(5).sort_values('date', ascending=False)
        recent['date'] = recent['date'].dt.strftime('%m/%d')
        st.dataframe(recent, use_container_width=True, hide_index=True)

def monthly_progress_page(username):
    st.header("Monthly Progress")
    
    df = load_workouts()
    
    if df.empty:
        st.info("No data available")
        return
    
    monthly_stats = get_monthly_stats(df, username)
    
    if not monthly_stats:
        st.info("No workouts found")
        return
    
    # Current month summary
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
    
    # Monthly comparison
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
    
    # Monthly trend chart
    st.divider()
    st.subheader("Workout Trend")
    
    chart_data = pd.DataFrame([
        {'Month': stat['month_name'][:3], 'Workouts': stat['workouts']} 
        for stat in reversed(monthly_stats[-6:])
    ])
    
    st.bar_chart(chart_data.set_index('Month'))

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
        new_muscle_group = st.selectbox("Muscle Group", 
                                         list(exercises_lib.keys()) + ["+ New"])
        
        if new_muscle_group == "+ New":
            new_muscle_group = st.text_input("New muscle group")
        
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
