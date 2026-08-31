
import streamlit as st
from datetime import date, time
from database import get_connection


# =========================================================
# LIGHT GREEN BACKGROUND
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #e8f5e9;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITLE
# =========================================================

st.title("📖 Today's Activity")

st.write(
    "Record what you actually worked on today."
)


# =========================================================
# ACTIVITY DATE
# =========================================================

activity_date = st.date_input(
    "Date",
    value=date.today()
)


# =========================================================
# CATEGORY
# =========================================================

category = st.selectbox(
    "What did you work on?",
    [
        "DSA",
        "Communication",
        "Verilog",
        "German",
        "English",
        "Electronics",
        "Personal",
        "Other"
    ]
)


# =========================================================
# ACTUAL TIME
# =========================================================

st.subheader("⏰ Actual Time")

start_time = st.time_input(
    "Start Time",
    value=time(18, 0)
)

end_time = st.time_input(
    "End Time",
    value=time(19, 0)
)


if end_time <= start_time:

    st.error(
        "End time must be after start time."
    )


# =========================================================
# WHAT DID YOU DO?
# =========================================================

st.subheader("📚 What did you work on?")

topic = st.text_input(
    "Topic",
    placeholder="Example: Binary Search"
)


# =========================================================
# WHAT DID YOU LEARN?
# =========================================================

learned = st.text_area(
    "What did you learn?",
    placeholder="Write what you understood today..."
)


# =========================================================
# COMPLETION
# =========================================================

completed = st.checkbox(
    "I completed this activity"
)


# =========================================================
# NOTES
# =========================================================

notes = st.text_area(
    "Notes",
    placeholder="Any problems, doubts, or observations?"
)


# =========================================================
# SAVE
# =========================================================

if st.button("💾 Save Activity"):

    if end_time <= start_time:

        st.error(
            "Please select a valid time range."
        )

    elif topic.strip() == "":

        st.warning(
            "Please enter what you worked on."
        )

    else:

        conn = get_connection()

        conn.execute(
            """
            INSERT INTO activity
            (
                activity_date,
                category,
                start_time,
                end_time,
                topic,
                learned,
                completed,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(activity_date),
                category,
                str(start_time),
                str(end_time),
                topic,
                learned,
                int(completed),
                notes
            )
        )

        conn.commit()
        conn.close()

        st.success(
            "✅ Activity saved successfully!"
        )

        st.rerun()


# =========================================================
# ACTIVITY HISTORY
# =========================================================

st.divider()

st.subheader("📋 Activity History")

conn = get_connection()

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
    ORDER BY activity_date DESC, start_time DESC
    """
).fetchall()

conn.close()


if not activities:

    st.info(
        "No activities recorded yet."
    )

else:

    for row in activities:

        (
            activity_date_value,
            activity_category,
            activity_start,
            activity_end,
            activity_topic,
            activity_completed
        ) = row

        if activity_completed:

            st.success(
                f"✅ {activity_date_value} | "
                f"{activity_start} → {activity_end} | "
                f"{activity_category} | "
                f"{activity_topic}"
            )

        else:

            st.warning(
                f"⏳ {activity_date_value} | "
                f"{activity_start} → {activity_end} | "
                f"{activity_category} | "
                f"{activity_topic}"
            )
