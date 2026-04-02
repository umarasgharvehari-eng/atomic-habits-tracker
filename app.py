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
        "user_settings": data.get("user_settings", {}),
    }

    for key, val in defaults["user_settings"].items():
        if not isinstance(normalized["user_settings"], dict):
            normalized["user_settings"] = {}
        normalized["user_settings"].setdefault(key, val)

    for key in ["check_ins", "reflections", "daily_logs", "weekly_reviews"]:
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
    done_dates = set(check_ins.get(habit_id, []))
    streak = 0
    day = datetime.now().date()
    while True:
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


def get_today_summary(data):
    habit_lookup = {h["id"]: h for h in data["habits"]}
    active_habits = [h for h in data["habits"] if h.get("active", True) and is_habit_scheduled_today(h)]
    total = len(active_habits)
    completed = sum(1 for h in active_habits if get_today() in data["check_ins"].get(h["id"], []))
    return completed, total, habit_lookup


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
    completed_today, total_today, _ = get_today_summary(data)
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
    if total_today > 0 and completed_today == total_today:
        badges.append(("✅ Perfect Day", "Completed all scheduled habits today"))
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
completed_today, total_today, habit_lookup = get_today_summary(data)
total_checkins = sum(len(v) for v in data["check_ins"].values())
level = get_level(total_checkins)
weekly_goal = data["user_settings"].get("weekly_goal", 80)
weekly_df = get_last_n_completion_counts(data, 7)
weekly_avg = round(weekly_df["rate"].mean(), 1) if not weekly_df.empty else 0

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Quick Stats")
st.sidebar.metric("Today's Progress", f"{completed_today}/{total_today}" if total_today else "0/0")
st.sidebar.metric("Level", f"Lv. {level}")
st.sidebar.metric("This Week", f"{weekly_avg}%")
st.sidebar.progress(min(weekly_avg / 100, 1.0), text=f"Goal: {weekly_goal}%")
st.sidebar.caption(recommend_next_action(data))
st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ using Streamlit")

