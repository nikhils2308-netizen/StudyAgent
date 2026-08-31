import streamlit as st
from datetime import date, time
from database import get_connection


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Tasks | StudyAgent",
    page_icon="📝",
    layout="wide"
)


# =========================================================
# LIGHT CALM THEME
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f8f6f4;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #514747 !important;
}

p {
    color: #706565;
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e7dfdc;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 3px 10px rgba(80, 60, 60, 0.05);
}

[data-testid="stMetricLabel"] {
    color: #766b68 !important;
}

[data-testid="stMetricValue"] {
    color: #514747 !important;
}

.stButton > button {
    border-radius: 10px;
    border: 1px solid #ddd2ce;
}

hr {
    border-color: #e7dfdc;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.title("📝 My Tasks")

st.caption(
    "Plan, prioritize, edit and manage your study tasks."
)


# =========================================================
# TODAY
# =========================================================

today = date.today()


# =========================================================
# MARK MISSED TASKS
# =========================================================

conn = get_connection()

conn.execute(
    """
    UPDATE tasks
    SET status = 'Not Completed'
    WHERE task_date < ?
      AND status = 'Pending'
    """,
    (str(today),)
)

conn.commit()
conn.close()


# =========================================================
# SUMMARY
# =========================================================

conn = get_connection()

summary_tasks = conn.execute(
    """
    SELECT status
    FROM tasks
    WHERE task_date = ?
    """,
    (str(today),)
).fetchall()

conn.close()


total_tasks = len(summary_tasks)

completed_tasks = sum(
    1 for task in summary_tasks
    if task[0] == "Completed"
)

pending_tasks = sum(
    1 for task in summary_tasks
    if task[0] == "Pending"
)

if total_tasks > 0:
    progress = int(
        completed_tasks / total_tasks * 100
    )
else:
    progress = 0


# =========================================================
# OVERVIEW
# =========================================================

st.subheader("📊 Today's Overview")

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
        "⏳ Pending",
        pending_tasks
    )

with col4:
    st.metric(
        "🎯 Progress",
        f"{progress}%"
    )

st.progress(progress / 100)

st.caption(
    f"{completed_tasks} of {total_tasks} tasks completed today"
)


# =========================================================
# CREATE TASK
# =========================================================

st.divider()

st.subheader("➕ Create New Task")

with st.form("create_task"):

    task_name = st.text_input(
        "Task name",
        placeholder="Example: Complete LeetCode arrays"
    )

    col1, col2 = st.columns(2)

    with col1:

        category = st.selectbox(
            "Category",
            [
                "DSA",
                "Verilog",
                "Communication",
                "English",
                "German",
                "College",
                "Project",
                "Other"
            ]
        )

    with col2:

        priority = st.selectbox(
            "Priority",
            [
                "High",
                "Medium",
                "Low"
            ]
        )

    col3, col4 = st.columns(2)

    with col3:

        task_date = st.date_input(
            "Task date",
            value=today
        )

    with col4:

        deadline = st.date_input(
            "Deadline",
            value=today
        )

    col5, col6 = st.columns(2)

    with col5:

        start_time = st.time_input(
            "Start time",
            value=time(18, 0)
        )

    with col6:

        end_time = st.time_input(
            "End time",
            value=time(19, 0)
        )

    submitted = st.form_submit_button(
        "➕ Create Task",
        use_container_width=True
    )


# =========================================================
# SAVE NEW TASK
# =========================================================

if submitted:

    if not task_name.strip():

        st.error(
            "Please enter a task name."
        )

    elif end_time <= start_time:

        st.error(
            "End time must be after start time."
        )

    elif task_date < today:

        st.error(
            "Task date cannot be in the past."
        )

    elif deadline < task_date:

        st.error(
            "Deadline cannot be before task date."
        )

    else:

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO tasks
            (
                task,
                category,
                task_date,
                start_time,
                end_time,
                deadline,
                status,
                priority
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_name.strip(),
                category,
                str(task_date),
                str(start_time),
                str(end_time),
                str(deadline),
                "Pending",
                priority
            )
        )

        conn.commit()
        conn.close()

        st.success(
            "✅ Task created successfully!"
        )

        st.rerun()


