import streamlit as st
from datetime import date, timedelta
from database import get_connection
from groq import Groq


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Coach | StudyAgent",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# THEME
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f7f8f6;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #39443d !important;
    }

    .ai-card {
        background-color: white;
        border: 1px solid #dfe7df;
        border-radius: 18px;
        padding: 25px;
        margin-top: 15px;
        box-shadow: 0 4px 15px rgba(60, 80, 60, 0.06);
    }

    .ai-header {
        color: #39443d;
        font-size: 23px;
        font-weight: 700;
    }

    .small-text {
        color: #68736b;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.title("🤖 AI Study Coach")

st.caption(
    "Your personal AI assistant for planning, priorities and study decisions."
)


# =========================================================
# GROQ API
# =========================================================

api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY was not found.")
    st.info(
        "Add your Groq API key to .streamlit/secrets.toml"
    )
    st.stop()


client = Groq(
    api_key=api_key
)


# =========================================================
# DATES
# =========================================================

today = date.today()

tomorrow = today + timedelta(days=1)

week_start = today - timedelta(
    days=today.weekday()
)

week_end = week_start + timedelta(days=6)


# =========================================================
# GET DATABASE CONNECTION
# =========================================================

conn = get_connection()


# =========================================================
# TODAY'S TASKS
# =========================================================

today_tasks = conn.execute(
    """
    SELECT
        task,
        category,
        start_time,
        end_time,
        deadline,
        status
    FROM tasks
    WHERE task_date = ?
    ORDER BY start_time
    """,
    (str(today),)
).fetchall()
# =========================================================
# UPCOMING TASKS
# =========================================================

upcoming_tasks = conn.execute(
    """
    SELECT
        task,
        category,
        task_date,
        start_time,
        end_time,
        deadline,
        status
    FROM tasks
    WHERE task_date >= ?
      AND task_date <= ?
    ORDER BY task_date, start_time
    """,
    (
        str(today),
        str(today + timedelta(days=7))
    )
).fetchall()


# =========================================================
# RECENT ACTIVITY
# =========================================================

recent_activities = conn.execute(
    """
    SELECT
        activity_date,
        category,
        topic,
        completed,
        learned,
        notes
    FROM activity
    WHERE activity_date >= ?
      AND activity_date <= ?
    ORDER BY activity_date DESC
    """,
    (
        str(today - timedelta(days=6)),
        str(today)
    )
).fetchall()


conn.close()


# =========================================================
# TODAY STATISTICS
# =========================================================

total_today = len(today_tasks)

completed_today = sum(
    1
    for task in today_tasks
    if task[5] == "Completed"
)

pending_today = sum(
    1
    for task in today_tasks
    if task[5] == "Pending"
)


if total_today > 0:
    today_completion = round(
        completed_today / total_today * 100
    )
else:
    today_completion = 0


# =========================================================
# TODAY OVERVIEW
# =========================================================

st.subheader("📊 Today's Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "📋 Today's Tasks",
        total_today
    )


with col2:
    st.metric(
        "✅ Completed",
        completed_today
    )


with col3:
    st.metric(
        "⏳ Pending",
        pending_today
    )


with col4:
    st.metric(
        "🎯 Progress",
        f"{today_completion}%"
    )


# =========================================================
# TODAY'S TASKS
# =========================================================

st.divider()

st.subheader("📅 Today's Tasks")


if not today_tasks:

    st.info(
        "No tasks scheduled for today."
    )

else:

    for task in today_tasks:

        task_name = task[0]
        category = task[1]
        start_time = task[2]
        end_time = task[3]
        deadline = task[4]
        status = task[5]

        if status == "Completed":

            st.success(
                f"✅ **{task_name}**  \n"
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time} • "
                f"Completed"
            )

        else:

            st.warning(
                f"⏳ **{task_name}**  \n"
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time} • "
                f"Pending • "
                f"Deadline: {deadline}"
            )


# =========================================================
# PREPARE DATA FOR AI
# =========================================================

today_text = ""

if today_tasks:

    for task in today_tasks:

        today_text += (
            f"Task: {task[0]} | "
            f"Category: {task[1]} | "
            f"Time: {task[2]}-{task[3]} | "
            f"Deadline: {task[4]} | "
            f"Status: {task[5]}\n"
        )

else:

    today_text = "NO TASKS SCHEDULED TODAY."


upcoming_text = ""

if upcoming_tasks:

    for task in upcoming_tasks:

        upcoming_text += (
            f"Task: {task[0]} | "
            f"Category: {task[1]} | "
            f"Date: {task[2]} | "
            f"Time: {task[3]}-{task[4]} | "
            f"Deadline: {task[5]} | "
            f"Status: {task[6]}\n"
        )

else:

    upcoming_text = "NO UPCOMING TASKS."


activity_text = ""

