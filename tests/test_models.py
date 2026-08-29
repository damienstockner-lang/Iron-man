import unittest
import tempfile
import os
import sqlite3
from datetime import date, datetime
from friday_assistant.db import connect_db, setup_database, get_user_id
from friday_assistant.models import (
    add_task, complete_task, add_note, add_contact, find_contact,
    add_appointment, add_reminder, add_expense, record_steps,
    get_tasks, get_upcoming_events, get_today_events, get_notes,
    search_all, get_stats, export_data,
    add_habit, complete_habit, get_habits,
    add_shopping_item, toggle_shopping_item, get_shopping_items,
    add_recipe, add_recipe_ingredient, get_recipes, get_recipe_ingredients,
    start_pomodoro, end_pomodoro, get_pomodoro_sessions,
)


class TestModels(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.conn = sqlite3.connect(self.temp_db.name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        setup_database(self.conn)
        self.user_id = get_user_id(self.conn, "Test User", "test@example.com", "1234567890")

    def tearDown(self):
        self.conn.close()
        os.unlink(self.temp_db.name)

    def test_add_task(self):
        task_id = add_task(self.conn, self.user_id, "Test task", priority="high")
        self.assertIsInstance(task_id, int)
        row = self.conn.execute("SELECT title, priority FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        self.assertEqual(row, ("Test task", "high"))

    def test_complete_task(self):
        task_id = add_task(self.conn, self.user_id, "Test task")
        complete_task(self.conn, task_id)
        row = self.conn.execute("SELECT is_completed FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        self.assertEqual(row[0], 1)

    def test_add_note_with_tags(self):
        note_id = add_note(self.conn, self.user_id, "Note content", tags="work,urgent")
        row = self.conn.execute("SELECT content, tags FROM notes WHERE note_id = ?", (note_id,)).fetchone()
        self.assertEqual(row, ("Note content", "work,urgent"))

    def test_add_contact(self):
        contact_id = add_contact(self.conn, "John", "555-1234", "john@example.com")
        row = self.conn.execute("SELECT name, phone, email FROM contacts WHERE contact_id = ?", (contact_id,)).fetchone()
        self.assertEqual(row, ("John", "555-1234", "john@example.com"))

    def test_find_contact(self):
        add_contact(self.conn, "John", "555-1234", "john@example.com")
        row = find_contact(self.conn, "John")
        self.assertIsNotNone(row)
        self.assertEqual(row[1], "John")

    def test_add_appointment(self):
        appt_id = add_appointment(self.conn, "Dentist", "2026-12-01T10:00:00", "Dr. Smith")
        row = self.conn.execute("SELECT service, provider FROM appointments WHERE appointment_id = ?", (appt_id,)).fetchone()
        self.assertEqual(row, ("Dentist", "Dr. Smith"))

    def test_add_reminder(self):
        reminder_id = add_reminder(self.conn, self.user_id, "Meeting", "2026-12-01T10:00:00", "Office")
        row = self.conn.execute("SELECT title, location FROM reminders WHERE reminder_id = ?", (reminder_id,)).fetchone()
        self.assertEqual(row, ("Meeting", "Office"))

    def test_add_expense(self):
        expense_id = add_expense(self.conn, self.user_id, 25.50, "food", "Lunch")
        row = self.conn.execute("SELECT amount, category FROM expenses WHERE expense_id = ?", (expense_id,)).fetchone()
        self.assertEqual(row, (25.5, "food"))

    def test_record_steps(self):
        record_steps(self.conn, 5000, "2026-08-29")
        row = self.conn.execute("SELECT steps FROM daily_steps WHERE step_date = ?", ("2026-08-29",)).fetchone()
        self.assertEqual(row[0], 5000)

    def test_get_tasks_sorted_by_priority(self):
        add_task(self.conn, self.user_id, "Low", priority="low")
        add_task(self.conn, self.user_id, "High", priority="high")
        tasks = get_tasks(self.conn, self.user_id)
        priorities = [t[5] for t in tasks]
        self.assertEqual(priorities, ["high", "low"])

    def test_get_today_events(self):
        add_schedule_event = __import__("friday_assistant.models", fromlist=["add_schedule_event"]).add_schedule_event
        add_schedule_event(self.conn, self.user_id, "Today event", "2026-08-29T10:00:00")
        events = get_today_events(self.conn, self.user_id)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0][1], "Today event")

    def test_search_all(self):
        add_task(self.conn, self.user_id, "Search task")
        results = search_all(self.conn, self.user_id, "Search")
        self.assertGreaterEqual(len(results["tasks"]), 1)

    def test_get_stats(self):
        stats = get_stats(self.conn, self.user_id)
        self.assertIn("tasks_total", stats)
        self.assertIn("habits", stats)
        self.assertIn("pomodoro_sessions", stats)

    def test_export_data(self):
        add_task(self.conn, self.user_id, "Export task")
        data = export_data(self.conn, self.user_id)
        self.assertIn("tasks", data)
        self.assertIn("habits", data)
        self.assertIn("shopping_items", data)
        self.assertIn("recipes", data)
        self.assertIn("pomodoro_sessions", data)

    def test_add_habit_and_complete(self):
        habit_id = add_habit(self.conn, self.user_id, "Exercise")
        complete_habit(self.conn, habit_id)
        habits = get_habits(self.conn, self.user_id)
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0][1], "Exercise")

    def test_add_shopping_and_toggle(self):
        item_id = add_shopping_item(self.conn, self.user_id, "Milk", 2)
        toggle_shopping_item(self.conn, item_id)
        items = get_shopping_items(self.conn, self.user_id, include_bought=True)
        self.assertEqual(items[0][3], 1)

    def test_add_recipe_and_ingredients(self):
        recipe_id = add_recipe(self.conn, self.user_id, "Pasta", "Boil water", 2)
        add_recipe_ingredient(self.conn, recipe_id, "Pasta", "200g")
        ingredients = get_recipe_ingredients(self.conn, recipe_id)
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0][1], "Pasta")
        self.assertEqual(ingredients[0][2], "200g")

    def test_pomodoro_start_and_stop(self):
        session_id = start_pomodoro(self.conn, self.user_id, "Study", 25)
        end_pomodoro(self.conn, session_id)
        sessions = get_pomodoro_sessions(self.conn, self.user_id)
        self.assertEqual(len(sessions), 1)
        self.assertIsNotNone(sessions[0][3])


if __name__ == "__main__":
    unittest.main()
