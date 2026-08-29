import unittest
import tempfile
import os
import sqlite3
from friday_assistant.db import connect_db, setup_database, get_user_id


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.conn = sqlite3.connect(self.temp_db.name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        setup_database(self.conn)

    def tearDown(self):
        self.conn.close()
        os.unlink(self.temp_db.name)

    def test_connect_db_returns_connection(self):
        conn = connect_db()
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()

    def test_setup_database_creates_all_tables(self):
        expected_tables = [
            "users", "tasks", "notes", "schedule_events", "daily_steps",
            "contacts", "appointments", "action_log", "tv_remote_commands",
            "reminders", "expenses", "habits", "habit_completions",
            "shopping_items", "recipes", "recipe_ingredients", "pomodoro_sessions"
        ]
        cursor = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} not created")

    def test_get_user_id_creates_user(self):
        user_id = get_user_id(self.conn, "Test User", "test@example.com", "1234567890")
        self.assertIsInstance(user_id, int)
        row = self.conn.execute("SELECT name, email, phone FROM users WHERE user_id = ?", (user_id,)).fetchone()
        self.assertEqual(row, ("Test User", "test@example.com", "1234567890"))

    def test_get_user_id_returns_existing(self):
        user_id1 = get_user_id(self.conn, "Test User", "test@example.com", "1234567890")
        user_id2 = get_user_id(self.conn, "Test User", "test@example.com", "1234567890")
        self.assertEqual(user_id1, user_id2)

    def test_users_table_has_phone_column(self):
        cursor = self.conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        self.assertIn("phone", columns)

    def test_tasks_table_has_priority_column(self):
        cursor = self.conn.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        self.assertIn("priority", columns)

    def test_notes_table_has_tags_column(self):
        cursor = self.conn.execute("PRAGMA table_info(notes)")
        columns = [row[1] for row in cursor.fetchall()]
        self.assertIn("tags", columns)

    def test_reminders_table_has_location_column(self):
        cursor = self.conn.execute("PRAGMA table_info(reminders)")
        columns = [row[1] for row in cursor.fetchall()]
        self.assertIn("location", columns)

    def test_foreign_keys_enabled(self):
        result = self.conn.execute("PRAGMA foreign_keys").fetchone()
        self.assertEqual(result[0], 1)


if __name__ == "__main__":
    unittest.main()
