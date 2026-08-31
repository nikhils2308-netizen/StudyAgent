import sqlite3

DB_NAME = "study.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # TASKS TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            category TEXT,
            task_date TEXT,
            start_time TEXT,
            end_time TEXT,
            deadline TEXT,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Medium'
        )
    """)

    # =====================================================
    # ACTIVITY TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_date TEXT,
            category TEXT,
            start_time TEXT,
            end_time TEXT,
            topic TEXT,
            learned TEXT,
            completed INTEGER DEFAULT 0,
            notes TEXT
        )
    """)

    # =====================================================
    # DAILY LOG TABLE
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_log (
            date TEXT,
            communication INTEGER,
            dsa INTEGER,
            verilog INTEGER,
            german INTEGER,
            english_video INTEGER,
            communication_minutes INTEGER,
            dsa_minutes INTEGER,
            verilog_minutes INTEGER,
            german_minutes INTEGER,
            notes TEXT
        )
    """)

    conn.commit()

    # =====================================================
    # ADD PRIORITY TO OLD DATABASE
    # =====================================================

    cursor.execute("PRAGMA table_info(tasks)")

    columns = cursor.fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "priority" not in column_names:

        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN priority TEXT DEFAULT 'Medium'
        """)

    conn.commit()
    conn.close()


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

create_tables()