# =========================================================
# TODAY'S TASKS
# =========================================================

st.divider()

st.subheader("📅 Today's Tasks")


conn = get_connection()

today_tasks = conn.execute(
    """
    SELECT
        id,
        task,
        category,
        task_date,
        start_time,
        end_time,
        deadline,
        status,
        priority
    FROM tasks
    WHERE task_date = ?
    ORDER BY
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
            ELSE 4
        END,
        start_time
    """,
    (str(today),)
).fetchall()

conn.close()


if not today_tasks:

    st.info(
        "📅 No tasks scheduled for today."
    )

else:

    for task in today_tasks:

        task_id = task[0]
        task_name = task[1]
        category = task[2]
        task_date_value = task[3]
        start_time = task[4]
        end_time = task[5]
        deadline = task[6]
        status = task[7]
        priority = task[8]

        if priority == "High":
            priority_icon = "🔴"
        elif priority == "Medium":
            priority_icon = "🟡"
        else:
            priority_icon = "🟢"


        # =================================================
        # COMPLETED TASK
        # =================================================

        if status == "Completed":

            st.success(
                f"✅ **{task_name}**  \n"
                f"{priority_icon} {priority} Priority • "
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time}  \n"
                f"📅 Deadline: {deadline}"
            )

        else:

            st.info(
                f"⏳ **{task_name}**  \n"
                f"{priority_icon} {priority} Priority • "
                f"📚 {category} • "
                f"🕐 {start_time} - {end_time}  \n"
                f"📅 Deadline: {deadline}"
            )


        # =================================================
        # ACTION BUTTONS
        # =================================================

        col1, col2, col3 = st.columns(3)


        # -------------------------------------------------
        # COMPLETE
        # -------------------------------------------------

        with col1:

            if status != "Completed":

                if st.button(
                    "✅ Complete",
                    key=f"complete_{task_id}",
                    use_container_width=True
                ):

                    conn = get_connection()

                    conn.execute(
                        """
                        UPDATE tasks
                        SET status = 'Completed'
                        WHERE id = ?
                        """,
                        (task_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.rerun()


        # -------------------------------------------------
        # EDIT
        # -------------------------------------------------

        with col2:

            if st.button(
                "✏️ Edit",
                key=f"edit_{task_id}",
                use_container_width=True
            ):

                st.session_state[
                    "editing_task"
                ] = task_id

                st.rerun()


        # -------------------------------------------------
        # DELETE
        # -------------------------------------------------

        with col3:

            if st.button(
                "🗑️ Delete",
                key=f"delete_{task_id}",
                use_container_width=True
            ):

                st.session_state[
                    "delete_task"
                ] = task_id

                st.rerun()


        # =================================================
        # EDIT FORM
        # =================================================

        if st.session_state.get(
            "editing_task"
        ) == task_id:

            st.markdown("---")

            st.subheader(
                f"✏️ Edit: {task_name}"
            )

            with st.form(
                f"edit_form_{task_id}"
            ):

                new_name = st.text_input(
                    "Task name",
                    value=task_name
                )

                edit_col1, edit_col2 = st.columns(2)

                with edit_col1:

                    new_category = st.selectbox(
                        "Category",
                        [
                            "DSA",
                            "Verilog",
                            "Communication",
                            "English",
                            "German",
                            "College",
                            "Project",
                            "Other"
                        ],
                        index=[
                            "DSA",
                            "Verilog",
                            "Communication",
                            "English",
                            "German",
                            "College",
                            "Project",
                            "Other"
                        ].index(category)
                        if category in [
                            "DSA",
                            "Verilog",
                            "Communication",
                            "English",
                            "German",
                            "College",
                            "Project",
                            "Other"
                        ]
                        else 0
                    )

                with edit_col2:

                    new_priority = st.selectbox(
                        "Priority",
                        [
                            "High",
                            "Medium",
                            "Low"
                        ],
                        index=[
                            "High",
                            "Medium",
                            "Low"
                        ].index(priority)
                        if priority in [
                            "High",
                            "Medium",
                            "Low"
                        ]
                        else 1
                    )


                edit_col3, edit_col4 = st.columns(2)

                with edit_col3:

                    new_date = st.date_input(
                        "Task date",
                        value=date.fromisoformat(
                            task_date_value
                        )
                    )

                with edit_col4:

                    new_deadline = st.date_input(
                        "Deadline",
                        value=date.fromisoformat(
                            deadline
                        )
                    )


                edit_col5, edit_col6 = st.columns(2)

                with edit_col5:

                    new_start = st.time_input(
                        "Start time",
                        value=time.fromisoformat(
                            start_time
                        )
                    )

                with edit_col6:

                    new_end = st.time_input(
    "End time",
    value=time.fromisoformat(
        end_time
    )
)


                new_status = st.selectbox(
                    "Status",
                    [
                        "Pending",
                        "Completed",
                        "Not Completed"
                    ],
                    index=[
                        "Pending",
                        "Completed",
                        "Not Completed"
                    ].index(status)
                    if status in [
                        "Pending",
                        "Completed",
                        "Not Completed"
                    ]
                    else 0
                )


                save_edit = st.form_submit_button(
                    "💾 Save Changes",
                    use_container_width=True
                )


            if save_edit:

                if not new_name.strip():

                    st.error(
                        "Task name cannot be empty."
                    )

                elif new_end <= new_start:

                    st.error(
                        "End time must be after start time."
                    )

                elif new_deadline < new_date:

                    st.error(
                        "Deadline cannot be before task date."
                    )

                else:

                    conn = get_connection()

                    conn.execute(
                        """
                        UPDATE tasks
                        SET
                            task = ?,
                            category = ?,
                            task_date = ?,
                            start_time = ?,
                            end_time = ?,
                            deadline = ?,
                            status = ?,
                            priority = ?
                        WHERE id = ?
                        """,
                        (
                            new_name.strip(),
                            new_category,
                            str(new_date),
                            str(new_start),
                            str(new_end),
                            str(new_deadline),
                            new_status,
                            new_priority,
                            task_id
                        )
                    )

                    conn.commit()
                    conn.close()

                    st.session_state[
                        "editing_task"
                    ] = None

                    st.success(
                        "✅ Task updated successfully!"
                    )

                    st.rerun()


        # =================================================
        # DELETE CONFIRMATION
        # =================================================

        if st.session_state.get(
            "delete_task"
        ) == task_id:

            st.warning(
                f"⚠️ Are you sure you want to delete "
                f"**{task_name}**?"
            )

            delete_col1, delete_col2 = st.columns(2)

            with delete_col1:

                if st.button(
                    "🗑️ Yes, Delete",
                    key=f"confirm_delete_{task_id}",
                    use_container_width=True
                ):

                    conn = get_connection()

                    conn.execute(
                        """
                        DELETE FROM tasks
                        WHERE id = ?
                        """,
                        (task_id,)
                    )

                    conn.commit()
                    conn.close()

                    st.session_state[
                        "delete_task"
                    ] = None

                    st.success(
                        "🗑️ Task deleted."
                    )

                    st.rerun()


            with delete_col2:

                if st.button(
                    "❌ Cancel",
                    key=f"cancel_delete_{task_id}",
                    use_container_width=True
                ):

                    st.session_state[
                        "delete_task"
                    ] = None

                    st.rerun()


# =========================================================
# BACKLOG
# =========================================================

st.divider()

st.subheader("📦 Backlog")

st.caption(
    "Previous tasks that were not completed."
)


conn = get_connection()

backlog_tasks = conn.execute(
    """
    SELECT
        id,
        task,
        category,
        task_date,
        start_time,
        end_time,
        deadline,
        status,
        priority
    FROM tasks
    WHERE task_date < ?
      AND status = 'Not Completed'
    ORDER BY
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
            ELSE 4
        END,
        task_date DESC
    """,
    (str(today),)
).fetchall()

conn.close()


if not backlog_tasks:

    st.success(
        "🎉 Your backlog is empty!"
    )

else:

    st.warning(
        f"⚠️ {len(backlog_tasks)} "
        f"unfinished task(s) in backlog."
    )


    for task in backlog_tasks:

        task_id = task[0]
        task_name = task[1]
        category = task[2]
        old_date = task[3]
        old_start = task[4]
        old_end = task[5]
        deadline = task[6]
        priority = task[8]


        if priority == "High":
            priority_icon = "🔴"
        elif priority == "Medium":
            priority_icon = "🟡"
        else:
            priority_icon = "🟢"


        try:

            old_date_obj = date.fromisoformat(
                old_date
            )

            missed_days = (
                today - old_date_obj
            ).days

        except ValueError:

            missed_days = 0


        st.error(
            f"❌ **{task_name}**  \n"
            f"{priority_icon} {priority} Priority • "
            f"📚 {category}  \n"
            f"📅 Missed: {old_date} • "
            f"{missed_days} day(s) ago  \n"
            f"🕐 Original time: "
            f"{old_start} - {old_end}"
        )


        col1, col2 = st.columns(2)


        with col1:

            if st.button(
                "🔄 Move to Today",
                key=f"move_{task_id}",
                use_container_width=True
            ):

                conn = get_connection()

                conn.execute(
                    """
                    UPDATE tasks
                    SET
                        task_date = ?,
                        status = 'Pending'
                    WHERE id = ?
                    """,
                    (
                        str(today),
                        task_id
                    )
                )

                conn.commit()
                conn.close()

                st.success(
                    "🔄 Task moved to today."
                )

                st.rerun()


        with col2:

            if st.button(
                "🗑️ Remove",
                key=f"backlog_delete_{task_id}",
                use_container_width=True
            ):

                conn = get_connection()

                conn.execute(
                    """
                    DELETE FROM tasks
                    WHERE id = ?
                    """,
                    (task_id,)
                )

                conn.commit()
                conn.close()

                st.success(
                    "🗑️ Task removed."
                )

                st.rerun()


# =========================================================
# UPCOMING TASKS
# =========================================================

st.divider()

st.subheader("📆 Upcoming Tasks")


conn = get_connection()

future_tasks = conn.execute(
    """
    SELECT
        task,
        category,
        task_date,
        start_time,
        end_time,
        deadline,
        status,
        priority
    FROM tasks
    WHERE task_date > ?
    ORDER BY
        task_date,
        CASE priority
            WHEN 'High' THEN 1
            WHEN 'Medium' THEN 2
            WHEN 'Low' THEN 3
            ELSE 4
        END,
        start_time
    """,
    (str(today),)
).fetchall()

conn.close()


if not future_tasks:

    st.info(
        "📅 No upcoming tasks."
    )

else:

    for task in future_tasks:

        task_name = task[0]
        category = task[1]
        task_date_value = task[2]
        start_time = task[3]
        end_time = task[4]
        deadline = task[5]
        status = task[6]
        priority = task[7]


        if priority == "High":
            priority_icon = "🔴"
        elif priority == "Medium":
            priority_icon = "🟡"
        else:
            priority_icon = "🟢"


        st.info(
            f"📌 **{task_name}**  \n"
            f"{priority_icon} {priority} Priority • "
            f"📚 {category}  \n"
            f"📅 {task_date_value} • "
            f"🕐 {start_time} - {end_time}  \n"
            f"📅 Deadline: {deadline}"
        )