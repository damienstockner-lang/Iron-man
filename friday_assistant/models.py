import sqlite3
from datetime import date, datetime
from typing import Optional


def add_schedule_event(conn: sqlite3.Connection, user_id: int, title: str,
                       starts_at: str, ends_at: Optional[str] = None,
                       location: Optional[str] = None, details: Optional[str] = None) -> int:
    cursor = conn.execute(
        """INSERT INTO schedule_events
           (user_id, title, starts_at, ends_at, location, details)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, title, starts_at, ends_at, location, details),
    )
    conn.commit()
    return int(cursor.lastrowid)


def add_task(conn: sqlite3.Connection, user_id: int, title: str,
             description: Optional[str] = None, due_date: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO tasks (user_id, title, description, due_date) VALUES (?, ?, ?, ?)",
        (user_id, title, description, due_date),
    )
    conn.commit()
    return int(cursor.lastrowid)


def complete_task(conn: sqlite3.Connection, task_id: int) -> None:
    conn.execute("UPDATE tasks SET is_completed = 1 WHERE task_id = ?", (task_id,))
    conn.commit()


def add_note(conn: sqlite3.Connection, user_id: int, content: str) -> int:
    cursor = conn.execute(
        "INSERT INTO notes (user_id, content) VALUES (?, ?)", (user_id, content)
    )
    conn.commit()
    return int(cursor.lastrowid)


def add_contact(conn: sqlite3.Connection, name: str, phone: Optional[str] = None,
                email: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)", (name, phone, email)
    )
    conn.commit()
    return int(cursor.lastrowid)


def find_contact(conn: sqlite3.Connection, name: str) -> Optional[tuple]:
    row = conn.execute(
        "SELECT contact_id, name, phone, email FROM contacts WHERE name LIKE ?",
        (f"%{name}%",),
    ).fetchone()
    return row


def add_appointment(conn: sqlite3.Connection, service: str, starts_at: str,
                    provider: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO appointments (service, starts_at, provider) VALUES (?, ?, ?)",
        (service, starts_at, provider),
    )
    conn.commit()
    return int(cursor.lastrowid)


def log_action(conn: sqlite3.Connection, action_type: str, recipient: Optional[str] = None,
               content: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO action_log (action_type, recipient, content) VALUES (?, ?, ?)",
        (action_type, recipient, content),
    )
    conn.commit()
    return int(cursor.lastrowid)


def queue_tv_command(conn: sqlite3.Connection, device_name: str, command: str) -> int:
    cursor = conn.execute(
        "INSERT INTO tv_remote_commands (device_name, command) VALUES (?, ?)",
        (device_name, command),
    )
    conn.commit()
    return int(cursor.lastrowid)


def add_reminder(conn: sqlite3.Connection, user_id: int, title: str, due_at: str) -> int:
    cursor = conn.execute(
        "INSERT INTO reminders (user_id, title, due_at) VALUES (?, ?, ?)",
        (user_id, title, due_at),
    )
    conn.commit()
    return int(cursor.lastrowid)


def add_expense(conn: sqlite3.Connection, user_id: int, amount: float,
                category: Optional[str] = None, note: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO expenses (user_id, amount, category, note) VALUES (?, ?, ?, ?)",
        (user_id, amount, category, note),
    )
    conn.commit()
    return int(cursor.lastrowid)


def record_steps(conn: sqlite3.Connection, steps: int, step_date: Optional[str] = None) -> None:
    if step_date is None:
        step_date = date.today().isoformat()
    conn.execute(
        """INSERT INTO daily_steps (step_date, steps) VALUES (?, ?)
           ON CONFLICT(step_date) DO UPDATE SET steps = excluded.steps, updated_at = CURRENT_TIMESTAMP""",
        (step_date, steps),
    )
    conn.commit()


def get_tasks(conn: sqlite3.Connection, user_id: int, include_completed: bool = False) -> list:
    query = "SELECT task_id, title, description, is_completed, due_date FROM tasks WHERE user_id = ?"
    if not include_completed:
        query += " AND is_completed = 0"
    query += " ORDER BY due_date IS NULL, due_date"
    return conn.execute(query, (user_id,)).fetchall()


def get_upcoming_events(conn: sqlite3.Connection, user_id: int, limit: int = 10) -> list:
    now = datetime.now().isoformat()
    return conn.execute(
        """SELECT event_id, title, starts_at, ends_at, location, details
           FROM schedule_events
           WHERE user_id = ? AND starts_at >= ?
           ORDER BY starts_at ASC
           LIMIT ?""",
        (user_id, now, limit),
    ).fetchall()


def get_today_events(conn: sqlite3.Connection, user_id: int) -> list:
    today = date.today().isoformat()
    return conn.execute(
        """SELECT event_id, title, starts_at, ends_at, location, details
           FROM schedule_events
           WHERE user_id = ? AND DATE(starts_at) = ?
           ORDER BY starts_at ASC""",
        (user_id, today),
    ).fetchall()


def get_notes(conn: sqlite3.Connection, user_id: int, limit: int = 20) -> list:
    return conn.execute(
        "SELECT note_id, content, created_at FROM notes WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()


def search_all(conn: sqlite3.Connection, user_id: int, query: str) -> dict:
    term = f"%{query}%"
    tasks = conn.execute(
        "SELECT task_id, title, description FROM tasks WHERE user_id = ? AND (title LIKE ? OR description LIKE ?)",
        (user_id, term, term),
    ).fetchall()
    notes = conn.execute(
        "SELECT note_id, content FROM notes WHERE user_id = ? AND content LIKE ?",
        (user_id, term),
    ).fetchall()
    contacts = conn.execute(
        "SELECT contact_id, name, phone, email FROM contacts WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?",
        (term, term, term),
    ).fetchall()
    events = conn.execute(
        "SELECT event_id, title, location, details FROM schedule_events WHERE user_id = ? AND (title LIKE ? OR location LIKE ? OR details LIKE ?)",
        (user_id, term, term, term),
    ).fetchall()
    return {
        "tasks": tasks,
        "notes": notes,
        "contacts": contacts,
        "events": events,
    }


def get_stats(conn: sqlite3.Connection, user_id: int) -> dict:
    task_stats = conn.execute(
        "SELECT COUNT(*), SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) FROM tasks WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    note_count = conn.execute(
        "SELECT COUNT(*) FROM notes WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    event_count = conn.execute(
        "SELECT COUNT(*) FROM schedule_events WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    contact_count = conn.execute(
        "SELECT COUNT(*) FROM contacts", ()
    ).fetchone()[0]
    total_steps = conn.execute(
        "SELECT SUM(steps) FROM daily_steps"
    ).fetchone()[0]
    total_expenses = conn.execute(
        "SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    return {
        "tasks_total": task_stats[0] or 0,
        "tasks_completed": task_stats[1] or 0,
        "notes": note_count,
        "events": event_count,
        "contacts": contact_count,
        "total_steps": total_steps or 0,
        "total_expenses": total_expenses or 0,
    }


def export_data(conn: sqlite3.Connection, user_id: int) -> dict:
    tasks = conn.execute(
        "SELECT task_id, title, description, is_completed, due_date FROM tasks WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    notes = conn.execute(
        "SELECT note_id, content, created_at FROM notes WHERE user_id = ?", (user_id,)
    ).fetchall()
    events = conn.execute(
        "SELECT event_id, title, starts_at, ends_at, location, details FROM schedule_events WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    contacts = conn.execute(
        "SELECT contact_id, name, phone, email FROM contacts", ()
    ).fetchall()
    expenses = conn.execute(
        "SELECT expense_id, amount, category, note, spent_at FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    return {
        "tasks": [{"task_id": t[0], "title": t[1], "description": t[2], "is_completed": t[3], "due_date": t[4]} for t in tasks],
        "notes": [{"note_id": n[0], "content": n[1], "created_at": n[2]} for n in notes],
        "events": [{"event_id": e[0], "title": e[1], "starts_at": e[2], "ends_at": e[3], "location": e[4], "details": e[5]} for e in events],
        "contacts": [{"contact_id": c[0], "name": c[1], "phone": c[2], "email": c[3]} for c in contacts],
        "expenses": [{"expense_id": x[0], "amount": x[1], "category": x[2], "note": x[3], "spent_at": x[4]} for x in expenses],
    }
