import streamlit as st
from datetime import date, timedelta
from database import get_connection


st.set_page_config(
    page_title="StudyAgent",
    page_icon="📚",
    layout="wide"
)

# ---------- CSS ----------
st.markdown("""
<style>

.stApp {
    background-color: #fdf7f7;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #5f4b4b !important;
}

p {
    color: #6f5c5c;
}

[data-testid="stMetric"] {
    background-color: #fffafa;
    border: 1px solid #eadada;
    padding: 20px;
    border-radius: 18px;
}

[data-testid="stMetricLabel"] {
    color: #8a7777 !important;
}

[data-testid="stMetricValue"] {
    color: #594646 !important;
}

hr {
    border-color: #eadada;
}

</style>
""", unsafe_allow_html=True)


# ---------- DATE ----------

today = date.today()


# ---------- DATABASE ----------

conn = get_connection()

tasks = conn.execute(
    """
    SELECT status
    FROM tasks
    WHERE task_date = ?
    """,
    (str(today),)
).fetchall()


completed_dates = conn.execute(
    """
    SELECT DISTINCT activity_date
    FROM activity
    WHERE completed = 1
    """
).fetchall()

conn.close()


# ---------- STATISTICS ----------

total_tasks = len(tasks)

completed_tasks = sum(
    1 for task in tasks
    if task[0] == "Completed"
)

pending_tasks = sum(
    1 for task in tasks
    if task[0] == "Pending"
)


if total_tasks > 0:
    progress = int(
        completed_tasks / total_tasks * 100
    )
else:
    progress = 0


# ---------- STREAK ----------

completed_dates = {
    row[0]
    for row in completed_dates
}

streak = 0
check_date = today

while str(check_date) in completed_dates:

    streak += 1

    check_date -= timedelta(days=1)

    if streak > 365:
        break


# =========================================================
# HEADER
# =========================================================

st.title("📚 StudyAgent")

st.caption(
    f"Your personal AI-powered study command center • "
    f"{today.strftime('%A, %d %B %Y')}"
)

st.divider()


# =========================================================
# KPI
# =========================================================

st.subheader("📊 Today's Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "🔥 Current Streak",
        f"{streak} days"
    )


with col2:
    st.metric(
        "🎯 Today's Progress",
        f"{progress}%"
    )


with col3:
    st.metric(
        "📋 Pending Tasks",
        pending_tasks
    )


with col4:
    st.metric(
        "📚 Total Tasks",
        total_tasks
    )


st.divider()


# =========================================================
# PROGRESS
# =========================================================

st.subheader("🎯 Today's Progress")

st.progress(
    progress / 100
)

st.caption(
    f"{completed_tasks} of {total_tasks} tasks completed"
)

st.divider()


# =========================================================
# STATUS
# =========================================================

if total_tasks == 0:

    st.info(
        "📅 You don't have any tasks scheduled for today."
    )

elif progress == 100:

    st.success(
        "🔥 Excellent! You've completed everything "
        "planned for today."
    )

elif progress >= 50:

    st.warning(
        "💪 You're halfway there. Keep going!"
    )

else:

    st.info(
        "🚀 Start with your highest-priority task."
    )


# =========================================================
# TODAY'S SCHEDULE
# =========================================================

st.divider()

st.subheader("📅 Today's Schedule")

conn = get_connection()

today_tasks = conn.execute(
    """
    SELECT
        task,
        category,
        start_time,
        end_time,
        status
    FROM tasks
    WHERE task_date = ?
    ORDER BY start_time
    """,
    (str(today),)
).fetchall()

conn.close()


if not today_tasks:

    st.info("No tasks scheduled for today.")

else:

    for task in today_tasks:

        task_name = task[0]
        category = task[1]
        start_time = task[2]
        end_time = task[3]
        status = task[4]

        if status == "Completed":

            st.success(
                f"✅ **{task_name}**  \n"
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time} • "
                f"Completed"
            )

        else:

            st.info(
                f"⏳ **{task_name}**  \n"
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time} • "
                f"{status}"
            )


