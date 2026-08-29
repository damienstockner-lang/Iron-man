import os
import json
from datetime import datetime

DB_FILE = "friday_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {
        "tasks": [],
        "notes": [],
        "reminders": [],
        "expenses": [],
        "steps": [],
        "contacts": [],
        "moods": []
    }

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_task(data, title, priority="medium"):
    task = {
        "task_id": len(data["tasks"]) + 1,
        "title": title,
        "priority": priority,
        "is_completed": 0,
        "created_at": datetime.now().isoformat()
    }
    data["tasks"].append(task)
    save_data(data)
    return task

def complete_task(data, task_id):
    for task in data["tasks"]:
        if task["task_id"] == task_id:
            task["is_completed"] = 1
            save_data(data)
            return True
    return False

def get_tasks(data, include_completed=False):
    if include_completed:
        return data["tasks"]
    return [t for t in data["tasks"] if t["is_completed"] == 0]

def add_note(data, content, tags=None):
    note = {
        "note_id": len(data["notes"]) + 1,
        "content": content,
        "tags": tags,
        "created_at": datetime.now().isoformat()
    }
    data["notes"].append(note)
    save_data(data)
    return note

def get_notes(data):
    return data["notes"]

def add_reminder(data, title, due_at=""):
    reminder = {
        "reminder_id": len(data["reminders"]) + 1,
        "title": title,
        "due_at": due_at,
        "is_done": 0
    }
    data["reminders"].append(reminder)
    save_data(data)
    return reminder

def add_expense(data, amount, category="", note=""):
    expense = {
        "expense_id": len(data["expenses"]) + 1,
        "amount": float(amount),
        "category": category,
        "note": note,
        "spent_at": datetime.now().isoformat()
    }
    data["expenses"].append(expense)
    save_data(data)
    return expense

def record_steps(data, count, step_date=None):
    if step_date is None:
        step_date = datetime.now().date().isoformat()
    data["steps"].append({
        "step_date": step_date,
        "steps": int(count),
        "updated_at": datetime.now().isoformat()
    })
    save_data(data)

def get_stats(data):
    return {
        "tasks_total": len(data["tasks"]),
        "tasks_completed": sum(1 for t in data["tasks"] if t["is_completed"] == 1),
        "notes": len(data["notes"]),
        "events": 0,
        "contacts": len(data["contacts"]),
        "total_steps": sum(s["steps"] for s in data["steps"]),
        "total_expenses": sum(e["amount"] for e in data["expenses"]),
        "moods": len(data["moods"]),
    }

def add_contact(data, name, phone="", email=""):
    contact = {
        "contact_id": len(data["contacts"]) + 1,
        "name": name,
        "phone": phone,
        "email": email
    }
    data["contacts"].append(contact)
    save_data(data)
    return contact

def export_data(data):
    return data


def add_mood(data, mood, notes=""):
    entry = {
        "mood_id": len(data["moods"]) + 1,
        "mood": mood,
        "notes": notes,
        "created_at": datetime.now().isoformat()
    }
    data["moods"].append(entry)
    save_data(data)
    return entry


def get_moods(data, limit=50):
    return data["moods"][-limit:]
