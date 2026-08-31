import streamlit as st
from datetime import date, timedelta
from database import get_connection


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Weekly Stats | StudyAgent",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# CALM LIGHT THEME
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f7f8f6;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #39443d !important;
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #dfe7df;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 3px 10px rgba(60, 80, 60, 0.05);
}

[data-testid="stMetricLabel"] {
    color: #66736a !important;
}

[data-testid="stMetricValue"] {
    color: #39443d !important;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATE RANGE
# =========================================================

today = date.today()

week_start = today - timedelta(days=today.weekday())

week_end = week_start + timedelta(days=6)


# =========================================================
# HEADER
# =========================================================

st.title("📊 Weekly Statistics")

st.caption(
    f"{week_start.strftime('%d %B')} → "
    f"{week_end.strftime('%d %B %Y')}"
)


# =========================================================
# GET TASK DATA
# =========================================================

conn = get_connection()

tasks = conn.execute(
    """
    SELECT
        task,
        category,
        task_date,
        status,
        priority
    FROM tasks
    WHERE task_date >= ?
      AND task_date <= ?
    ORDER BY task_date
    """,
    (
        str(week_start),
        str(week_end)
    )
).fetchall()


# =========================================================
# GET ACTIVITY DATA
# =========================================================

activities = conn.execute(
    """
    SELECT
        activity_date,
        category,
        start_time,
        end_time,
        topic,
        completed
    FROM activity
    WHERE activity_date >= ?
      AND activity_date <= ?
    ORDER BY activity_date
    """,
    (
        str(week_start),
        str(week_end)
    )
).fetchall()

conn.close()


# =========================================================
# TASK STATISTICS
# =========================================================

total_tasks = len(tasks)

completed_tasks = sum(
    1
    for task in tasks
    if task[3] == "Completed"
)

pending_tasks = sum(
    1
    for task in tasks
    if task[3] == "Pending"
)

missed_tasks = sum(
    1
    for task in tasks
    if task[3] == "Not Completed"
)


if total_tasks > 0:

    completion_rate = round(
        completed_tasks / total_tasks * 100
    )

else:

    completion_rate = 0


# =========================================================
# ACTIVITY STATISTICS
# =========================================================

total_activities = len(activities)

completed_activities = sum(
    1
    for activity in activities
    if activity[5] == 1
)


# =========================================================
# HEADER METRICS
# =========================================================

st.subheader("🎯 Weekly Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📋 Total Tasks",
        total_tasks
    )

with col2:

    st.metric(
        "✅ Completed",
        completed_tasks
    )

with col3:

    st.metric(
        "❌ Missed",
        missed_tasks
    )

with col4:

    st.metric(
        "🎯 Completion",
        f"{completion_rate}%"
    )


# =========================================================
# PROGRESS
# =========================================================

st.divider()

st.subheader("📈 Task Completion")

st.progress(
    completion_rate / 100
)

st.caption(
    f"You completed {completed_tasks} "
    f"out of {total_tasks} tasks."
)


# =========================================================
# DAILY BREAKDOWN
# =========================================================

st.divider()

st.subheader("📅 Daily Breakdown")


days = []

for i in range(7):

    current_day = week_start + timedelta(days=i)

    day_tasks = [
        task
        for task in tasks
        if task[2] == str(current_day)
    ]

    day_total = len(day_tasks)

    day_completed = sum(
        1
        for task in day_tasks
        if task[3] == "Completed"
    )

    if day_total > 0:

        day_progress = round(
            day_completed / day_total * 100
        )

    else:

        day_progress = 0


    days.append(
        (
            current_day,
            day_total,
            day_completed,
            day_progress
        )
    )


for current_day, day_total, day_completed, day_progress in days:

    col1, col2, col3 = st.columns(
        [2, 1, 4]
    )


    with col1:

        if current_day == today:

            st.write(
                f"**🟢 Today — "
                f"{current_day.strftime('%A')}**"
            )

        else:

            st.write(
                f"**{current_day.strftime('%A')}**"
            )


    with col2:

        st.write(
            f"{day_completed}/{day_total}"
        )


    with col3:

        st.progress(
            day_progress / 100
        )


# =========================================================
# CATEGORY BREAKDOWN
# =========================================================

st.divider()

st.subheader("📚 Study by Category")


category_counts = {}


for activity in activities:

    category = activity[1]

    if category not in category_counts:

        category_counts[category] = 0

    category_counts[category] += 1


if not category_counts:

    st.info(
        "No activity recorded this week."
    )

else:

    for category, count in sorted(
        category_counts.items(),
        key=lambda x: x[1],
        reverse=True
    ):

        st.write(
            f"📚 **{category}** — "
            f"{count} session(s)"
        )


# =========================================================
# ACTIVITY SUMMARY
# =========================================================

st.divider()

st.subheader("⏱️ Activity Summary")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "📖 Study Sessions",
        total_activities
    )

with col2:

    st.metric(
        "✅ Completed Sessions",
        completed_activities
    )


# =========================================================
# WEEKLY STATUS
# =========================================================

st.divider()

st.subheader("💡 Weekly Status")


if total_tasks == 0:

    st.info(
        "📅 No tasks were planned this week yet."
    )

elif completion_rate >= 80:

    st.success(
        "🔥 Excellent week! "
        "You maintained a strong task completion rate."
    )

elif completion_rate >= 60:

    st.warning(
        "💪 Good progress! "
        "Try to reduce the number of missed tasks next week."
    )

else:

    st.error(
        "⚠️ Your completion rate is low this week. "
        "Consider planning fewer tasks and completing them consistently."
    )


# =========================================================
# MISSED TASKS
# =========================================================

st.divider()

st.subheader("❌ Missed Tasks")


missed = [
    task
    for task in tasks
    if task[3] == "Not Completed"
]


if not missed:

    st.success(
        "🎉 No missed tasks this week!"
    )

else:

    for task in missed:

        task_name = task[0]
        category = task[1]
        task_date = task[2]
        priority = task[4]

        st.warning(
            f"❌ **{task_name}**  \n"
            f"📚 {category} • "
            f"📅 {task_date} • "
            f"Priority: {priority}"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "📊 StudyAgent • Weekly statistics generated from your local study data."
)