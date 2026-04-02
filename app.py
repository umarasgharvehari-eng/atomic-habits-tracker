from pathlib import Path

clean_app = r'''import streamlit as st
import json
import os
from datetime import datetime, timedelta

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

DATA_FILE = "habits_data.json"


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def get_default_data():
    return {
        "habits": [],
        "check_ins": {},
        "reflections": {},
        "user_settings": {
            "name": "",
            "started_date": get_today(),
            "theme": "default",
            "show_tips": True
        }
    }


def normalize_data(data):
    default_data = get_default_data()

    if not isinstance(data, dict):
        data = {}

    normalized = {
        "habits": data.get("habits", default_data["habits"]),
        "check_ins": data.get("check_ins", default_data["check_ins"]),
        "reflections": data.get("reflections", default_data["reflections"]),
        "user_settings": data.get("user_settings", default_data["user_settings"]),
    }

    if not isinstance(normalized["habits"], list):
        normalized["habits"] = []

    if not isinstance(normalized["check_ins"], dict):
        normalized["check_ins"] = {}

    if not isinstance(normalized["reflections"], dict):
        normalized["reflections"] = {}

    if not isinstance(normalized["user_settings"], dict):
        normalized["user_settings"] = {}

    for key, value in default_data["user_settings"].items():
        normalized["user_settings"].setdefault(key, value)

    for i, habit in enumerate(normalized["habits"]):
        if not isinstance(habit, dict):
            normalized["habits"][i] = {
                "id": f"habit_{i}_{int(datetime.now().timestamp())}",
                "name": "Untitled Habit",
                "two_minute_version": "",
                "identity": "someone who shows up",
                "stack_trigger": "",
                "location": "",
                "reward": "",
                "time_of_day": "Morning (6-9am)",
                "reminder_enabled": True,
                "weekend_skip": False,
                "created_at": get_today(),
                "updated_at": get_today(),
            }
            habit = normalized["habits"][i]

        habit.setdefault("id", f"habit_{i}_{int(datetime.now().timestamp())}")
        habit.setdefault("name", "Untitled Habit")
        habit.setdefault("two_minute_version", "")
        habit.setdefault("identity", "someone who shows up")
        habit.setdefault("stack_trigger", "")
        habit.setdefault("location", "")
        habit.setdefault("reward", "")
        habit.setdefault("time_of_day", "Morning (6-9am)")
        habit.setdefault("reminder_enabled", True)
        habit.setdefault("weekend_skip", False)
        habit.setdefault("created_at", get_today())
        habit.setdefault("updated_at", get_today())

    return normalized


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return normalize_data(json.load(f))
        except Exception:
            return get_default_data()
    return get_default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(normalize_data(data), f, indent=2)


def get_date_list(days=30):
    dates = []
    today = datetime.now().date()
    for i in range(days - 1, -1, -1):
        dates.append((today - timedelta(days=i)).strftime("%Y-%m-%d"))
    return dates


def get_streak(habit_id, check_ins):
    habit_dates = sorted(set(check_ins.get(habit_id, [])), reverse=True)
    if not habit_dates:
        return 0

    streak = 0
    today = datetime.now().date()
    for i, date_str in enumerate(habit_dates):
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if date == today - timedelta(days=i):
            streak += 1
        else:
            break
    return streak


def get_best_streak(habit_id, check_ins):
    dates = sorted(set(check_ins.get(habit_id, [])))
    if not dates:
        return 0

    best_streak = 1
    current_streak = 1
    for i in range(1, len(dates)):
        prev_date = datetime.strptime(dates[i - 1], "%Y-%m-%d").date()
        curr_date = datetime.strptime(dates[i], "%Y-%m-%d").date()
        if (curr_date - prev_date).days == 1:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        elif (curr_date - prev_date).days > 1:
            current_streak = 1
    return best_streak


def get_completion_rate(habit_id, check_ins, days=30):
    habit_dates = set(check_ins.get(habit_id, []))
    if not habit_dates:
        return 0
    date_list = get_date_list(days)
    completed = sum(1 for date in date_list if date in habit_dates)
    return round((completed / days) * 100)


def get_weekly_progress(habit_id, check_ins):
    weeks = []
    today = datetime.now().date()
    habit_dates = set(check_ins.get(habit_id, []))
    for week in range(4):
        week_start = today - timedelta(days=today.weekday() + (week * 7))
        week_dates = [(week_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        completed = sum(1 for date in week_dates if date in habit_dates)
        weeks.append(completed)
    return list(reversed(weeks))


if "data" not in st.session_state:
    st.session_state.data = load_data()
else:
    st.session_state.data = normalize_data(st.session_state.data)

if "editing_habit" not in st.session_state:
    st.session_state.editing_habit = None
if "show_delete_confirm" not in st.session_state:
    st.session_state.show_delete_confirm = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Today's Habits"

st.session_state.show_tips = st.session_state.data.get("user_settings", {}).get("show_tips", True)

st.sidebar.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #667eea; margin: 0;">⚛️</h1>
    <h3 style="margin: 5px 0; color: #333;">Atomic Habits</h3>
    <p style="font-size: 12px; color: #666;">Build better habits, 1% at a time</p>
</div>
""", unsafe_allow_html=True)

pages = [
    "🏠 Today's Habits",
    "➕ Add New Habit",
    "📊 Progress Dashboard",
    "⚙️ Manage Habits",
    "📚 Learn & Tips",
    "👤 My Profile",
]
default_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
page = st.sidebar.radio("Navigate", pages, index=default_index)
st.session_state.current_page = page

data = normalize_data(st.session_state.data)
st.session_state.data = data
today = get_today()

if data.get("habits"):
    total_habits = len(data["habits"])
    completed_today = sum(
        1 for h in data["habits"]
        if h["id"] in data["check_ins"] and today in data["check_ins"][h["id"]]
    )
    total_streak = sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Quick Stats")
    st.sidebar.metric("Today's Progress", f"{completed_today}/{total_habits}")
    st.sidebar.metric("Total Streaks", f"{total_streak} days")
    avg_rate = sum(get_completion_rate(h["id"], data["check_ins"]) for h in data["habits"]) / total_habits
    st.sidebar.progress(avg_rate / 100, text=f"30-day avg: {round(avg_rate)}%")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Start with just 1-2 habits!")


def show_tip(tip_text, tip_type="info"):
    if st.session_state.show_tips:
        if tip_type == "success":
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
        if habit.get("stack_trigger"):
            st.caption(f"🔗 After: {habit['stack_trigger']}")
        if habit.get("two_minute_version"):
            st.caption(f"⏱️ 2-min rule: {habit['two_minute_version']}")
        if habit.get("reward"):
            st.caption(f"🎁 Reward: {habit['reward']}")

    with col2:
        if streak > 0:
            st.markdown(
                f"<div style='text-align: center;'><span style='font-size: 28px;'>🔥</span><br><b>{streak}</b><br><small>days</small></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='text-align: center; color: #999;'><span style='font-size: 28px;'>⚪</span><br><small>Start today!</small></div>",
                unsafe_allow_html=True
            )

    with col3:
        if is_completed:
            st.success("✅ Completed!")
            if st.button("↩️ Undo", key=f"undo_{habit_id}"):
                on_complete(habit_id, undo=True)
        else:
            if st.button("✅ Complete", key=f"complete_{habit_id}"):
                on_complete(habit_id)

        edit_col, del_col = st.columns(2)
        with edit_col:
            if st.button("✏️ Edit", key=f"edit_{habit_id}"):
                on_edit(habit_id)
        with del_col:
            if st.button("🗑️ Delete", key=f"delete_{habit_id}"):
                on_delete(habit_id)

    st.markdown("</div>", unsafe_allow_html=True)


if page == "🏠 Today's Habits":
    st.markdown("""
    <div class="main-header">
        <h1>🌅 Today&#39;s Habits</h1>
        <p>Small actions, remarkable results</p>
    </div>
    """, unsafe_allow_html=True)

    show_tip("Start with your easiest habit to build momentum! The 2-minute rule means making it so easy you can not say no.")
    data = st.session_state.data
    today = get_today()

    if not data.get("habits"):
        st.markdown("""
        <div class="empty-state">
            <h2>🎯 No habits yet!</h2>
            <p>Let&#39;s build your first atomic habit together.</p>
            <p>Remember: You don&#39;t need to be perfect, just consistent.</p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("➕ Create Your First Habit", use_container_width=True):
                st.session_state.current_page = "➕ Add New Habit"
                st.rerun()
    else:
        total_habits = len(data["habits"])
        completed_today = sum(
            1 for h in data["habits"]
            if h["id"] in data["check_ins"] and today in data["check_ins"][h["id"]]
        )
        completion_rate = round((completed_today / total_habits) * 100) if total_habits else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completed_today}</div><div class="stat-label">Done Today</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_habits - completed_today}</div><div class="stat-label">Remaining</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completion_rate}%</div><div class="stat-label">Completion</div></div>', unsafe_allow_html=True)
        with c4:
            total_streak = sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])
            st.markdown(f'<div class="stat-card"><div class="stat-number">🔥{total_streak}</div><div class="stat-label">Total Streak</div></div>', unsafe_allow_html=True)

        st.progress(completion_rate / 100)

        st.markdown("---")
        c1, c2 = st.columns([3, 1])
        with c1:
            filter_status = st.selectbox("Filter habits:", ["All", "Completed", "Not Completed"], label_visibility="collapsed")
        with c2:
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
                app_data = st.session_state.data
                if undo:
                    if hid in app_data["check_ins"] and today in app_data["check_ins"][hid]:
                        app_data["check_ins"][hid].remove(today)
                else:
                    app_data["check_ins"].setdefault(hid, [])
                    if today not in app_data["check_ins"][hid]:
                        app_data["check_ins"][hid].append(today)
                save_data(app_data)
                st.session_state.data = normalize_data(app_data)
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
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes, Delete", key="confirm_delete"):
                    data["habits"] = [h for h in data["habits"] if h["id"] != hid]
                    data["check_ins"].pop(hid, None)
                    save_data(data)
                    st.session_state.data = normalize_data(data)
                    st.session_state.show_delete_confirm = None
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", key="cancel_delete"):
                    st.session_state.show_delete_confirm = None
                    st.rerun()

        st.markdown("---")
        st.subheader("📝 Daily Reflection")
        show_tip("Take 30 seconds to reflect. This reinforces your identity and helps you spot patterns.", "success")

        current_reflection = data.get("reflections", {}).get(today, "")
        reflection = st.text_area(
            "What went well today? What could be improved?",
            value=current_reflection,
            placeholder="I showed up even when I did not feel like it..."
        )

        c1, c2 = st.columns([1, 3])
        with c1:
            if st.button("💾 Save Reflection"):
                st.session_state.data["reflections"][today] = reflection
                save_data(st.session_state.data)
                st.success("Reflection saved! 🌟")
        with c2:
            if data.get("reflections") and st.button("📖 View Past Reflections"):
                st.session_state.current_page = "📊 Progress Dashboard"
                st.rerun()

elif page == "➕ Add New Habit":
    is_editing = st.session_state.editing_habit is not None
    habit_to_edit = next((h for h in st.session_state.data["habits"] if h["id"] == st.session_state.editing_habit), None) if is_editing else None

    st.markdown(f"""
    <div class="main-header">
        <h1>{"✏️ Edit Habit" if is_editing else "➕ Create New Atomic Habit"}</h1>
        <p>{"Refine your system" if is_editing else "Build your system, not just goals"}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("habit_form", clear_on_submit=not is_editing):
        name = st.text_input("Habit Name *", value=habit_to_edit["name"] if habit_to_edit else "")
        c1, c2 = st.columns(2)
        with c1:
            two_minute = st.text_input("2-Minute Version *", value=habit_to_edit["two_minute_version"] if habit_to_edit else "")
        with c2:
            identity = st.text_input("Identity Statement *", value=habit_to_edit["identity"] if habit_to_edit else "")
        stack_trigger = st.text_input("After I...", value=habit_to_edit["stack_trigger"] if habit_to_edit else "")
        location = st.text_input("Location", value=habit_to_edit.get("location", "") if habit_to_edit else "")
        reward = st.text_input("Reward", value=habit_to_edit["reward"] if habit_to_edit else "")
        time_options = ["Morning (6-9am)", "Late Morning (9-12pm)", "Afternoon (12-5pm)", "Evening (5-9pm)", "Anytime", "Specific Time"]
        time_of_day = st.selectbox(
            "Best time to perform",
            time_options,
            index=time_options.index(habit_to_edit["time_of_day"]) if habit_to_edit and habit_to_edit["time_of_day"] in time_options else 0
        )
        c1, c2 = st.columns(2)
        with c1:
            reminder_enabled = st.checkbox("Enable daily reminder", value=habit_to_edit.get("reminder_enabled", True) if habit_to_edit else True)
        with c2:
            weekend_skip = st.checkbox("Skip weekends", value=habit_to_edit.get("weekend_skip", False) if habit_to_edit else False)

        submitted = st.form_submit_button("💾 Update Habit" if is_editing else "➕ Create Habit", use_container_width=True)

        if submitted:
            if not (name and two_minute and identity):
                st.error("⚠️ Please fill in all required fields.")
            elif is_editing and habit_to_edit:
                habit_to_edit.update({
                    "name": name,
                    "two_minute_version": two_minute,
                    "identity": identity,
                    "stack_trigger": stack_trigger,
                    "location": location,
                    "reward": reward,
                    "time_of_day": time_of_day,
                    "reminder_enabled": reminder_enabled,
                    "weekend_skip": weekend_skip,
                    "updated_at": get_today(),
                })
                save_data(st.session_state.data)
                st.session_state.editing_habit = None
                st.success("Habit updated successfully!")
            else:
                st.session_state.data["habits"].append({
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
                    "updated_at": get_today(),
                })
                save_data(st.session_state.data)
                st.success("Habit created successfully!")

elif page == "📊 Progress Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Your Progress</h1>
        <p>Track your compound growth</p>
    </div>
    """, unsafe_allow_html=True)

    data = st.session_state.data
    if not data.get("habits"):
        st.info("👋 No habits to track yet. Create your first habit to see your progress!")
    else:
        total_checkins = sum(len(dates) for dates in data["check_ins"].values())
        active_habits = len(data["habits"])
        total_streak = sum(get_streak(h["id"], data["check_ins"]) for h in data["habits"])
        avg_rate = sum(get_completion_rate(h["id"], data["check_ins"]) for h in data["habits"]) / active_habits if active_habits else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{active_habits}</div><div class="stat-label">Active Habits</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_checkins}</div><div class="stat-label">Total Check-ins</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_streak}</div><div class="stat-label">Current Streaks</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{round(avg_rate)}%</div><div class="stat-label">30-Day Consistency</div></div>', unsafe_allow_html=True)

        reflections = data.get("reflections", {})
        if reflections:
            st.markdown("---")
            st.subheader("📖 Past Reflections")
            for date, reflection in sorted(reflections.items(), key=lambda x: x[0], reverse=True)[:10]:
                with st.expander(f"📝 {date}"):
                    st.write(reflection)

elif page == "⚙️ Manage Habits":
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Manage Your Habits</h1>
        <p>Edit, delete, or reorganize</p>
    </div>
    """, unsafe_allow_html=True)

    data = st.session_state.data
    if not data.get("habits"):
        st.info("No habits to manage yet.")
    else:
        for i, habit in enumerate(data["habits"]):
            st.markdown(f"**{i+1}. {habit['name']}**")
            st.caption(f"Created: {habit['created_at']}")
            st.markdown("---")

elif page == "📚 Learn & Tips":
    st.markdown("""
    <div class="main-header">
        <h1>📚 Learn Atomic Habits</h1>
        <p>Master the framework</p>
    </div>
    """, unsafe_allow_html=True)

    show_tips_setting = st.checkbox(
        "Show beginner tips throughout the app",
        value=st.session_state.data.get("user_settings", {}).get("show_tips", True),
    )
    st.session_state.show_tips = show_tips_setting
    st.session_state.data["user_settings"]["show_tips"] = show_tips_setting
    save_data(st.session_state.data)

elif page == "👤 My Profile":
    st.markdown("""
    <div class="main-header">
        <h1>👤 My Profile</h1>
        <p>Your identity and settings</p>
    </div>
    """, unsafe_allow_html=True)

    data = st.session_state.data
    user_settings = data.get("user_settings", {})

    with st.form("profile_form"):
        st.subheader("📝 Your Information")
        name = st.text_input("Your Name", value=user_settings.get("name", ""), placeholder="What should we call you?")

        st.markdown("---")
        st.subheader("⚙️ App Settings")
        show_tips = st.checkbox("Show beginner tips", value=user_settings.get("show_tips", True))

        c1, c2 = st.columns(2)
        with c1:
            save_profile = st.form_submit_button("💾 Save Profile", use_container_width=True)
        with c2:
            reset_all = st.form_submit_button("🔄 Reset All Data", use_container_width=True)

        if save_profile:
            st.session_state.data["user_settings"]["name"] = name
            st.session_state.data["user_settings"]["show_tips"] = show_tips
            st.session_state.show_tips = show_tips
            save_data(st.session_state.data)
            st.success("Profile saved!")

        if reset_all:
            st.session_state.data = get_default_data()
            save_data(st.session_state.data)
            st.success("All data reset!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")
st.sidebar.caption("Based on Atomic Habits by James Clear")
'''
path = Path("/mnt/data/app_clean_fixed.py")
path.write_text(clean_app, encoding="utf-8")
print(path)