if recent_activities:

    for activity in recent_activities:

        activity_text += (
            f"Date: {activity[0]} | "
            f"Category: {activity[1]} | "
            f"Topic: {activity[2]} | "
            f"Completed: {activity[3]} | "
            f"Learned: {activity[4]} | "
            f"Notes: {activity[5]}\n"
        )

else:

    activity_text = "NO RECENT ACTIVITY."


# =========================================================
# AI RECOMMENDATIONS
# =========================================================

st.divider()

st.subheader("🧠 Smart Daily Recommendations")

st.write(
    "Ask your AI Coach what you should focus on today."
)


if st.button(
    "🎯 What Should I Do Today?",
    use_container_width=True
):

    prompt = f"""
You are a personal AI study coach.

Today is {today}.

Analyze ONLY the real information provided below.

IMPORTANT RULES:

- Never invent a task.
- Never invent an activity.
- Never invent a deadline.
- Never invent a study session.
- Never assume the student worked on something.
- Never mention an activity unless it appears in the activity data.
- Never mention a task unless it appears in the task data.
- Never create fake schedules.
- Never claim duplicate entries unless duplicates are clearly visible.
- Use the exact task names from the data.
- If information is unavailable, say so.

TODAY'S TASKS:

{today_text}


UPCOMING TASKS:

{upcoming_text}


RECENT ACTIVITY:

{activity_text}


TODAY'S STATISTICS:

Total tasks: {total_today}

Completed tasks: {completed_today}

Pending tasks: {pending_today}

Completion rate: {today_completion}%


YOUR JOB:

Determine what the student should focus on.

Prioritize using:

1. Deadline
2. Pending status
3. Scheduled time
4. Existing workload


RESPONSE FORMAT:

🎯 TOP PRIORITY

Choose ONE existing pending task.

Explain why it should be done first.

If there are no pending tasks, say:

No pending task requires attention.


🔥 SECOND PRIORITY

Choose the second most important EXISTING task if one exists.

If there is no second task, say:

No second priority is available.


⏰ TODAY'S PLAN

Use ONLY existing tasks.

Do not invent new activities.

If there are no tasks today, say:

No tasks are scheduled for today.


⚠️ WARNING

Mention only real problems visible in the data.

Examples:

- deadline today
- overdue task
- pending task
- heavy workload

If there is no warning, say:

No critical warning.


💡 COACH TIP

Give ONE practical suggestion based directly on the supplied data.

Do not give generic motivational advice.

Keep the response concise and practical.
"""


    # =====================================================
    # CALL GROQ
    # =====================================================

    with st.spinner(
        "🧠 AI Coach is analyzing your study data..."
    ):

        try:

            response = client.chat.completions.create(

                model="openai/gpt-oss-20b",

                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a practical personal "
                            "study coach. Use only the "
                            "information supplied by the "
                            "user. Never invent information."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.2,

                max_tokens=900
            )


            recommendation = (
                response
                .choices[0]
                .message
                .content
            )


            # =============================================
            # DISPLAY RESPONSE
            # =============================================

            st.markdown(
                """
                <div class="ai-card">
                <div class="ai-header">
                🤖 Your AI Coach
                </div>

                <br>

                <div class="small-text">
                Based on your current tasks,
                deadlines and recent activity.
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                recommendation
            )


        except Exception as e:

            st.error(
                "❌ Groq request failed."
            )

            st.code(
                str(e)
            )


# =========================================================
# DEADLINE WATCH
# =========================================================

st.divider()

st.subheader("⚠️ Deadline Watch")


deadline_found = False


for task in upcoming_tasks:

    task_name = task[0]
    category = task[1]
    task_deadline = task[5]
    status = task[6]


    if status == "Completed":
        continue


    if not task_deadline:
        continue


    try:

        deadline_date = date.fromisoformat(
            task_deadline
        )

    except ValueError:

        continue


    days_left = (
        deadline_date - today
    ).days


    if days_left < 0:

        deadline_found = True

        st.error(
            f"🔴 **{task_name}** — "
            f"{category} — "
            f"OVERDUE by {abs(days_left)} day(s)"
        )


    elif days_left == 0:

        deadline_found = True

        st.error(
            f"🔴 **{task_name}** — "
            f"{category} — "
            f"Due TODAY"
        )

# =========================================================

st.divider()

st.subheader("📖 Recent Activity")


if not recent_activities:

    st.info(
        "No recent activity recorded."
    )

else:

    for activity in recent_activities[:8]:

        activity_date = activity[0]
        category = activity[1]
        topic = activity[2]
        completed = activity[3]


        if completed:

            st.success(
                f"✅ **{topic}** — "
                f"{category} — "
                f"{activity_date}"
            )

        else:

            st.warning(
                f"⏳ **{topic}** — "
                f"{category} — "
                f"{activity_date}"
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🤖 StudyAgent AI Coach • "
    "Recommendations are generated from your study data."
)