# =========================================================
# UPCOMING DEADLINES
# =========================================================

st.divider()

st.subheader("⚠️ Upcoming Deadlines")

conn = get_connection()

deadline_tasks = conn.execute(
    """
    SELECT
        task,
        category,
        deadline,
        status
    FROM tasks
    WHERE deadline IS NOT NULL
      AND deadline != ''
      AND status != 'Completed'
    ORDER BY deadline
    """
).fetchall()

conn.close()


upcoming_found = False

for task in deadline_tasks:

    task_name = task[0]
    category = task[1]
    deadline = task[2]
    status = task[3]

    try:

        deadline_date = date.fromisoformat(
            deadline
        )

    except ValueError:

        continue


    days_left = (
        deadline_date - today
    ).days


    if days_left > 7:
        continue


    upcoming_found = True


    if days_left < 0:

        st.error(
            f"🔴 **{task_name}**  \n"
            f"📚 {category}  •  "
            f"Deadline: {deadline}  \n"
            f"⚠️ **OVERDUE by {abs(days_left)} day(s)**"
        )


    elif days_left == 0:

        st.error(
            f"🔴 **{task_name}**  \n"
            f"📚 {category}  •  "
            f"Deadline: {deadline}  \n"
            f"🔥 **Due TODAY**"
        )


    elif days_left == 1:

        st.warning(
            f"🟠 **{task_name}**  \n"
            f"📚 {category}  •  "
            f"Deadline: {deadline}  \n"
            f"⏰ **Due TOMORROW**"
        )


    else:

        st.info(
            f"🔵 **{task_name}**  \n"
            f"📚 {category}  •  "
            f"Deadline: {deadline}  \n"
            f"📅 **{days_left} days remaining**"
        )


if not upcoming_found:

    st.success(
        "🎉 No urgent deadlines in the next 7 days!"
    )


# =========================================================
# TODAY'S ACTIVITY
# =========================================================

st.divider()

st.subheader("📖 Today's Activity")

conn = get_connection()

activities = conn.execute(
    """
    SELECT
        category,
        start_time,
        end_time,
        topic,
        completed
    FROM activity
    WHERE activity_date = ?
    ORDER BY start_time
    """,
    (str(today),)
).fetchall()

conn.close()


if not activities:

    st.info(
        "📖 No study activity recorded today yet."
    )

else:

    for activity in activities:

        category = activity[0]
        start_time = activity[1]
        end_time = activity[2]
        topic = activity[3]
        completed = activity[4]


        if completed:

            st.success(
                f"✅ **{topic or 'Study Session'}**  \n"
                f"📚 {category}  •  "
                f"🕐 {start_time} - {end_time}  \n"
                f"Completed"
            )


        else:

            st.warning(
                f"⏳ **{topic or 'Study Session'}**  \n"
                f"📚 {category}  •  "
                f"🕐 {start_time} - {end_time}  \n"
                f"Not completed"
            )


# =========================================================
# TOMORROW'S PLAN
# =========================================================

st.divider()

st.subheader("🌅 Tomorrow's Plan")

conn = get_connection()

tomorrow_tasks = conn.execute(
    """
    SELECT
        task,
        category,
        start_time,
        end_time,
        status
    FROM tasks
    WHERE task_date = ?
    ORDER BY start_time
    """,
    (str(today + timedelta(days=1)),)
).fetchall()

conn.close()


if not tomorrow_tasks:

    st.info(
        "📅 No tasks planned for tomorrow yet."
    )

else:

    st.write(
        f"Here is what you have planned for "
        f"**{(today + timedelta(days=1)).strftime('%A, %d %B')}**:"
    )

    for task in tomorrow_tasks:

        task_name = task[0]
        category = task[1]
        start_time = task[2]
        end_time = task[3]
        status = task[4]

        if status == "Completed":

            st.success(
                f"✅ **{task_name}**  \n"
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time}"
            )

        else:

            st.info(
                f"📌 **{task_name}**  \n"
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time}"
            )