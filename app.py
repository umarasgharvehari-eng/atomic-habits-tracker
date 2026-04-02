import streamlit as st
import json
import os
from datetime import datetime, timedelta
from collections import Counter
import pandas as pd

st.set_page_config(
    page_title="Atomic Habits Tracker Pro",
    page_icon="⚛️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 18px;
        text-align: center;
        margin-bottom: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.10);
    }
    .card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }
    .habit-card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 14px;
        border-left: 6px solid #667eea;
    }
    .habit-card.done {
        border-left-color: #4CAF50;
        background: linear-gradient(135deg, #f1f8e9 0%, #ffffff 100%);
    }
    .badge {
        display: inline-block;
        background: #eef2ff;
        color: #4254c5;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 4px;
    }
    .small-muted {
        color: #666;
        font-size: 13px;
    }
    .tip-box {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border-left: 4px solid #ffc107;
        padding: 14px;
        border-radius: 10px;
        margin: 12px 0;
    }
    .success-box {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-left: 4px solid #4caf50;
        padding: 14px;
        border-radius: 10px;
        margin: 12px 0;
    }
    .quote-box {
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 4px solid #9c27b0;
        padding: 18px;
        border-radius: 12px;
        margin: 16px 0;
        text-align: center;
        font-style: italic;
    }
    .stat-card {
        background: white;
        padding: 18px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .stat-number {
        font-size: 30px;
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
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        border-radius: 50%;
        margin: 2px;
        font-size: 11px;
        font-weight: 600;
    }
    .calendar-day.completed {
        background: #4caf50;
        color: white;
    }
    .calendar-day.missed {
        background: #ffebee;
        color: #d32f2f;
    }
    .calendar-day.future {
        background: #f1f1f1;
        color: #9e9e9e;
    }
</style>
""", unsafe_allow_html=True)

DATA_FILE = "habits_data.json"
MOOD_LABELS = ["😞 Tough", "😐 Okay", "🙂 Good", "😄 Great", "🔥 Amazing"]
ENERGY_LABELS = ["Low", "Steady", "High"]


def get_today():
    return datetime.now().strftime("%Y-%m-%d")


def get_week_key(date_str=None):
    if date_str is None:
        dt = datetime.now().date()
    else:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def get_default_data():
    today = get_today()
    return {
        "habits": [],
        "check_ins": {},
        "reflections": {},
        "daily_logs": {},
        "weekly_reviews": {},
        "today_status": {},
        "user_settings": {
            "name": "",
            "started_date": today,
            "theme": "default",
            "show_tips": True,
            "motivation": "",
            "weekly_goal": 80,
        },
    }


def normalize_data(data):
    defaults = get_default_data()
    if not isinstance(data, dict):
        data = {}

    normalized = {
        "habits": data.get("habits", []),
        "check_ins": data.get("check_ins", {}),
        "reflections": data.get("reflections", {}),
        "daily_logs": data.get("daily_logs", {}),
        "weekly_reviews": data.get("weekly_reviews", {}),
        "today_status": data.get("today_status", {}),
        "user_settings": data.get("user_settings", {}),
    }

    for key, val in defaults["user_settings"].items():
        if not isinstance(normalized["user_settings"], dict):
            normalized["user_settings"] = {}
        normalized["user_settings"].setdefault(key, val)

    for key in ["check_ins", "reflections", "daily_logs", "weekly_reviews", "today_status"]:
        if not isinstance(normalized[key], dict):
            normalized[key] = {}

    if not isinstance(normalized["habits"], list):
        normalized["habits"] = []

    clean_habits = []
    for i, habit in enumerate(normalized["habits"]):
        if not isinstance(habit, dict):
            habit = {}
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
        habit.setdefault("category", "Personal")
        habit.setdefault("difficulty", "Easy")
        habit.setdefault("why", "")
        habit.setdefault("celebration", "")
        habit.setdefault("active", True)
        clean_habits.append(habit)
    normalized["habits"] = clean_habits

    for habit_id, dates in list(normalized["check_ins"].items()):
        if not isinstance(dates, list):
            normalized["check_ins"][habit_id] = []
        else:
            normalized["check_ins"][habit_id] = sorted(list(set(dates)))
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
    today = datetime.now().date()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days - 1, -1, -1)]


def is_habit_scheduled_for_date(habit, date_obj):
    if not habit.get("active", True):
        return False
    if habit.get("weekend_skip", False) and date_obj.weekday() >= 5:
        return False
    return True


def is_habit_scheduled_today(habit):
    return is_habit_scheduled_for_date(habit, datetime.now().date())


def get_completed_dates_for_scheduled_days(habit_id, check_ins, habit_lookup, days=30):
    dates = get_date_list(days)
    habit = habit_lookup.get(habit_id, {})
    scheduled_dates = []
    done_dates = set(check_ins.get(habit_id, []))
    for date_str in dates:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        if is_habit_scheduled_for_date(habit, dt):
            scheduled_dates.append((date_str, date_str in done_dates))
    return scheduled_dates


def get_streak(habit_id, check_ins, habit_lookup):
    habit = habit_lookup.get(habit_id, {})

    # If a habit is paused/inactive, its live streak should be 0.
    if not habit.get("active", True):
        return 0

    done_dates = set(check_ins.get(habit_id, []))
    if not done_dates:
        return 0

    streak = 0
    day = datetime.now().date()

    # Safety bound to prevent date underflow / infinite loops.
    # More than enough for habit tracking while guaranteeing termination.
    for _ in range(3660):  # about 10 years
        if not is_habit_scheduled_for_date(habit, day):
            day -= timedelta(days=1)
            continue

        if day.strftime("%Y-%m-%d") in done_dates:
            streak += 1
            day -= timedelta(days=1)
        else:
            break

    return streak


def get_best_streak(habit_id, check_ins, habit_lookup, lookback_days=365):
    habit = habit_lookup.get(habit_id, {})
    done_dates = set(check_ins.get(habit_id, []))
    dates = []
    today = datetime.now().date()
    for i in range(lookback_days - 1, -1, -1):
        day = today - timedelta(days=i)
        if is_habit_scheduled_for_date(habit, day):
            dates.append(day.strftime("%Y-%m-%d"))
    if not dates:
        return 0
    best, current = 0, 0
    for date_str in dates:
        if date_str in done_dates:
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def get_completion_rate(habit_id, check_ins, habit_lookup, days=30):
    scheduled = get_completed_dates_for_scheduled_days(habit_id, check_ins, habit_lookup, days)
    if not scheduled:
        return 0
    completed = sum(1 for _, done in scheduled if done)
    return round((completed / len(scheduled)) * 100)


def get_weekly_progress(habit_id, check_ins, habit_lookup):
    values = []
    today = datetime.now().date()
    habit = habit_lookup.get(habit_id, {})
    done_dates = set(check_ins.get(habit_id, []))
    for week in range(3, -1, -1):
        week_start = today - timedelta(days=today.weekday() + (week * 7))
        total, completed = 0, 0
        for i in range(7):
            day = week_start + timedelta(days=i)
            if is_habit_scheduled_for_date(habit, day):
                total += 1
                if day.strftime("%Y-%m-%d") in done_dates:
                    completed += 1
        values.append((completed, total))
    return values


def get_today_status_map(data, date_str=None):
    date_str = date_str or get_today()
    status_root = data.setdefault("today_status", {})
    if not isinstance(status_root, dict):
        data["today_status"] = {}
        status_root = data["today_status"]
    day_map = status_root.setdefault(date_str, {})
    if not isinstance(day_map, dict):
        status_root[date_str] = {}
        day_map = status_root[date_str]
    return day_map


def is_habit_stopped_for_today(data, habit_id, date_str=None):
    date_str = date_str or get_today()
    return get_today_status_map(data, date_str).get(habit_id) == "stopped"


def set_habit_today_status(data, habit_id, status, date_str=None):
    date_str = date_str or get_today()
    day_map = get_today_status_map(data, date_str)
    if status:
        day_map[habit_id] = status
    else:
        day_map.pop(habit_id, None)


def get_today_progress_summary(data):
    habit_lookup = {h["id"]: h for h in data["habits"]}
    active_habits = [h for h in data["habits"] if h.get("active", True) and is_habit_scheduled_today(h)]
    total = len(active_habits)
    today_str = get_today()
    done_ids = {h["id"] for h in active_habits if today_str in data["check_ins"].get(h["id"], [])}
    stopped_ids = {h["id"] for h in active_habits if is_habit_stopped_for_today(data, h["id"], today_str)}
    handled_ids = done_ids | stopped_ids
    return {
        "habit_lookup": habit_lookup,
        "total": total,
        "completed": len(done_ids),
        "stopped": len(stopped_ids - done_ids),
        "handled": len(handled_ids),
        "remaining": max(total - len(handled_ids), 0),
    }


def get_today_summary(data):
    summary = get_today_progress_summary(data)
    return summary["completed"], summary["total"], summary["habit_lookup"]


def get_last_n_completion_counts(data, days=14):
    habit_lookup = {h["id"]: h for h in data["habits"]}
    rows = []
    for date_str in get_date_list(days):
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        scheduled = [h for h in data["habits"] if is_habit_scheduled_for_date(h, dt) and h.get("active", True)]
        done = sum(1 for h in scheduled if date_str in data["check_ins"].get(h["id"], []))
        rows.append({
            "date": date_str,
            "completed": done,
            "scheduled": len(scheduled),
            "rate": round((done / len(scheduled)) * 100, 1) if scheduled else 0
        })
    return pd.DataFrame(rows)


def get_category_breakdown(data):
    if not data["habits"]:
        return pd.DataFrame(columns=["category", "count"])
    counts = Counter(h.get("category", "Other") for h in data["habits"] if h.get("active", True))
    return pd.DataFrame({"category": list(counts.keys()), "count": list(counts.values())}).sort_values("count", ascending=False)


def get_mood_dataframe(data, days=14):
    rows = []
    mapping = {label: idx + 1 for idx, label in enumerate(MOOD_LABELS)}
    for date_str in get_date_list(days):
        log = data.get("daily_logs", {}).get(date_str, {})
        mood = log.get("mood")
        rows.append({
            "date": date_str,
            "mood_score": mapping.get(mood, 0)
        })
    return pd.DataFrame(rows)


def get_level(total_checkins):
    return (total_checkins // 25) + 1


def get_achievements(data):
    habit_lookup = {h["id"]: h for h in data["habits"]}
    total_checkins = sum(len(v) for v in data["check_ins"].values())
    today_summary = get_today_progress_summary(data)
    completed_today = today_summary["completed"]
    total_today = today_summary["total"]
    handled_today = today_summary["handled"]
    longest = 0
    for h in data["habits"]:
        longest = max(longest, get_best_streak(h["id"], data["check_ins"], habit_lookup))
    reflections_count = len([v for v in data.get("reflections", {}).values() if str(v).strip()])
    daily_logs = len(data.get("daily_logs", {}))

    badges = []
    if total_checkins >= 1:
        badges.append(("🌱 First Step", "Completed your first check-in"))
    if total_checkins >= 25:
        badges.append(("⚡ Momentum", "25 total habit check-ins"))
    if total_checkins >= 100:
        badges.append(("🏆 Century Club", "100 total habit check-ins"))
    if longest >= 7:
        badges.append(("🔥 7-Day Streak", "Maintained a 7-day streak"))
    if longest >= 30:
        badges.append(("🚀 30-Day Streak", "Maintained a 30-day streak"))
    if total_today > 0 and handled_today == total_today:
        badges.append(("✅ Handled Today", "Handled all scheduled habits today"))
    if total_today > 0 and completed_today == total_today:
        badges.append(("🌟 Perfect Completion", "Completed all scheduled habits today"))
    if reflections_count >= 5:
        badges.append(("📝 Reflective", "Saved 5 reflections"))
    if daily_logs >= 7:
        badges.append(("💛 Self-Aware", "Logged 7 daily mood/energy check-ins"))
    return badges


def recommend_next_action(data):
    if not data["habits"]:
        return "Create your first tiny habit. Make it small enough that you can do it in under 2 minutes."
    habit_lookup = {h["id"]: h for h in data["habits"]}
    scored = []
    for habit in data["habits"]:
        if not habit.get("active", True):
            continue
        rate = get_completion_rate(habit["id"], data["check_ins"], habit_lookup, 14)
        scored.append((rate, habit))
    if not scored:
        return "Start with one active habit and check it off today."
    scored.sort(key=lambda x: x[0])
    low_rate, habit = scored[0]
    if low_rate < 40:
        return f"Your weakest system right now is '{habit['name']}'. Shrink it to the 2-minute version: {habit.get('two_minute_version') or 'make it easier'}."
    if low_rate < 70:
        return f"'{habit['name']}' is close. Add a stronger cue: after {habit.get('stack_trigger') or 'an existing routine'}, do it immediately."
    return "You're building consistency well. Protect your current streaks by doing the easiest habit first today."


def show_tip(text, success=False):
    if st.session_state.show_tips:
        css = "success-box" if success else "tip-box"
        label = "Tip" if success else "Beginner Tip"
        st.markdown(f'<div class="{css}">💡 <b>{label}:</b> {text}</div>', unsafe_allow_html=True)


def persist():
    save_data(st.session_state.data)
    st.session_state.data = normalize_data(st.session_state.data)


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
    <h3 style="margin: 5px 0; color: #333;">Atomic Habits Tracker Pro</h3>
    <p style="font-size: 12px; color: #666;">Small habits, big identity change</p>
</div>
""", unsafe_allow_html=True)

pages = [
    "🏠 Today's Habits",
    "➕ Add New Habit",
    "📊 Progress Dashboard",
    "📅 Weekly Review",
    "⚙️ Manage Habits",
    "🏆 Achievements",
    "📚 Learn & Tips",
    "👤 My Profile",
]
default_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
page = st.sidebar.radio("Navigate", pages, index=default_index)
st.session_state.current_page = page

data = st.session_state.data
today_summary = get_today_progress_summary(data)
completed_today = today_summary["completed"]
total_today = today_summary["total"]
handled_today = today_summary["handled"]
stopped_today = today_summary["stopped"]
remaining_today = today_summary["remaining"]
habit_lookup = today_summary["habit_lookup"]
total_checkins = sum(len(v) for v in data["check_ins"].values())
level = get_level(total_checkins)
weekly_goal = data["user_settings"].get("weekly_goal", 80)
weekly_df = get_last_n_completion_counts(data, 7)
weekly_avg = round(weekly_df["rate"].mean(), 1) if not weekly_df.empty else 0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Quick Stats")
st.sidebar.metric("Today's Progress", f"{handled_today}/{total_today}" if total_today else "0/0")
st.sidebar.metric("Level", f"Lv. {level}")
st.sidebar.metric("This Week", f"{weekly_avg}%")
st.sidebar.progress(min(weekly_avg / 100, 1.0), text=f"Goal: {weekly_goal}%")
st.sidebar.caption(recommend_next_action(data))
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")

# PAGE: TODAY
if page == "🏠 Today's Habits":
    name = data["user_settings"].get("name", "").strip()
    subtitle = f"Welcome, {name} — focus on showing up, not being perfect" if name else "Focus on showing up, not being perfect"
    st.markdown(f"""
    <div class="main-header">
        <h1>🌅 Today's Habits</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

    show_tip("Start with the easiest habit first. Action creates motivation. You can also stop a task for today if you do not want it in your remaining list.", success=False)

    if name:
        st.write(f"Welcome back, **{name}**.")
    if not data["habits"]:
        st.info("You have no habits yet. Start with one tiny habit.")
        if st.button("➕ Create Your First Habit", use_container_width=True):
            st.session_state.current_page = "➕ Add New Habit"
            st.rerun()
    else:
        handled_rate = round((handled_today / total_today) * 100) if total_today else 0
        completion_rate = round((completed_today / total_today) * 100) if total_today else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completed_today}</div><div class="stat-label">Completed</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{stopped_today}</div><div class="stat-label">Stopped Today</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{remaining_today}</div><div class="stat-label">Remaining</div></div>', unsafe_allow_html=True)
        with c4:
            total_streak = sum(get_streak(h["id"], data["check_ins"], habit_lookup) for h in data["habits"] if h.get("active", True))
            st.markdown(f'<div class="stat-card"><div class="stat-number">{handled_rate}%</div><div class="stat-label">Handled Today</div></div>', unsafe_allow_html=True)

        st.progress(min(handled_rate / 100, 1.0), text=f"Today handled: {handled_today}/{total_today}")
        st.caption(f"Completion score: {completion_rate}% • Stopped tasks are hidden from today remaining count but are not counted as completed.")
        if total_today > 0 and handled_today == total_today:
            st.success("🎉 Nice work. You handled all scheduled habits for today.")

        st.markdown("---")
        filter_col, sort_col = st.columns(2)
        with filter_col:
            filter_status = st.selectbox("Filter", ["All", "Pending", "Completed", "Stopped", "Only Active"], label_visibility="collapsed")
        with sort_col:
            sort_by = st.selectbox("Sort", ["Priority", "Name", "Streak", "Category"], label_visibility="collapsed")

        habits_to_show = [h for h in data["habits"] if h.get("active", True) or filter_status != "Only Active"]

        if sort_by == "Name":
            habits_to_show = sorted(habits_to_show, key=lambda h: h["name"].lower())
        elif sort_by == "Streak":
            habits_to_show = sorted(habits_to_show, key=lambda h: get_streak(h["id"], data["check_ins"], habit_lookup), reverse=True)
        elif sort_by == "Category":
            habits_to_show = sorted(habits_to_show, key=lambda h: h.get("category", ""))
        else:
            difficulty_rank = {"Easy": 0, "Medium": 1, "Hard": 2}
            habits_to_show = sorted(habits_to_show, key=lambda h: (difficulty_rank.get(h.get("difficulty", "Easy"), 0), h["name"].lower()))

        today_str = get_today()
        for habit in habits_to_show:
            scheduled = is_habit_scheduled_today(habit)
            done = today_str in data["check_ins"].get(habit["id"], [])
            stopped = is_habit_stopped_for_today(data, habit["id"], today_str)
            if filter_status == "Pending" and (done or stopped):
                continue
            if filter_status == "Completed" and not done:
                continue
            if filter_status == "Stopped" and not stopped:
                continue
            if filter_status == "Only Active" and not habit.get("active", True):
                continue

            streak = get_streak(habit["id"], data["check_ins"], habit_lookup)
            card_class = "habit-card done" if done else "habit-card"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            left, mid, right = st.columns([3.2, 1.1, 1.8])

            with left:
                title = f"**{habit['name']}**"
                if stopped:
                    title += " _(Stopped for today)_"
                elif not scheduled:
                    title += " _(Not scheduled today)_"
                st.markdown(title)
                st.markdown(f"<span class='badge'>I am {habit['identity']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='badge'>{habit.get('category', 'Personal')}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='badge'>{habit.get('difficulty', 'Easy')}</span>", unsafe_allow_html=True)
                if habit.get("stack_trigger"):
                    st.caption(f"🔗 After: {habit['stack_trigger']}")
                if habit.get("two_minute_version"):
                    st.caption(f"⏱️ Tiny version: {habit['two_minute_version']}")
                if habit.get("why"):
                    st.caption(f"🎯 Why: {habit['why']}")
                if habit.get("celebration"):
                    st.caption(f"🎉 Celebrate with: {habit['celebration']}")

            with mid:
                st.metric("Streak", f"{streak}")
                st.caption(f"30d: {get_completion_rate(habit['id'], data['check_ins'], habit_lookup)}%")

            with right:
                if scheduled:
                    if done:
                        st.success("✅ Completed")
                        x1, x2 = st.columns(2)
                        with x1:
                            if st.button("Undo", key=f"undo_{habit['id']}", use_container_width=True):
                                if today_str in data["check_ins"].get(habit["id"], []):
                                    data["check_ins"][habit["id"]].remove(today_str)
                                set_habit_today_status(data, habit["id"], None, today_str)
                                persist()
                                st.rerun()
                        with x2:
                            stop_label = "Stopped ✓" if stopped else "Stop Today"
                            if st.button(stop_label, key=f"stop_done_{habit['id']}", use_container_width=True):
                                set_habit_today_status(data, habit["id"], None if stopped else "stopped", today_str)
                                persist()
                                st.rerun()
                    elif stopped:
                        st.warning("⏸️ Stopped for today")
                        x1, x2 = st.columns(2)
                        with x1:
                            if st.button("Resume", key=f"resume_{habit['id']}", use_container_width=True):
                                set_habit_today_status(data, habit["id"], None, today_str)
                                persist()
                                st.rerun()
                        with x2:
                            if st.button("Complete", key=f"complete_stopped_{habit['id']}", use_container_width=True):
                                data["check_ins"].setdefault(habit["id"], [])
                                if today_str not in data["check_ins"][habit["id"]]:
                                    data["check_ins"][habit["id"]].append(today_str)
                                set_habit_today_status(data, habit["id"], None, today_str)
                                persist()
                                st.balloons()
                                st.rerun()
                    else:
                        x1, x2 = st.columns(2)
                        with x1:
                            if st.button("Complete", key=f"complete_{habit['id']}", use_container_width=True):
                                data["check_ins"].setdefault(habit["id"], [])
                                if today_str not in data["check_ins"][habit["id"]]:
                                    data["check_ins"][habit["id"]].append(today_str)
                                set_habit_today_status(data, habit["id"], None, today_str)
                                persist()
                                st.balloons()
                                st.rerun()
                        with x2:
                            if st.button("Stop Today", key=f"stop_{habit['id']}", use_container_width=True):
                                set_habit_today_status(data, habit["id"], "stopped", today_str)
                                persist()
                                st.rerun()
                else:
                    st.info("Skip day")

                a, b = st.columns(2)
                with a:
                    if st.button("Edit", key=f"edit_{habit['id']}", use_container_width=True):
                        st.session_state.editing_habit = habit["id"]
                        st.session_state.current_page = "➕ Add New Habit"
                        st.rerun()
                with b:
                    if st.button("Delete", key=f"delete_{habit['id']}", use_container_width=True):
                        st.session_state.show_delete_confirm = habit["id"]
                        st.rerun()
            st.markdown("</div>", unsafe_all
