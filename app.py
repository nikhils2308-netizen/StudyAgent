import streamlit as st

st.set_page_config(
    page_title="StudyAgent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 StudyAgent")

st.write("Your personal AI-powered life and study progress tracker.")

st.info(
    "Use the sidebar to manage your tasks, activities, "
    "AI coaching, and progress reports."
)

st.markdown("""
<style>

/* SIDEBAR CSS HERE */

</style>
""", unsafe_allow_html=True)

import streamlit as st

st.set_page_config(
    page_title="StudyAgent",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #fffafa 0%,
        #fdf5f5 50%,
        #faf1f1 100%
    );
}

[data-testid="stSidebarNav"] a {
    border-radius: 12px;
    margin: 5px 0;
    padding: 11px 14px;
    color: #705f5f !important;
    font-size: 15px;
    font-weight: 500;
}

[data-testid="stSidebarNav"] a:hover {
    background-color: #f5e4e4 !important;
}

[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: #f3e5e5 !important;
    color: #5a4040 !important;
    font-weight: 700;
    border-left: 4px solid #b87979;
}

[data-testid="stSidebarNav"]::before {
    content: "📚  StudyAgent";
    display: block;
    font-size: 22px;
    font-weight: 800;
    color: #5f4545;
    padding: 10px 12px 22px 12px;
}

</style>
""", unsafe_allow_html=True)