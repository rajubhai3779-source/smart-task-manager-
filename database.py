import sqlite3

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def add_task(title, priority):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, priority) VALUES (?, ?)", (title, priority))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("SELECT id, title, priority, completed FROM tasks ORDER BY completed ASC, id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def toggle_task(task_id, current_status):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    new_status = 0 if current_status else 1
    c.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