# PAGE: TODAY
if page == "🏠 Today's Habits":
    st.markdown("""
    <div class="main-header">
        <h1>🌅 Today's Habits</h1>
        <p>Focus on showing up, not being perfect</p>
    </div>
    """, unsafe_allow_html=True)

    show_tip("Start with the easiest habit first. Action creates motivation.", success=False)

    name = data["user_settings"].get("name", "").strip()
    if name:
        st.write(f"Welcome back, **{name}**.")
    if not data["habits"]:
        st.info("You have no habits yet. Start with one tiny habit.")
        if st.button("➕ Create Your First Habit", use_container_width=True):
            st.session_state.current_page = "➕ Add New Habit"
            st.rerun()
    else:
        completion_rate = round((completed_today / total_today) * 100) if total_today else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completed_today}</div><div class="stat-label">Done Today</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{max(total_today - completed_today, 0)}</div><div class="stat-label">Remaining</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{completion_rate}%</div><div class="stat-label">Daily Score</div></div>', unsafe_allow_html=True)
        with c4:
            total_streak = sum(get_streak(h["id"], data["check_ins"], habit_lookup) for h in data["habits"] if h.get("active", True))
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_streak}</div><div class="stat-label">Streak Power</div></div>', unsafe_allow_html=True)

        st.progress(min(completion_rate / 100, 1.0), text=f"Today: {completion_rate}%")
        if total_today > 0 and completed_today == total_today:
            st.success("🎉 Perfect day. Protect this identity by repeating it tomorrow.")

        st.markdown("---")
        filter_col, sort_col = st.columns(2)
        with filter_col:
            filter_status = st.selectbox("Filter", ["All", "Pending", "Completed", "Only Active"], label_visibility="collapsed")
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
            if filter_status == "Pending" and done:
                continue
            if filter_status == "Completed" and not done:
                continue
            if filter_status == "Only Active" and not habit.get("active", True):
                continue

            streak = get_streak(habit["id"], data["check_ins"], habit_lookup)
            card_class = "habit-card done" if done else "habit-card"
            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
            left, mid, right = st.columns([3.2, 1.1, 1.8])

            with left:
                title = f"**{habit['name']}**"
                if not scheduled:
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
                        st.success("✅ Done")
                        if st.button("Undo", key=f"undo_{habit['id']}", use_container_width=True):
                            if today_str in data["check_ins"].get(habit["id"], []):
                                data["check_ins"][habit["id"]].remove(today_str)
                                persist()
                                st.rerun()
                    else:
                        if st.button("Complete", key=f"complete_{habit['id']}", use_container_width=True):
                            data["check_ins"].setdefault(habit["id"], [])
                            if today_str not in data["check_ins"][habit["id"]]:
                                data["check_ins"][habit["id"]].append(today_str)
                                persist()
                                st.balloons()
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
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.show_delete_confirm:
            hid = st.session_state.show_delete_confirm
            habit_name = next((h["name"] for h in data["habits"] if h["id"] == hid), "this habit")
            st.warning(f"Delete '{habit_name}' and its history?")
            d1, d2 = st.columns(2)
            with d1:
                if st.button("Yes, delete", key="confirm_delete"):
                    data["habits"] = [h for h in data["habits"] if h["id"] != hid]
                    data["check_ins"].pop(hid, None)
                    persist()
                    st.session_state.show_delete_confirm = None
                    st.rerun()
            with d2:
                if st.button("Cancel", key="cancel_delete"):
                    st.session_state.show_delete_confirm = None
                    st.rerun()

        st.markdown("---")
        st.subheader("🧠 Daily Check-in")
        show_tip("Your mood and energy affect your habits. Track them so you can design better systems.", success=True)

        today_log = data["daily_logs"].get(today_str, {})
        with st.form("daily_checkin_form"):
            c1, c2 = st.columns(2)
            with c1:
                mood = st.selectbox("Mood", MOOD_LABELS, index=MOOD_LABELS.index(today_log.get("mood", "🙂 Good")) if today_log.get("mood", "🙂 Good") in MOOD_LABELS else 2)
            with c2:
                energy = st.selectbox("Energy", ENERGY_LABELS, index=ENERGY_LABELS.index(today_log.get("energy", "Steady")) if today_log.get("energy", "Steady") in ENERGY_LABELS else 1)

            win = st.text_input("Small win today", value=today_log.get("win", ""), placeholder="What worked well today?")
            obstacle = st.text_input("Obstacle today", value=today_log.get("obstacle", ""), placeholder="What got in the way?")
            tomorrow_focus = st.text_input("Tomorrow focus", value=today_log.get("tomorrow_focus", ""), placeholder="What will you make easier tomorrow?")
            reflection = st.text_area("Reflection", value=data["reflections"].get(today_str, ""), placeholder="I showed up even when I did not feel like it...")

            saved = st.form_submit_button("💾 Save Daily Check-in", use_container_width=True)
            if saved:
                data["daily_logs"][today_str] = {
                    "mood": mood,
                    "energy": energy,
                    "win": win,
                    "obstacle": obstacle,
                    "tomorrow_focus": tomorrow_focus,
                }
                data["reflections"][today_str] = reflection
                persist()
                st.success("Daily check-in saved.")

