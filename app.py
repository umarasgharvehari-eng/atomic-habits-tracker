import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Atomic Habits Tracker",
    page_icon="⚛️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .habit-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        border-left: 5px solid #4CAF50;
    }
    .streak-fire {
        color: #ff6b35;
        font-size: 24px;
    }
    .identity-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .progress-bar {
        background-color: #e0e0e0;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
    }
    .progress-fill {
        background-color: #4CAF50;
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .quote-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        border-radius: 5px;
        font-style: italic;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Data persistence functions
def load_data():
    """Load habits data from JSON file"""
    if os.path.exists('habits_data.json'):
        with open('habits_data.json', 'r') as f:
            return json.load(f)
    return {"habits": [], "check_ins": {}}

def save_data(data):
    """Save habits data to JSON file"""
    with open('habits_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def get_today():
    """Get today's date as string"""
    return datetime.now().strftime('%Y-%m-%d')

def get_streak(habit_id, check_ins):
    """Calculate current streak for a habit"""
    if habit_id not in check_ins:
        return 0

    dates = sorted(check_ins[habit_id], reverse=True)
    if not dates:
        return 0

    streak = 0
    today = datetime.now().date()

    for i, date_str in enumerate(dates):
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        expected = today - timedelta(days=i)
        if date == expected:
            streak += 1
        else:
            break

    return streak

def get_completion_rate(habit_id, check_ins, days=30):
    """Calculate completion rate over last N days"""
    if habit_id not in check_ins:
        return 0

    today = datetime.now().date()
    completed = 0

    for i in range(days):
        check_date = today - timedelta(days=i)
        check_date_str = check_date.strftime('%Y-%m-%d')
        if check_date_str in check_ins[habit_id]:
            completed += 1

    return round((completed / days) * 100)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = False

# Sidebar navigation
st.sidebar.title("⚛️ Atomic Habits")
page = st.sidebar.radio("Navigate", ["Today's Habits", "Add New Habit", "Progress Dashboard", "About Atomic Habits"])

# Main content
if page == "Today's Habits":
    st.title("🌅 Today's Habits")
    st.markdown("*Small habits, remarkable results*")

    today = get_today()
    data = st.session_state.data

    if not data["habits"]:
        st.info("👋 No habits yet! Go to 'Add New Habit' to create your first atomic habit.")
    else:
        # Progress overview
        total_habits = len(data["habits"])
        completed_today = sum(1 for h in data["habits"] if h["id"] in data["check_ins"] and today in data["check_ins"][h["id"]])

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Habits", total_habits)
        col2.metric("Completed Today", f"{completed_today}/{total_habits}")
        col3.metric("Completion Rate", f"{round((completed_today/total_habits)*100)}%")

        st.progress(completed_today / total_habits)

        st.markdown("---")

        # Display habits
        for habit in data["habits"]:
            habit_id = habit["id"]
            is_completed = habit_id in data["check_ins"] and today in data["check_ins"][habit_id]
            streak = get_streak(habit_id, data["check_ins"])

            with st.container():
                st.markdown('<div class="habit-card">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**{habit['name']}**")
                    st.markdown(f"<span class='identity-badge'>I am {habit['identity']}</span>", unsafe_allow_html=True)
                    if habit.get('stack_trigger'):
                        st.caption(f"🔗 After: {habit['stack_trigger']}")
                    if habit.get('two_minute_version'):
                        st.caption(f"⏱️ 2-min version: {habit['two_minute_version']}")

                with col2:
                    if streak > 0:
                        st.markdown(f"<span class='streak-fire'>🔥 {streak}</span>", unsafe_allow_html=True)
                        st.caption("day streak")

                with col3:
                    if is_completed:
                        st.success("✅ Done!")
                        if st.button("Undo", key=f"undo_{habit_id}"):
                            data["check_ins"][habit_id].remove(today)
                            save_data(data)
                            st.rerun()
                    else:
                        if st.button("Complete", key=f"complete_{habit_id}"):
                            if habit_id not in data["check_ins"]:
                                data["check_ins"][habit_id] = []
                            data["check_ins"][habit_id].append(today)
                            save_data(data)
                            st.balloons()
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        # Daily reflection
        st.markdown("---")
        st.subheader("📝 Daily Reflection")
        reflection = st.text_area("What did you learn about yourself today?", placeholder="I showed up even when...")
        if st.button("Save Reflection"):
            st.success("Reflection saved! 🌟")

elif page == "Add New Habit":
    st.title("➕ Create New Atomic Habit")

    with st.form("new_habit_form"):
        st.markdown("### 🎯 Habit Details")

        name = st.text_input("Habit Name", placeholder="e.g., Exercise, Read, Meditate")

        col1, col2 = st.columns(2)
        with col1:
            two_minute = st.text_input("2-Minute Version", placeholder="e.g., Put on running shoes")
        with col2:
            identity = st.text_input("Identity Statement", placeholder="e.g., a runner, a reader")

        st.markdown("### 🔗 Habit Stacking")
        stack_trigger = st.text_input("After I... (existing habit)", placeholder="e.g., pour my morning coffee")

        st.markdown("### 🎁 Temptation Bundling (Optional)")
        reward = st.text_input("I will enjoy... while doing this habit", placeholder="e.g., listen to my favorite podcast")

        st.markdown("### 🔔 Reminder Cues")
        time_of_day = st.selectbox("Best time to perform", ["Morning", "Afternoon", "Evening", "Anytime"])

        submitted = st.form_submit_button("Create Habit", use_container_width=True)

        if submitted:
            if name and two_minute and identity:
                new_habit = {
                    "id": f"habit_{datetime.now().timestamp()}",
                    "name": name,
                    "two_minute_version": two_minute,
                    "identity": identity,
                    "stack_trigger": stack_trigger,
                    "reward": reward,
                    "time_of_day": time_of_day,
                    "created_at": get_today()
                }

                st.session_state.data["habits"].append(new_habit)
                save_data(st.session_state.data)

                st.success(f"✅ Habit '{name}' created! Remember: You don't rise to your goals, you fall to your systems.")
                st.balloons()
            else:
                st.error("Please fill in at least the name, 2-minute version, and identity.")

elif page == "Progress Dashboard":
    st.title("📊 Your Progress")

    data = st.session_state.data

    if not data["habits"]:
        st.info("No habits to track yet. Create your first habit!")
    else:
        # Overall stats
        total_checkins = sum(len(dates) for dates in data["check_ins"].values())

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Habits", len(data["habits"]))
        col2.metric("Total Check-ins", total_checkins)

        # Calculate overall consistency
        if data["habits"]:
            avg_rate = sum(get_completion_rate(h["id"], data["check_ins"]) for h in data["habits"]) / len(data["habits"])
            col3.metric("30-Day Consistency", f"{round(avg_rate)}%")

        st.markdown("---")

        # Individual habit stats
        st.subheader("🔥 Habit Streaks")

        for habit in data["habits"]:
            habit_id = habit["id"]
            streak = get_streak(habit_id, data["check_ins"])
            rate_30 = get_completion_rate(habit_id, data["check_ins"], 30)
            rate_7 = get_completion_rate(habit_id, data["check_ins"], 7)

            with st.expander(f"{habit['name']} - 🔥 {streak} days"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Streak", f"{streak} days")
                col2.metric("7-Day Rate", f"{rate_7}%")
                col3.metric("30-Day Rate", f"{rate_30}%")

                # Progress bar
                st.progress(rate_30 / 100)

                # Show identity reminder
                st.info(f"💡 Remember: You are {habit['identity']}")

                # Calendar heatmap simulation
                st.caption("Last 14 days:")
                days_cols = st.columns(14)
                today = datetime.now().date()

                for i, col in enumerate(days_cols):
                    check_date = today - timedelta(days=13-i)
                    check_date_str = check_date.strftime('%Y-%m-%d')
                    is_done = habit_id in data["check_ins"] and check_date_str in data["check_ins"][habit_id]

                    day_abbr = check_date.strftime('%a')[0]
                    if is_done:
                        col.markdown(f"<div style='text-align:center; color:green; font-weight:bold;'>{day_abbr}✓</div>", unsafe_allow_html=True)
                    else:
                        col.markdown(f"<div style='text-align:center; color:lightgray;'>{day_abbr}</div>", unsafe_allow_html=True)

        # 1% better calculation
        st.markdown("---")
        st.subheader("📈 Compound Growth")

        days_active = (datetime.now() - datetime.strptime(data["habits"][0]["created_at"], '%Y-%m-%d')).days + 1 if data["habits"] else 0
        if days_active > 0:
            improvement = (1.01 ** days_active)
            st.markdown(f"<div class='quote-box'>If you've been getting 1% better each day for {days_active} days, you're now <b>{improvement:.2f}x</b> better than when you started!</div>", unsafe_allow_html=True)

elif page == "About Atomic Habits":
    st.title("⚛️ The Atomic Habits Framework")

    st.markdown("""
    ### The Four Laws of Behavior Change

    #### 🎯 1. Make It Obvious
    - **Design your environment**: Make the cues of good habits visible
    - **Habit Stacking**: Pair a new habit with a current habit
    - **Implementation Intention**: "I will [BEHAVIOR] at [TIME] in [LOCATION]"

    #### 😍 2. Make It Attractive
    - **Temptation Bundling**: Pair an action you want to do with an action you need to do
    - **Join a culture**: Surround yourself with people who have the habits you want

    #### ✅ 3. Make It Easy
    - **The 2-Minute Rule**: When you start a new habit, it should take less than 2 minutes
    - **Reduce friction**: Decrease the number of steps between you and your good habits

    #### 🎉 4. Make It Satisfying
    - **Immediate rewards**: Give yourself an instant reward when you complete your habit
    - **Never miss twice**: If you miss one day, get back on track quickly

    ### Key Principles

    > "You do not rise to the level of your goals. You fall to the level of your systems."

    - **Focus on systems, not goals**
    - **Build identity-based habits** (focus on who you want to become)
    - **Small changes compound** (1% better each day = 37x better in a year)
    - **The Plateau of Latent Potential**: Results often come slowly, then suddenly
    """
    )

    st.markdown("---")
    st.info("💡 **Pro Tip**: Use this app daily. The goal isn't perfection—it's consistency. Never miss twice!")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")
st.sidebar.caption("Based on Atomic Habits by James Clear")
