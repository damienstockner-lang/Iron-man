import unittest
import tempfile
import os
import sqlite3
from friday_assistant.cli import build_parser
from friday_assistant.db import connect_db, setup_database, get_user_id


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        import friday_assistant.db as db_module
        self.original_db_name = db_module.DB_NAME
        db_module.DB_NAME = self.temp_db.name
        self.conn = sqlite3.connect(self.temp_db.name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        setup_database(self.conn)
        self.user_id = get_user_id(self.conn, "Test User", "test@example.com", "1234567890")
        self.conn.close()

    def tearDown(self):
        import friday_assistant.db as db_module
        db_module.DB_NAME = self.original_db_name
        os.unlink(self.temp_db.name)

    def test_parser_task_add(self):
        args = build_parser(["task", "--add", "Test task"])
        self.assertEqual(args.command, "task")
        self.assertEqual(args.add, "Test task")

    def test_parser_task_priority(self):
        args = build_parser(["task", "--add", "Test", "--priority", "high"])
        self.assertEqual(args.priority, "high")

    def test_parser_note_with_tags(self):
        args = build_parser(["note", "--add", "Note", "--tags", "work,urgent"])
        self.assertEqual(args.tags, "work,urgent")

    def test_parser_habit_commands(self):
        args = build_parser(["habit", "--add", "Exercise"])
        self.assertEqual(args.command, "habit")
        self.assertEqual(args.add, "Exercise")

    def test_parser_shopping_commands(self):
        args = build_parser(["shopping", "--add", "Milk"])
        self.assertEqual(args.command, "shopping")
        self.assertEqual(args.add, "Milk")

    def test_parser_pomodoro_commands(self):
        args = build_parser(["pomodoro", "--start", "Study"])
        self.assertEqual(args.command, "pomodoro")
        self.assertEqual(args.start, "Study")

    def test_parser_tv_listen(self):
        args = build_parser(["tv", "--device", "LivingRoom", "--listen"])
        self.assertTrue(args.listen)

    def test_parser_voice(self):
        args = build_parser(["voice", "--command", "Hello"])
        self.assertEqual(args.command, "Hello")

    def test_parser_weather(self):
        args = build_parser(["weather", "Vancouver"])
        self.assertEqual(args.city, "Vancouver")

    def test_parser_config_set(self):
        args = build_parser(["config", "--set", "theme=dark"])
        self.assertEqual(args.set, "theme=dark")


if __name__ == "__main__":
    unittest.main()