# PAGE: ADD / EDIT
elif page == "➕ Add New Habit":
    is_editing = st.session_state.editing_habit is not None
    habit_to_edit = next((h for h in data["habits"] if h["id"] == st.session_state.editing_habit), None) if is_editing else None

    st.markdown(f"""
    <div class="main-header">
        <h1>{"✏️ Edit Habit" if is_editing else "➕ Create New Atomic Habit"}</h1>
        <p>{"Refine your system" if is_editing else "Build identity-based habits that you can actually keep"}</p>
    </div>
    """, unsafe_allow_html=True)

    show_tip("Make the habit obvious, attractive, easy, and satisfying.", success=False)

    with st.form("habit_form", clear_on_submit=not is_editing):
        st.subheader("Core habit")
        name = st.text_input("Habit Name *", value=habit_to_edit["name"] if habit_to_edit else "", placeholder="Read, Walk, Meditate")
        c1, c2 = st.columns(2)
        with c1:
            two_minute = st.text_input("2-Minute Version *", value=habit_to_edit["two_minute_version"] if habit_to_edit else "", placeholder="Read 1 page")
        with c2:
            identity = st.text_input("Identity Statement *", value=habit_to_edit["identity"] if habit_to_edit else "", placeholder="a reader")

        st.subheader("Cue and motivation")
        stack_trigger = st.text_input("After I...", value=habit_to_edit["stack_trigger"] if habit_to_edit else "", placeholder="pour my coffee")
        location = st.text_input("Where will you do it?", value=habit_to_edit.get("location", "") if habit_to_edit else "", placeholder="living room")
        why = st.text_input("Why does this matter?", value=habit_to_edit.get("why", "") if habit_to_edit else "", placeholder="It helps me become calmer and stronger.")
        reward = st.text_input("Reward / temptation bundle", value=habit_to_edit.get("reward", "") if habit_to_edit else "", placeholder="listen to a favorite podcast")
        celebration = st.text_input("How will you celebrate?", value=habit_to_edit.get("celebration", "") if habit_to_edit else "", placeholder="say 'I keep promises to myself'")

        st.subheader("Settings")
        c1, c2, c3 = st.columns(3)
        time_options = ["Morning (6-9am)", "Late Morning (9-12pm)", "Afternoon (12-5pm)", "Evening (5-9pm)", "Anytime"]
        with c1:
            time_of_day = st.selectbox("Best time", time_options, index=time_options.index(habit_to_edit.get("time_of_day", "Morning (6-9am)")) if habit_to_edit and habit_to_edit.get("time_of_day", "Morning (6-9am)") in time_options else 0)
        with c2:
            category = st.selectbox("Category", ["Health", "Learning", "Work", "Mindset", "Relationships", "Spiritual", "Personal"], index=["Health", "Learning", "Work", "Mindset", "Relationships", "Spiritual", "Personal"].index(habit_to_edit.get("category", "Personal")) if habit_to_edit and habit_to_edit.get("category", "Personal") in ["Health", "Learning", "Work", "Mindset", "Relationships", "Spiritual", "Personal"] else 6)
        with c3:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=["Easy", "Medium", "Hard"].index(habit_to_edit.get("difficulty", "Easy")) if habit_to_edit and habit_to_edit.get("difficulty", "Easy") in ["Easy", "Medium", "Hard"] else 0)
        c4, c5 = st.columns(2)
        with c4:
            weekend_skip = st.checkbox("Skip weekends", value=habit_to_edit.get("weekend_skip", False) if habit_to_edit else False)
        with c5:
            active = st.checkbox("Active habit", value=habit_to_edit.get("active", True) if habit_to_edit else True)

        submitted = st.form_submit_button("💾 Update Habit" if is_editing else "➕ Create Habit", use_container_width=True)

        if submitted:
            if not (name and two_minute and identity):
                st.error("Please fill all required fields.")
            else:
                payload = {
                    "name": name,
                    "two_minute_version": two_minute,
                    "identity": identity,
                    "stack_trigger": stack_trigger,
                    "location": location,
                    "why": why,
                    "reward": reward,
                    "celebration": celebration,
                    "time_of_day": time_of_day,
                    "category": category,
                    "difficulty": difficulty,
                    "weekend_skip": weekend_skip,
                    "active": active,
                    "updated_at": get_today(),
                }
                if is_editing and habit_to_edit:
                    habit_to_edit.update(payload)
                    st.session_state.editing_habit = None
                    persist()
                    st.success("Habit updated.")
                else:
                    payload.update({
                        "id": f"habit_{int(datetime.now().timestamp())}_{len(data['habits'])}",
                        "created_at": get_today(),
                        "reminder_enabled": True,
                    })
                    data["habits"].append(payload)
                    persist()
                    st.success("Habit created.")
                    st.balloons()

    if is_editing and st.button("Cancel editing", use_container_width=True):
        st.session_state.editing_habit = None
        st.rerun()

