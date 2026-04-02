import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

# Page configuration
st.set_page_config(
    page_title="Atomic Habits Tracker",
    page_icon="⚛️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, beginner-friendly styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .habit-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        margin-bottom: 15px;
        border-left: 5px solid #667eea;
        transition: transform 0.2s;
    }
    .habit-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .habit-card.completed {
        border-left-color: #4CAF50;
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
    }
    .stButton>button {
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .identity-badge {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        color: #1565c0;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
        margin-top: 5px;
    }
    .tip-box {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        font-size: 14px;
    }
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .quote-box {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 4px solid #9c27b0;
        padding: 20px;
        border-radius: 10px;
        font-style: italic;
        margin: 20px 0;
        text-align: center;
        font-size: 16px;
    }
    .empty-state {
        text-align: center;
        padding: 40px;
        background: white;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        color: #667eea;
    }
    .stat-label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .calendar-day {
        display: inline-block;
        width: 30px;
        height: 30px;
        line-height: 30px;
        text-align: center;
        border-radius: 50%;
        margin: 2px;
        font-size: 12px;
        font-weight: 600;
    }
    .calendar-day.completed {
        background-color: #4caf50;
        color: white;
    }
    .calendar-day.missed {
        background-color: #ffebee;
        color: #f44336;
    }
    .calendar-day.future {
        background-color: #f5f5f5;
        color: #9e9e9e;
    }
</style>
""", unsafe_allow_html=True)

# Data persistence functions
def load_data():
    if os.path.exists('habits_data.json'):
        try:
            with open('habits_data.json', 'r') as f:
                return json.load(f)
        except:
            return get_default_data()
    return get_default_data()

def get_default_data():
    return {
        "habits": [],
        "check_ins": {},
        "reflections": {},
        "user_settings": {
            "name": "",
            "started_date": datetime.now().strftime('%Y-%m-%d'),
            "theme": "default"
        }
    }

def save_data(data):
    with open('habits_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def get_today():
    return datetime.now().strftime('%Y-%m-%d')

def get_date_list(days=30):
    dates = []
    today = datetime.now().date()
    for i in range(days-1, -1, -1):
        date = today - timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    return dates

def get_streak(habit_id, check_ins):
    if habit_id not in check_ins or not check_ins[habit_id]:
        return 0
    dates = sorted(check_ins[habit_id], reverse=True)
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

def get_best_streak(habit_id, check_ins):
    if habit_id not in check_ins or not check_ins[habit_id]:
        return 0
    dates = sorted(check_ins[habit_id])
    if not dates:
        return 0
    best_streak = 1
    current_streak = 1
    for i in range(1, len(dates)):
        prev_date = datetime.strptime(dates[i-1], '%Y-%m-%d').date()
        curr_date = datetime.strptime(dates[i], '%Y-%m-%d').date()
        if (curr_date - prev_date).days == 1:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        elif (curr_date - prev_date).days > 1:
            current_streak = 1
    return best_streak

def get_completion_rate(habit_id, check_ins, days=30):
    if habit_id not in check_ins:
        return 0
    date_list = get_date_list(days)
    completed = sum(1 for date in date_list if date in check_ins[habit_id])
    return round((completed / days) * 100)

def get_weekly_progress(habit_id, check_ins):
    weeks = []
    today = datetime.now().date()
    for week in range(4):
        week_start = today - timedelta(days=today.weekday() + (week * 7))
        week_dates = [(week_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        completed = sum(1 for date in week_dates if habit_id in check_ins and date in check_ins[habit_id])
        weeks.append(completed)
    return list(reversed(weeks))

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()
if 'editing_habit' not in st.session_state:
    st.session_state.editing_habit = None
if 'show_delete_confirm' not in st.session_state:
    st.session_state.show_delete_confirm = None
if 'show_tips' not in st.session_state:
    st.session_state.show_tips = True
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Today's Habits"

# Sidebar
st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #667eea; margin: 0;">⚛️</h1>
    <h3 style="margin: 5px 0; color: #333;">Atomic Habits</h3>
    <p style="font-size: 12px; color: #666;">Build better habits, 1% at a time</p>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigate",
    ["🏠 Today's Habits", "➕ Add New Habit", "📊 Progress Dashboard", "⚙️ Manage Habits", "📚 Learn & Tips", "👤 My Profile"]
)

st.session_state.current_page = page

# Quick stats in sidebar
data = st.session_state.data
today = get_today()

if data["habits"]:
    total_habits = len(data["habits"])
    completed_today = sum(1 for h in data["habits"] if h["id"] in data["check_ins"] and today in data["check_ins"][h["id"]])
    total_streak = sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Today's Progress", f"{completed_today}/{total_habits}")
    st.sidebar.metric("Total Streaks", f"{total_streak} days")
    if total_habits > 0:
        avg_rate = sum(get_completion_rate(h["id"], data["check_ins"]) for h in data["habits"]) / total_habits
        st.sidebar.progress(avg_rate / 100, text=f"30-day avg: {round(avg_rate)}%")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Start with just 1-2 habits!")

# Helper functions
def show_tip(tip_text, type="info"):
    if st.session_state.show_tips:
        if type == "success":
            st.markdown(f'<div class="success-box">💡 <b>Tip:</b> {tip_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="tip-box">💡 <b>Beginner Tip:</b> {tip_text}</div>', unsafe_allow_html=True)

def habit_card(habit, is_completed, streak, on_complete, on_edit, on_delete):
    habit_id = habit["id"]
    card_class = "habit-card completed" if is_completed else "habit-card"

    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1, 2])

    with col1:
        st.markdown(f"**{habit['name']}**")
        st.markdown(f"<span class='identity-badge'>I am {habit['identity']}</span>", unsafe_allow_html=True)
        if habit.get('stack_trigger'):
            st.caption(f"🔗 After: {habit['stack_trigger']}")
        if habit.get('two_minute_version'):
            st.caption(f"⏱️ 2-min rule: {habit['two_minute_version']}")
        if habit.get('reward'):
            st.caption(f"🎁 Reward: {habit['reward']}")

    with col2:
        if streak > 0:
            st.markdown(f"<div style='text-align: center;'><span style='font-size: 28px;'>🔥</span><br><b>{streak}</b><br><small>days</small></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align: center; color: #999;'><span style='font-size: 28px;'>⚪</span><br><small>Start today!</small></div>", unsafe_allow_html=True)

    with col3:
        if is_completed:
            st.success("✅ Completed!")
            if st.button("↩️ Undo", key=f"undo_{habit_id}", help="Mark as not done"):
                on_complete(habit_id, undo=True)
        else:
            if st.button("✅ Complete", key=f"complete_{habit_id}", help="Mark as done for today"):
                on_complete(habit_id)

        edit_col, del_col = st.columns(2)
        with edit_col:
            if st.button("✏️ Edit", key=f"edit_{habit_id}", help="Edit this habit"):
                on_edit(habit_id)
        with del_col:
            if st.button("🗑️ Delete", key=f"delete_{habit_id}", help="Delete this habit"):
                on_delete(habit_id)

    st.markdown('</div>', unsafe_allow_html=True)

# Page: Today's Habits
if page == "🏠 Today's Habits":
    st.markdown('<div class="main-header"><h1>🌅 Today's Habits</h1><p>Small actions, remarkable results</p></div>', unsafe_allow_html=True)
    show_tip("Start with your easiest habit to build momentum! The 2-minute rule means making it so easy you can't say no.")

    data = st.session_state.data
    today = get_today()

    if not data["habits"]:
        st.markdown("<div class='empty-state'><h2>🎯 No habits yet!</h2><p>Let's build your first atomic habit together.</p><p>Remember: You don't need to be perfect, just consistent.</p></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Create Your First Habit", use_container_width=True):
                st.session_state.current_page = "➕ Add New Habit"
                st.rerun()
    else:
        total_habits = len(data["habits"])
        completed_today = sum(1 for h in data["habits"] if h["id"] in data["check_ins"] and today in data["check_ins"][h["id"]])
        completion_rate = round((completed_today / total_habits) * 100) if total_habits > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completed_today}</div><div class="stat-label">Done Today</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_habits - completed_today}</div><div class="stat-label">Remaining</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completion_rate}%</div><div class="stat-label">Completion</div></div>', unsafe_allow_html=True)
        with col4:
            total_streak = sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])
            st.markdown(f'<div class="stat-card"><div class="stat-number">🔥{total_streak}</div><div class="stat-label">Total Streak</div></div>', unsafe_allow_html=True)

        st.progress(completion_rate / 100)

        if completion_rate == 100:
            st.balloons()
            st.success("🎉 Amazing! You've completed all your habits today! Remember: Never miss twice!")

        st.markdown("---")

        col1, col2 = st.columns([3, 1])
        with col1:
            filter_status = st.selectbox("Filter habits:", ["All", "Completed", "Not Completed"], label_visibility="collapsed")
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()

        for habit in data["habits"]:
            habit_id = habit["id"]
            is_completed = habit_id in data["check_ins"] and today in data["check_ins"][habit_id]
            streak = get_streak(habit_id, data["check_ins"])

            if filter_status == "Completed" and not is_completed:
                continue
            if filter_status == "Not Completed" and is_completed:
                continue

            def on_complete(hid, undo=False):
                if undo:
                    if hid in data["check_ins"] and today in data["check_ins"][hid]:
                        data["check_ins"][hid].remove(today)
                else:
                    if hid not in data["check_ins"]:
                        data["check_ins"][hid] = []
                    if today not in data["check_ins"][hid]:
                        data["check_ins"][hid].append(today)
                        st.balloons()
                save_data(data)
                st.rerun()

            def on_edit(hid):
                st.session_state.editing_habit = hid
                st.session_state.current_page = "➕ Add New Habit"
                st.rerun()

            def on_delete(hid):
                st.session_state.show_delete_confirm = hid
                st.rerun()

            habit_card(habit, is_completed, streak, on_complete, on_edit, on_delete)

        if st.session_state.show_delete_confirm:
            hid = st.session_state.show_delete_confirm
            habit_name = next((h["name"] for h in data["habits"] if h["id"] == hid), "this habit")
            st.warning(f"⚠️ Are you sure you want to delete '{habit_name}'?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete", key="confirm_delete"):
                    data["habits"] = [h for h in data["habits"] if h["id"] != hid]
                    if hid in data["check_ins"]:
                        del data["check_ins"][hid]
                    save_data(data)
                    st.session_state.show_delete_confirm = None
                    st.success("Habit deleted!")
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", key="cancel_delete"):
                    st.session_state.show_delete_confirm = None
                    st.rerun()

        st.markdown("---")
        st.subheader("📝 Daily Reflection")
        show_tip("Take 30 seconds to reflect. This reinforces your identity and helps you spot patterns.", "success")

        reflection_key = f"reflection_{today}"
        current_reflection = data["reflections"].get(today, "")
        reflection = st.text_area("What went well today? What could be improved?", value=current_reflection, placeholder="I showed up even when I didn't feel like it...", key=reflection_key)

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("💾 Save Reflection"):
                data["reflections"][today] = reflection
                save_data(data)
                st.success("Reflection saved! 🌟")
        with col2:
            if data["reflections"]:
                if st.button("📖 View Past Reflections"):
                    st.session_state.current_page = "📊 Progress Dashboard"
                    st.rerun()

# Page: Add New Habit
elif page == "➕ Add New Habit":
    is_editing = st.session_state.editing_habit is not None

    if is_editing:
        st.markdown('<div class="main-header"><h1>✏️ Edit Habit</h1><p>Refine your system</p></div>', unsafe_allow_html=True)
        habit_to_edit = next((h for h in st.session_state.data["habits"] if h["id"] == st.session_state.editing_habit), None)
    else:
        st.markdown('<div class="main-header"><h1>➕ Create New Atomic Habit</h1><p>Build your system, not just goals</p></div>', unsafe_allow_html=True)
        show_tip("Start SMALL! The 2-minute rule: make it so easy you can't say no. You can always do more once you've started.")
        habit_to_edit = None

    with st.form("habit_form", clear_on_submit=not is_editing):
        st.markdown("### 🎯 What's your habit?")

        name = st.text_input("Habit Name *", value=habit_to_edit["name"] if habit_to_edit else "", placeholder="e.g., Exercise, Read, Meditate, Write")

        col1, col2 = st.columns(2)
        with col1:
            two_minute = st.text_input("2-Minute Version * (Make it easy!)", value=habit_to_edit["two_minute_version"] if habit_to_edit else "", placeholder="e.g., Put on running shoes, Read 1 page")
        with col2:
            identity = st.text_input("Identity Statement * (Who you want to become)", value=habit_to_edit["identity"] if habit_to_edit else "", placeholder="e.g., a runner, a reader, a writer")

        st.markdown("### 🔗 Habit Stacking (When & Where)")
        show_tip("Link your new habit to something you already do daily. This creates a clear cue!", "success")

        stack_trigger = st.text_input("After I... (existing daily habit)", value=habit_to_edit["stack_trigger"] if habit_to_edit else "", placeholder="e.g., pour my morning coffee, brush my teeth, sit at my desk")
        location = st.text_input("I will do this at... (specific location)", value=habit_to_edit.get("location", "") if habit_to_edit else "", placeholder="e.g., in my living room, at the park, in my office")

        st.markdown("### 🎁 Temptation Bundling (Make it attractive)")
        show_tip("Pair something you WANT to do with something you NEED to do. Only allow yourself the treat while doing the habit.", "success")

        reward = st.text_input("While doing this habit, I will enjoy...", value=habit_to_edit["reward"] if habit_to_edit else "", placeholder="e.g., listen to my favorite podcast, watch a show, drink special coffee")

        st.markdown("### ⏰ When?")
        time_options = ["Morning (6-9am)", "Late Morning (9-12pm)", "Afternoon (12-5pm)", "Evening (5-9pm)", "Anytime", "Specific Time"]
        time_of_day = st.selectbox("Best time to perform", time_options, index=time_options.index(habit_to_edit["time_of_day"]) if habit_to_edit and habit_to_edit["time_of_day"] in time_options else 0)

        st.markdown("### 🔔 Reminder Settings")
        col1, col2 = st.columns(2)
        with col1:
            reminder_enabled = st.checkbox("Enable daily reminder", value=habit_to_edit.get("reminder_enabled", True) if habit_to_edit else True)
        with col2:
            weekend_skip = st.checkbox("Skip weekends", value=habit_to_edit.get("weekend_skip", False) if habit_to_edit else False)

        submit_label = "💾 Update Habit" if is_editing else "➕ Create Habit"
        submitted = st.form_submit_button(submit_label, use_container_width=True)

        if submitted:
            if name and two_minute and identity:
                if is_editing and habit_to_edit:
                    habit_to_edit["name"] = name
                    habit_to_edit["two_minute_version"] = two_minute
                    habit_to_edit["identity"] = identity
                    habit_to_edit["stack_trigger"] = stack_trigger
                    habit_to_edit["location"] = location
                    habit_to_edit["reward"] = reward
                    habit_to_edit["time_of_day"] = time_of_day
                    habit_to_edit["reminder_enabled"] = reminder_enabled
                    habit_to_edit["weekend_skip"] = weekend_skip
                    habit_to_edit["updated_at"] = get_today()
                    st.session_state.editing_habit = None
                    save_data(st.session_state.data)
                    st.success(f"✅ Habit '{name}' updated successfully!")
                else:
                    new_habit = {
                        "id": f"habit_{int(datetime.now().timestamp())}_{len(st.session_state.data['habits'])}",
                        "name": name,
                        "two_minute_version": two_minute,
                        "identity": identity,
                        "stack_trigger": stack_trigger,
                        "location": location,
                        "reward": reward,
                        "time_of_day": time_of_day,
                        "reminder_enabled": reminder_enabled,
                        "weekend_skip": weekend_skip,
                        "created_at": get_today(),
                        "updated_at": get_today()
                    }
                    st.session_state.data["habits"].append(new_habit)
                    save_data(st.session_state.data)
                    st.success(f"🎉 Habit '{name}' created! Remember: You don't rise to your goals, you fall to your systems.")
                    st.balloons()
                    st.info("💡 **Next Step:** Go to 'Today's Habits' and complete your first check-in!")
            else:
                st.error("⚠️ Please fill in all required fields (marked with *)")

    if is_editing:
        st.markdown("---")
        if st.button("❌ Cancel Editing"):
            st.session_state.editing_habit = None
            st.rerun()

# Page: Progress Dashboard
elif page == "📊 Progress Dashboard":
    st.markdown('<div class="main-header"><h1>📊 Your Progress</h1><p>Track your compound growth</p></div>', unsafe_allow_html=True)
    show_tip("Focus on your system, not your goals. A 1% improvement each day compounds to being 37x better in a year!")

    data = st.session_state.data

    if not data["habits"]:
        st.info("👋 No habits to track yet. Create your first habit to see your progress!")
        if st.button("➕ Create First Habit"):
            st.session_state.current_page = "➕ Add New Habit"
            st.rerun()
    else:
        total_checkins = sum(len(dates) for dates in data["check_ins"].values())
        active_habits = len(data["habits"])
        total_streak = sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])
        avg_rate = sum(get_completion_rate(h["id"], data["check_ins"]) for h in data["habits"]) / active_habits if active_habits > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{active_habits}</div><div class="stat-label">Active Habits</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_checkins}</div><div class="stat-label">Total Check-ins</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_streak}</div><div class="stat-label">Current Streaks</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{round(avg_rate)}%</div><div class="stat-label">30-Day Consistency</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🔥 Individual Habit Stats")

        for habit in data["habits"]:
            habit_id = habit["id"]
            streak = get_streak(habit_id, data["check_ins"])
            best_streak = get_best_streak(habit_id, data["check_ins"])
            rate_30 = get_completion_rate(habit_id, data["check_ins"], 30)
            rate_7 = get_completion_rate(habit_id, data["check_ins"], 7)
            total_done = len(data["check_ins"].get(habit_id, []))

            with st.expander(f"📈 {habit['name']} - 🔥 {streak} days (Best: {best_streak})"):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Current Streak", f"{streak} days")
                m2.metric("Best Streak", f"{best_streak} days")
                m3.metric("7-Day Rate", f"{rate_7}%")
                m4.metric("30-Day Rate", f"{rate_30}%")

                st.progress(rate_30 / 100, text=f"30-day completion: {rate_30}%")
                st.info(f"💡 **Identity:** You are {habit['identity']}")

                st.caption("Last 4 weeks:")
                weekly_data = get_weekly_progress(habit_id, data["check_ins"])
                week_labels = ["This Week", "Last Week", "2 Weeks Ago", "3 Weeks Ago"]
                for week, label in zip(weekly_data, week_labels):
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.caption(label)
                    with col2:
                        st.progress(week / 7, text=f"{week}/7 days")

                st.caption("Last 14 days:")
                days_cols = st.columns(14)
                today_dt = datetime.now().date()
                for i, col in enumerate(days_cols):
                    check_date = today_dt - timedelta(days=13-i)
                    check_date_str = check_date.strftime('%Y-%m-%d')
                    is_done = habit_id in data["check_ins"] and check_date_str in data["check_ins"][habit_id]
                    day_abbr = check_date.strftime('%a')[0]
                    if is_done:
                        col.markdown(f"<div class='calendar-day completed'>{day_abbr}</div>", unsafe_allow_html=True)
                    elif check_date < today_dt:
                        col.markdown(f"<div class='calendar-day missed'>{day_abbr}</div>", unsafe_allow_html=True)
                    else:
                        col.markdown(f"<div class='calendar-day future'>{day_abbr}</div>", unsafe_allow_html=True)

                st.markdown("---")
                edit_col, del_col = st.columns(2)
                with edit_col:
                    if st.button(f"✏️ Edit {habit['name']}", key=f"dash_edit_{habit_id}"):
                        st.session_state.editing_habit = habit_id
                        st.session_state.current_page = "➕ Add New Habit"
                        st.rerun()
                with del_col:
                    if st.button(f"🗑️ Delete {habit['name']}", key=f"dash_delete_{habit_id}"):
                        st.session_state.show_delete_confirm = habit_id
                        st.rerun()

        st.markdown("---")
        st.subheader("📈 Compound Growth Calculator")

        if data["habits"]:
            earliest_date = min(datetime.strptime(h["created_at"], '%Y-%m-%d') for h in data["habits"])
            days_active = (datetime.now() - earliest_date).days + 1
            improvement = (1.01 ** days_active)

            st.markdown(f'<div class="quote-box"><h3>🎯 The Math of Small Wins</h3><p>If you've been getting <b>1% better</b> each day for <b>{days_active} days</b>...</p><h2>You are now <span style="color: #667eea;">{improvement:.2f}x</span> better than when you started!</h2><p><small>1% daily improvement = 37x yearly improvement</small></p></div>', unsafe_allow_html=True)

        if data["reflections"]:
            st.markdown("---")
            st.subheader("📖 Past Reflections")
            sorted_reflections = sorted(data["reflections"].items(), key=lambda x: x[0], reverse=True)
            for date, reflection in sorted_reflections[:10]:
                with st.expander(f"📝 {date}"):
                    st.write(reflection)
                    if st.button("🗑️ Delete", key=f"del_ref_{date}"):
                        del data["reflections"][date]
                        save_data(data)
                        st.rerun()

# Page: Manage Habits
elif page == "⚙️ Manage Habits":
    st.markdown('<div class="main-header"><h1>⚙️ Manage Your Habits</h1><p>Edit, delete, or reorganize</p></div>', unsafe_allow_html=True)
    show_tip("It's better to have fewer consistent habits than many inconsistent ones. Don't be afraid to remove habits that don't serve you.")

    data = st.session_state.data

    if not data["habits"]:
        st.info("No habits to manage yet.")
    else:
        st.subheader(f"You have {len(data['habits'])} habits")

        for i, habit in enumerate(data["habits"]):
            with st.container():
                st.markdown(f'<div class="habit-card">', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([3, 2, 2])

                with col1:
                    st.markdown(f"**{i+1}. {habit['name']}**")
                    st.caption(f"Created: {habit['created_at']}")
                    st.markdown(f"<span class='identity-badge'>{habit['identity']}</span>", unsafe_allow_html=True)

                with col2:
                    streak = get_streak(habit["id"], data["check_ins"])
                    total_done = len(data["check_ins"].get(habit["id"], []))
                    st.metric("Current Streak", f"{streak} days")
                    st.caption(f"Total completed: {total_done}")

                with col3:
                    if i > 0:
                        if st.button("⬆️ Up", key=f"up_{habit['id']}"):
                            data["habits"][i], data["habits"][i-1] = data["habits"][i-1], data["habits"][i]
                            save_data(data)
                            st.rerun()
                    if i < len(data["habits"]) - 1:
                        if st.button("⬇️ Down", key=f"down_{habit['id']}"):
                            data["habits"][i], data["habits"][i+1] = data["habits"][i+1], data["habits"][i]
                            save_data(data)
                            st.rerun()
                    if st.button("✏️ Edit", key=f"manage_edit_{habit['id']}"):
                        st.session_state.editing_habit = habit["id"]
                        st.session_state.current_page = "➕ Add New Habit"
                        st.rerun()
                    if st.button("🗑️ Delete", key=f"manage_delete_{habit['id']}"):
                        st.session_state.show_delete_confirm = habit["id"]
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("⚡ Bulk Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Delete All Habits", use_container_width=True):
                st.warning("⚠️ This will delete ALL habits and data. This cannot be undone!")
                confirm = st.checkbox("I understand this will delete everything")
                if confirm and st.button("Confirm Delete All"):
                    st.session_state.data = get_default_data()
                    save_data(st.session_state.data)
                    st.success("All data cleared!")
                    st.rerun()
        with col2:
            if st.button("📥 Export Data", use_container_width=True):
                json_str = json.dumps(data, indent=2)
                st.download_button(label="Download JSON", data=json_str, file_name="atomic_habits_backup.json", mime="application/json")

# Page: Learn & Tips
elif page == "📚 Learn & Tips":
    st.markdown('<div class="main-header"><h1>📚 Learn Atomic Habits</h1><p>Master the framework</p></div>', unsafe_allow_html=True)

    show_tips_setting = st.checkbox("Show beginner tips throughout the app", value=st.session_state.show_tips)
    st.session_state.show_tips = show_tips_setting

    st.markdown("---")
    st.subheader("⚖️ The Four Laws of Behavior Change")

    laws = [
        ("🎯 1. Make It Obvious", ["Design your environment", "Use habit stacking", "Implementation intentions"], ["Hide cues of bad habits"]),
        ("😍 2. Make It Attractive", ["Temptation bundling", "Join supportive cultures", "Create motivation rituals"], ["Reframe bad habits as unattractive"]),
        ("✅ 3. Make It Easy", ["The 2-Minute Rule", "Reduce friction", "Prime your environment"], ["Increase friction for bad habits"]),
        ("🎉 4. Make It Satisfying", ["Immediate rewards", "Habit tracking", "Never miss twice"], ["Make bad habits unsatisfying"])
    ]

    for law in laws:
        with st.expander(law[0]):
            st.markdown("**For Good Habits:**")
            for item in law[1]:
                st.markdown(f"- ✅ {item}")
            st.markdown("**For Bad Habits:**")
            for item in law[2]:
                st.markdown(f"- ❌ {item}")

    st.markdown("---")
    st.subheader("🧠 Key Principles")

    principles = [
        ("🎯 Identity-Based Habits", "Focus on who you want to become, not what you want to achieve. Every action you take is a vote for the type of person you wish to become."),
        ("📈 The 1% Rule", "If you get 1% better each day for one year, you'll end up 37 times better. Small changes compound into remarkable results."),
        ("⏱️ The 2-Minute Rule", "When you start a new habit, it should take less than two minutes to do. Make it so easy you can't say no."),
        ("🔗 Habit Stacking", "Pair a new habit with a current habit. 'After [CURRENT HABIT], I will [NEW HABIT].'"),
        ("🎁 Temptation Bundling", "Pair an action you want to do with an action you need to do."),
        ("📊 Never Miss Twice", "Missing once is a mistake. Missing twice is the start of a new habit. Get back on track immediately."),
        ("🏛️ Environment Design", "You don't have to be the victim of your environment. You can also be the architect of it."),
        ("🔄 Systems vs Goals", "You do not rise to the level of your goals. You fall to the level of your systems.")
    ]

    for title, desc in principles:
        st.markdown(f"**{title}**")
        st.caption(desc)
        st.markdown("")

    st.markdown("---")
    st.subheader("💬 Inspirational Quotes")

    quotes = [
        "Success is the product of daily habits—not once-in-a-lifetime transformations.",
        "You do not rise to the level of your goals. You fall to the level of your systems.",
        "Every action you take is a vote for the type of person you wish to become.",
        "Habits are the compound interest of self-improvement.",
        "Time magnifies the margin between success and failure. It will multiply whatever you feed it."
    ]

    for quote in quotes:
        st.markdown(f'<div class="quote-box">"{quote}"</div>', unsafe_allow_html=True)

# Page: My Profile
elif page == "👤 My Profile":
    st.markdown('<div class="main-header"><h1>👤 My Profile</h1><p>Your identity and settings</p></div>', unsafe_allow_html=True)

    data = st.session_state.data

    with st.form("profile_form"):
        st.subheader("📝 Your Information")
        name = st.text_input("Your Name", value=data["user_settings"].get("name", ""), placeholder="What should we call you?")

        st.markdown("---")
        st.subheader("🎯 Your Identity Statements")
        if data["habits"]:
            st.markdown("**Current identities you're building:**")
            for habit in data["habits"]:
                st.markdown(f"- I am {habit['identity']} (via {habit['name']})")
        else:
            st.info("Create habits to define your identities!")

        st.markdown("---")
        st.subheader("⚙️ App Settings")
        show_tips = st.checkbox("Show beginner tips", value=data["user_settings"].get("show_tips", True))

        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Profile", use_container_width=True):
                data["user_settings"]["name"] = name
                data["user_settings"]["show_tips"] = show_tips
                save_data(data)
                st.success("Profile saved!")
        with col2:
            if st.form_submit_button("🔄 Reset All Data", use_container_width=True):
                st.warning("⚠️ This will delete ALL your habits and progress!")
                st.session_state.data = get_default_data()
                save_data(st.session_state.data)
                st.success("All data reset!")
                st.rerun()

    st.markdown("---")
    st.subheader("📊 Your Journey Summary")
    if data["habits"]:
        start_date = datetime.strptime(data["user_settings"]["started_date"], '%Y-%m-%d')
        days_journey = (datetime.now() - start_date).days + 1
        total_checkins = sum(len(dates) for dates in data["check_ins"].values())
        st.markdown(f'<div style="background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"><h4>🎯 Journey Stats</h4><p><b>Started:</b> {start_date.strftime("%B %d, %Y")} ({days_journey} days ago)</p><p><b>Total Habits Created:</b> {len(data["habits"])}</p><p><b>Total Check-ins:</b> {total_checkins}</p><p><b>Current Streaks:</b> {sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])} days combined</p></div>', unsafe_allow_html=True)
    else:
        st.info("Start your journey by creating your first habit!")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")
st.sidebar.caption("Based on Atomic Habits by James Clear")

if st.sidebar.button("❓ Need Help?"):
    st.session_state.current_page = "📚 Learn & Tips"
    st.rerun()
