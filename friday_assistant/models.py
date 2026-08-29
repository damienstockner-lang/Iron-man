import sqlite3
from datetime import date, datetime
from typing import Optional


def add_schedule_event(conn: sqlite3.Connection, user_id: int, title: str,
                       starts_at: str, ends_at: Optional[str] = None,
                       location: Optional[str] = None, details: Optional[str] = None,
                       recurrence: Optional[str] = None, recurrence_until: Optional[str] = None) -> int:
    cursor = conn.execute(
        """INSERT INTO schedule_events
           (user_id, title, starts_at, ends_at, location, details, recurrence, recurrence_until)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, title, starts_at, ends_at, location, details, recurrence, recurrence_until),
    )
    conn.commit()
    return int(cursor.lastrowid)


def add_task(conn: sqlite3.Connection, user_id: int, title: str,
             description: Optional[str] = None, due_date: Optional[str] = None,
             priority: str = "medium", recurrence: Optional[str] = None,
             recurrence_until: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO tasks (user_id, title, description, due_date, priority, recurrence, recurrence_until) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, title, description, due_date, priority, recurrence, recurrence_until),
    )
    conn.commit()
    return int(cursor.lastrowid)


def complete_task(conn: sqlite3.Connection, task_id: int) -> None:
    conn.execute("UPDATE tasks SET is_completed = 1 WHERE task_id = ?", (task_id,))
    conn.commit()


def add_note(conn: sqlite3.Connection, user_id: int, content: str, tags: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO notes (user_id, content, tags) VALUES (?, ?, ?)", (user_id, content, tags)
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


def add_reminder(conn: sqlite3.Connection, user_id: int, title: str, due_at: str,
                 location: Optional[str] = None) -> int:
    cursor = conn.execute(
        "INSERT INTO reminders (user_id, title, due_at, location) VALUES (?, ?, ?, ?)",
        (user_id, title, due_at, location),
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
    query = "SELECT task_id, title, description, is_completed, due_date, priority, recurrence, recurrence_until FROM tasks WHERE user_id = ?"
    if not include_completed:
        query += " AND is_completed = 0"
    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, due_date IS NULL, due_date"
    return conn.execute(query, (user_id,)).fetchall()


def get_upcoming_events(conn: sqlite3.Connection, user_id: int, limit: int = 10) -> list:
    now = datetime.now().isoformat()
    return conn.execute(
        """SELECT event_id, title, starts_at, ends_at, location, details, recurrence, recurrence_until
           FROM schedule_events
           WHERE user_id = ? AND starts_at >= ?
           ORDER BY starts_at ASC
           LIMIT ?""",
        (user_id, now, limit),
    ).fetchall()


def get_today_events(conn: sqlite3.Connection, user_id: int) -> list:
    today = date.today().isoformat()
    return conn.execute(
        """SELECT event_id, title, starts_at, ends_at, location, details, recurrence, recurrence_until
           FROM schedule_events
           WHERE user_id = ? AND DATE(starts_at) = ?
           ORDER BY starts_at ASC""",
        (user_id, today),
    ).fetchall()


def get_notes(conn: sqlite3.Connection, user_id: int, limit: int = 20) -> list:
    return conn.execute(
        "SELECT note_id, content, created_at, tags FROM notes WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
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
    habit_count = conn.execute(
        "SELECT COUNT(*) FROM habits WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    shopping_count = conn.execute(
        "SELECT COUNT(*) FROM shopping_items WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    recipe_count = conn.execute(
        "SELECT COUNT(*) FROM recipes WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    pomodoro_count = conn.execute(
        "SELECT COUNT(*) FROM pomodoro_sessions WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    return {
        "tasks_total": task_stats[0] or 0,
        "tasks_completed": task_stats[1] or 0,
        "notes": note_count,
        "events": event_count,
        "contacts": contact_count,
        "total_steps": total_steps or 0,
        "total_expenses": total_expenses or 0,
        "habits": habit_count,
        "shopping_items": shopping_count,
        "recipes": recipe_count,
        "pomodoro_sessions": pomodoro_count,
    }


def export_data(conn: sqlite3.Connection, user_id: int) -> dict:
    tasks = conn.execute(
        "SELECT task_id, title, description, is_completed, due_date, priority, recurrence, recurrence_until FROM tasks WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    notes = conn.execute(
        "SELECT note_id, content, created_at, tags FROM notes WHERE user_id = ?", (user_id,)
    ).fetchall()
    events = conn.execute(
        "SELECT event_id, title, starts_at, ends_at, location, details, recurrence, recurrence_until FROM schedule_events WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    contacts = conn.execute(
        "SELECT contact_id, name, phone, email FROM contacts", ()
    ).fetchall()
    expenses = conn.execute(
        "SELECT expense_id, amount, category, note, spent_at FROM expenses WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    habits = conn.execute(
        "SELECT habit_id, name, frequency, streak, best_streak FROM habits WHERE user_id = ?", (user_id,)
    ).fetchall()
    shopping = conn.execute(
        "SELECT item_id, name, quantity, is_bought, created_at FROM shopping_items WHERE user_id = ?", (user_id,)
    ).fetchall()
    recipes = conn.execute(
        "SELECT recipe_id, name, instructions, servings, created_at FROM recipes WHERE user_id = ?", (user_id,)
    ).fetchall()
    ingredients = conn.execute(
        "SELECT ingredient_id, recipe_id, name, amount FROM recipe_ingredients", ()
    ).fetchall()
    pomodoros = conn.execute(
        "SELECT session_id, task, started_at, ended_at, duration_minutes FROM pomodoro_sessions WHERE user_id = ?", (user_id,)
    ).fetchall()
    return {
        "tasks": [{"task_id": t[0], "title": t[1], "description": t[2], "is_completed": t[3], "due_date": t[4], "priority": t[5], "recurrence": t[6], "recurrence_until": t[7]} for t in tasks],
        "notes": [{"note_id": n[0], "content": n[1], "created_at": n[2], "tags": n[3]} for n in notes],
        "events": [{"event_id": e[0], "title": e[1], "starts_at": e[2], "ends_at": e[3], "location": e[4], "details": e[5], "recurrence": e[6], "recurrence_until": e[7]} for e in events],
        "contacts": [{"contact_id": c[0], "name": c[1], "phone": c[2], "email": c[3]} for c in contacts],
        "expenses": [{"expense_id": x[0], "amount": x[1], "category": x[2], "note": x[3], "spent_at": x[4]} for x in expenses],
        "habits": [{"habit_id": h[0], "name": h[1], "frequency": h[2], "streak": h[3], "best_streak": h[4]} for h in habits],
        "shopping_items": [{"item_id": s[0], "name": s[1], "quantity": s[2], "is_bought": s[3], "created_at": s[4]} for s in shopping],
        "recipes": [{"recipe_id": r[0], "name": r[1], "instructions": r[2], "servings": r[3], "created_at": r[4]} for r in recipes],
        "recipe_ingredients": [{"ingredient_id": i[0], "recipe_id": i[1], "name": i[2], "amount": i[3]} for i in ingredients],
        "pomodoro_sessions": [{"session_id": p[0], "task": p[1], "started_at": p[2], "ended_at": p[3], "duration_minutes": p[4]} for p in pomodoros],
    }


def add_habit(conn: sqlite3.Connection, user_id: int, name: str, frequency: str = "daily") -> int:
    cursor = conn.execute(
        "INSERT INTO habits (user_id, name, frequency) VALUES (?, ?, ?)",
        (user_id, name, frequency),
    )
    conn.commit()
    return int(cursor.lastrowid)


def complete_habit(conn: sqlite3.Connection, habit_id: int) -> None:
    today = date.today().isoformat()
    row = conn.execute(
        "SELECT MAX(completed_at) FROM habit_completions WHERE habit_id = ?", (habit_id,)
    ).fetchone()
    last_date = row[0] if row and row[0] else None
    streak = 1
    if last_date:
        last = datetime.fromisoformat(last_date).date()
        if last == date.today():
            return
        if (date.today() - last).days == 1:
            streak = conn.execute("SELECT streak FROM habits WHERE habit_id = ?", (habit_id,)).fetchone()[0] + 1
    conn.execute(
        "INSERT INTO habit_completions (habit_id, completed_at) VALUES (?, ?)",
        (habit_id, datetime.now().isoformat()),
    )
    best = conn.execute("SELECT best_streak FROM habits WHERE habit_id = ?", (habit_id,)).fetchone()[0]
    if streak > best:
        best = streak
    conn.execute(
        "UPDATE habits SET streak = ?, best_streak = ? WHERE habit_id = ?",
        (streak, best, habit_id),
    )
    conn.commit()


def get_habits(conn: sqlite3.Connection, user_id: int) -> list:
    return conn.execute(
        "SELECT habit_id, name, frequency, streak, best_streak FROM habits WHERE user_id = ?",
        (user_id,),
    ).fetchall()


def add_shopping_item(conn: sqlite3.Connection, user_id: int, name: str, quantity: int = 1) -> int:
    cursor = conn.execute(
        "INSERT INTO shopping_items (user_id, name, quantity) VALUES (?, ?, ?)",
        (user_id, name, quantity),
    )
    conn.commit()
    return int(cursor.lastrowid)


def toggle_shopping_item(conn: sqlite3.Connection, item_id: int) -> None:
    conn.execute(
        "UPDATE shopping_items SET is_bought = NOT is_bought WHERE item_id = ?",
        (item_id,),
    )
    conn.commit()


def get_shopping_items(conn: sqlite3.Connection, user_id: int, include_bought: bool = False) -> list:
    query = "SELECT item_id, name, quantity, is_bought, created_at FROM shopping_items WHERE user_id = ?"
    if not include_bought:
        query += " AND is_bought = 0"
    query += " ORDER BY created_at ASC"
    return conn.execute(query, (user_id,)).fetchall()


def add_recipe(conn: sqlite3.Connection, user_id: int, name: str,
               instructions: Optional[str] = None, servings: int = 1) -> int:
    cursor = conn.execute(
        "INSERT INTO recipes (user_id, name, instructions, servings) VALUES (?, ?, ?, ?)",
        (user_id, name, instructions, servings),
    )
    conn.commit()
    return int(cursor.lastrowid)


def add_recipe_ingredient(conn: sqlite3.Connection, recipe_id: int, name: str, amount: str) -> int:
    cursor = conn.execute(
        "INSERT INTO recipe_ingredients (recipe_id, name, amount) VALUES (?, ?, ?)",
        (recipe_id, name, amount),
    )
    conn.commit()
    return int(cursor.lastrowid)


def get_recipes(conn: sqlite3.Connection, user_id: int) -> list:
    return conn.execute(
        "SELECT recipe_id, name, instructions, servings, created_at FROM recipes WHERE user_id = ?",
        (user_id,),
    ).fetchall()


def get_recipe_ingredients(conn: sqlite3.Connection, recipe_id: int) -> list:
    return conn.execute(
        "SELECT ingredient_id, name, amount FROM recipe_ingredients WHERE recipe_id = ?",
        (recipe_id,),
    ).fetchall()


def start_pomodoro(conn: sqlite3.Connection, user_id: int, task: Optional[str] = None,
                   duration_minutes: int = 25) -> int:
    started_at = datetime.now().isoformat()
    cursor = conn.execute(
        "INSERT INTO pomodoro_sessions (user_id, task, started_at, duration_minutes) VALUES (?, ?, ?, ?)",
        (user_id, task, started_at, duration_minutes),
    )
    conn.commit()
    return int(cursor.lastrowid)


def end_pomodoro(conn: sqlite3.Connection, session_id: int) -> None:
    ended_at = datetime.now().isoformat()
    conn.execute(
        "UPDATE pomodoro_sessions SET ended_at = ? WHERE session_id = ?",
        (ended_at, session_id),
    )
    conn.commit()


def get_pomodoro_sessions(conn: sqlite3.Connection, user_id: int, limit: int = 20) -> list:
    return conn.execute(
        "SELECT session_id, task, started_at, ended_at, duration_minutes FROM pomodoro_sessions WHERE user_id = ? ORDER BY started_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