# PAGE: DASHBOARD
elif page == "📊 Progress Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>📊 Progress Dashboard</h1>
        <p>Measure consistency, not perfection</p>
    </div>
    """, unsafe_allow_html=True)

    if not data["habits"]:
        st.info("Create your first habit to unlock the dashboard.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        best_streak_overall = max([get_best_streak(h["id"], data["check_ins"], habit_lookup) for h in data["habits"]] or [0])
        active_habits = len([h for h in data["habits"] if h.get("active", True)])
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{active_habits}</div><div class="stat-label">Active Habits</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_checkins}</div><div class="stat-label">Total Check-ins</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{best_streak_overall}</div><div class="stat-label">Best Streak</div></div>', unsafe_allow_html=True)
        with c4:
            avg_30 = round(sum(get_completion_rate(h["id"], data["check_ins"], habit_lookup, 30) for h in data["habits"]) / len(data["habits"]), 1)
            st.markdown(f'<div class="stat-card"><div class="stat-number">{avg_30}%</div><div class="stat-label">30d Avg</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        tabs = st.tabs(["📈 Trends", "🥇 Habit Rankings", "📖 Reflections"])

        with tabs[0]:
            completion_df = get_last_n_completion_counts(data, 21)
            st.caption("Completion rate over the last 21 days")
            st.line_chart(completion_df.set_index("date")["rate"])
            mood_df = get_mood_dataframe(data, 21)
            if mood_df["mood_score"].sum() > 0:
                st.caption("Mood trend over the last 21 days")
                st.line_chart(mood_df.set_index("date")["mood_score"])
            category_df = get_category_breakdown(data)
            if not category_df.empty:
                st.caption("Active habits by category")
                st.bar_chart(category_df.set_index("category"))

        with tabs[1]:
            ranking_rows = []
            for habit in data["habits"]:
                ranking_rows.append({
                    "Habit": habit["name"],
                    "Category": habit.get("category", "Personal"),
                    "Current Streak": get_streak(habit["id"], data["check_ins"], habit_lookup),
                    "Best Streak": get_best_streak(habit["id"], data["check_ins"], habit_lookup),
                    "7d %": get_completion_rate(habit["id"], data["check_ins"], habit_lookup, 7),
                    "30d %": get_completion_rate(habit["id"], data["check_ins"], habit_lookup, 30),
                    "Status": "Active" if habit.get("active", True) else "Paused",
                })
            ranking_df = pd.DataFrame(ranking_rows).sort_values(["30d %", "Current Streak"], ascending=False)
            st.dataframe(ranking_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("Individual deep dive")
            chosen = st.selectbox("Choose a habit", [h["name"] for h in data["habits"]])
            habit = next(h for h in data["habits"] if h["name"] == chosen)
            habit_id = habit["id"]
            st.write(f"**Identity:** I am {habit['identity']}")
            st.write(f"**Recommendation:** {recommend_next_action({'habits':[habit], 'check_ins': data['check_ins'], 'reflections':{}, 'daily_logs':{}, 'weekly_reviews':{}, 'user_settings': data['user_settings']})}")
            weekly = get_weekly_progress(habit_id, data["check_ins"], habit_lookup)
            for idx, (done, total) in enumerate(weekly):
                label = ["3 weeks ago", "2 weeks ago", "Last week", "This week"][idx]
                st.progress((done / total) if total else 0.0, text=f"{label}: {done}/{total}")

            st.caption("Last 14 scheduled days")
            cols = st.columns(14)
            scheduled = get_completed_dates_for_scheduled_days(habit_id, data["check_ins"], habit_lookup, 30)
            recent = scheduled[-14:]
            for i, (date_str, done) in enumerate(recent):
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                cls = "completed" if done else "missed"
                cols[i].markdown(f"<div class='calendar-day {cls}'>{dt.strftime('%a')[0]}</div>", unsafe_allow_html=True)

        with tabs[2]:
            reflections = data.get("reflections", {})
            if reflections:
                for date_str, reflection in sorted(reflections.items(), reverse=True)[:20]:
                    with st.expander(f"📝 {date_str}"):
                        st.write(reflection or "_No reflection text_")
                        log = data.get("daily_logs", {}).get(date_str, {})
                        if log:
                            st.caption(f"Mood: {log.get('mood', '-')}, Energy: {log.get('energy', '-')}")
                            if log.get("win"):
                                st.write(f"**Win:** {log['win']}")
                            if log.get("obstacle"):
                                st.write(f"**Obstacle:** {log['obstacle']}")
                            if log.get("tomorrow_focus"):
                                st.write(f"**Tomorrow focus:** {log['tomorrow_focus']}")
            else:
                st.info("No reflections yet. Save one from Today's Habits.")

# PAGE: WEEKLY REVIEW
elif page == "📅 Weekly Review":
    st.markdown("""
    <div class="main-header">
        <h1>📅 Weekly Review</h1>
        <p>Review your systems and adjust the environment</p>
    </div>
    """, unsafe_allow_html=True)

    week_key = get_week_key()
    current_review = data["weekly_reviews"].get(week_key, {})
    week_df = get_last_n_completion_counts(data, 7)
    weekly_consistency = round(week_df["rate"].mean(), 1) if not week_df.empty else 0
    toughest_day = week_df.sort_values("rate").iloc[0]["date"] if not week_df.empty else get_today()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Weekly Consistency", f"{weekly_consistency}%")
    with c2:
        st.metric("Weekly Goal", f"{weekly_goal}%")
    with c3:
        st.metric("Gap", f"{round(weekly_goal - weekly_consistency,1)}%")

    st.markdown("---")
    st.write("**Weekly insight**")
    if weekly_consistency >= weekly_goal:
        st.success("You hit your weekly standard. Focus on protecting your environment and avoiding overconfidence.")
    elif weekly_consistency >= 60:
        st.info("You are close. Pick one low-performing habit and make it easier next week.")
    else:
        st.warning("Your system has too much friction right now. Reduce the size of the habit and strengthen the cue.")

    st.caption(f"Toughest day this week: {toughest_day}")
    st.line_chart(week_df.set_index("date")["rate"])

    with st.form("weekly_review_form"):
        wins = st.text_area("What worked this week?", value=current_review.get("wins", ""), placeholder="Which systems helped you stay consistent?")
        friction = st.text_area("What caused friction?", value=current_review.get("friction", ""), placeholder="What made habits hard?")
        redesign = st.text_area("How will you redesign your environment next week?", value=current_review.get("redesign", ""), placeholder="What will you make more obvious, easier, or more satisfying?")
        keep = st.text_input("One habit to protect next week", value=current_review.get("keep", ""), placeholder="Which habit is worth defending?")
        submit_review = st.form_submit_button("💾 Save Weekly Review", use_container_width=True)
        if submit_review:
            data["weekly_reviews"][week_key] = {
                "wins": wins,
                "friction": friction,
                "redesign": redesign,
                "keep": keep,
            }
            persist()
            st.success("Weekly review saved.")

    if data["weekly_reviews"]:
        st.markdown("---")
        st.subheader("Past weekly reviews")
        for review_week, review in sorted(data["weekly_reviews"].items(), reverse=True)[:8]:
            with st.expander(f"Week of {review_week}"):
                st.write(f"**Wins:** {review.get('wins', '')}")
                st.write(f"**Friction:** {review.get('friction', '')}")
                st.write(f"**Redesign:** {review.get('redesign', '')}")
                st.write(f"**Protect:** {review.get('keep', '')}")

# PAGE: MANAGE
elif page == "⚙️ Manage Habits":
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Manage Habits</h1>
        <p>Edit, pause, reorder, or export your systems</p>
    </div>
    """, unsafe_allow_html=True)

    if not data["habits"]:
        st.info("No habits to manage yet.")
    else:
        for i, habit in enumerate(data["habits"]):
            with st.container():
                st.markdown('<div class="card">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns([3, 1.5, 2])
                with c1:
                    st.markdown(f"**{i + 1}. {habit['name']}**")
                    st.caption(f"{habit.get('category','Personal')} • {habit.get('difficulty','Easy')} • {'Active' if habit.get('active', True) else 'Paused'}")
                    st.caption(f"Created: {habit.get('created_at', get_today())}")
                with c2:
                    st.metric("Streak", get_streak(habit["id"], data["check_ins"], habit_lookup))
                    st.metric("30d", f"{get_completion_rate(habit['id'], data['check_ins'], habit_lookup)}%")
                with c3:
                    u1, u2 = st.columns(2)
                    with u1:
                        if i > 0 and st.button("⬆️ Up", key=f"up_{habit['id']}", use_container_width=True):
                            data["habits"][i], data["habits"][i-1] = data["habits"][i-1], data["habits"][i]
                            persist()
                            st.rerun()
                    with u2:
                        if i < len(data["habits"]) - 1 and st.button("⬇️ Down", key=f"down_{habit['id']}", use_container_width=True):
                            data["habits"][i], data["habits"][i+1] = data["habits"][i+1], data["habits"][i]
                            persist()
                            st.rerun()

                    u3, u4 = st.columns(2)
                    with u3:
                        if st.button("✏️ Edit", key=f"manage_edit_{habit['id']}", use_container_width=True):
                            st.session_state.editing_habit = habit["id"]
                            st.session_state.current_page = "➕ Add New Habit"
                            st.rerun()
                    with u4:
                        toggle_label = "Pause" if habit.get("active", True) else "Resume"
                        if st.button(toggle_label, key=f"pause_{habit['id']}", use_container_width=True):
                            habit["active"] = not habit.get("active", True)
                            persist()
                            st.rerun()

                    if st.button("🗑️ Delete habit", key=f"manage_delete_{habit['id']}", use_container_width=True):
                        data["habits"] = [h for h in data["habits"] if h["id"] != habit["id"]]
                        data["check_ins"].pop(habit["id"], None)
                        persist()
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")
        json_str = json.dumps(data, indent=2)
        st.download_button("📥 Export Backup JSON", data=json_str, file_name="atomic_habits_backup.json", mime="application/json", use_container_width=True)

# PAGE: ACHIEVEMENTS
elif page == "🏆 Achievements":
    st.markdown("""
    <div class="main-header">
        <h1>🏆 Achievements</h1>
        <p>Celebrate evidence of your new identity</p>
    </div>
    """, unsafe_allow_html=True)

    badges = get_achievements(data)
    total_checkins = sum(len(v) for v in data["check_ins"].values())
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Level", get_level(total_checkins))
    with c2:
        st.metric("Badges", len(badges))
    with c3:
        st.metric("Total Check-ins", total_checkins)

    if badges:
        for icon, desc in badges:
            st.markdown(f'<div class="card"><h4 style="margin-bottom:6px;">{icon}</h4><div>{desc}</div></div>', unsafe_allow_html=True)
    else:
        st.info("Complete your first habit to unlock achievements.")

    st.markdown("---")
    st.subheader("Motivation")
    st.markdown(f'<div class="quote-box">"Every action you take is a vote for the type of person you wish to become."</div>', unsafe_allow_html=True)

# PAGE: LEARN
elif page == "📚 Learn & Tips":
    st.markdown("""
    <div class="main-header">
        <h1>📚 Learn Atomic Habits</h1>
        <p>Use behavior design to make consistency easier</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("tips_form"):
        show_tips_setting = st.checkbox("Show beginner tips across the app", value=data["user_settings"].get("show_tips", True))
        saved = st.form_submit_button("Save preference", use_container_width=True)
        if saved:
            data["user_settings"]["show_tips"] = show_tips_setting
            st.session_state.show_tips = show_tips_setting
            persist()
            st.success("Preference saved.")

    st.markdown("---")
    st.subheader("Your personalized advice")
    st.write(recommend_next_action(data))

    st.markdown("---")
    laws = [
        ("🎯 Make It Obvious", "Design a cue. Use habit stacking and keep the trigger visible."),
        ("😍 Make It Attractive", "Pair the habit with something enjoyable and connect it to your desired identity."),
        ("✅ Make It Easy", "Shrink the action. The 2-minute version should feel almost too easy."),
        ("🎉 Make It Satisfying", "Celebrate immediately, check it off, and never miss twice."),
    ]
    for title, desc in laws:
        with st.expander(title):
            st.write(desc)

    st.markdown("---")
    quotes = [
        "You do not rise to the level of your goals. You fall to the level of your systems.",
        "Success is the product of daily habits, not once-in-a-lifetime transformations.",
        "Habits are the compound interest of self-improvement.",
    ]
    for quote in quotes:
        st.markdown(f'<div class="quote-box">{quote}</div>', unsafe_allow_html=True)

# PAGE: PROFILE
elif page == "👤 My Profile":
    st.markdown("""
    <div class="main-header">
        <h1>👤 My Profile</h1>
        <p>Your identity, motivation, and app settings</p>
    </div>
    """, unsafe_allow_html=True)

    user_settings = data.get("user_settings", {})
    with st.form("profile_form"):
        st.subheader("Your information")
        name = st.text_input("Your Name", value=user_settings.get("name", ""), placeholder="What should we call you?")
        motivation = st.text_area("Why are you building these habits?", value=user_settings.get("motivation", ""), placeholder="I want to become more disciplined, peaceful, and healthy.")
        weekly_goal_input = st.slider("Weekly consistency goal (%)", min_value=40, max_value=100, value=int(user_settings.get("weekly_goal", 80)), step=5)
        show_tips = st.checkbox("Show beginner tips", value=user_settings.get("show_tips", True))

        save_profile = st.form_submit_button("💾 Save Profile", use_container_width=True)
        if save_profile:
            data["user_settings"]["name"] = name
            data["user_settings"]["motivation"] = motivation
            data["user_settings"]["weekly_goal"] = weekly_goal_input
            data["user_settings"]["show_tips"] = show_tips
            st.session_state.show_tips = show_tips
            persist()
            st.success("Profile saved.")

    st.markdown("---")
    st.subheader("Journey summary")
    started_str = user_settings.get("started_date", get_today())
    try:
        start_date = datetime.strptime(started_str, "%Y-%m-%d")
    except ValueError:
        start_date = datetime.now()
    days_journey = (datetime.now() - start_date).days + 1

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Days on journey", days_journey)
    with c2:
        st.metric("Total check-ins", total_checkins)
    with c3:
        st.metric("Current level", level)

    if user_settings.get("motivation"):
        st.markdown(f'<div class="card"><b>Your reason:</b><br>{user_settings["motivation"]}</div>', unsafe_allow_html=True)

    if data["habits"]:
        st.subheader("Identity statements")
        for habit in data["habits"]:
            if habit.get("active", True):
                st.write(f"- I am {habit['identity']} through **{habit['name']}**")

        if st.button("🔄 Reset All Data", use_container_width=True):
            st.session_state.data = get_default_data()
            persist()
            st.success("All data reset.")
            st.rerun()
