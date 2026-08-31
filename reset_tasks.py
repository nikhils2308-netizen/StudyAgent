from database import get_connection

conn = get_connection()

conn.execute("DROP TABLE IF EXISTS tasks")

conn.execute("""
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    category TEXT NOT NULL,
    task_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    deadline TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    completed_date TEXT
)
""")

conn.commit()

print("Tasks table reset successfully.")

tables = conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Tables:", tables)

conn.close()