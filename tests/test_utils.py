import os

import unittest
from unittest.mock import patch, MagicMock
from friday_assistant.utils import (
    open_url, speak_text, translate_text, analyze_image,
    answer_question, get_weather, load_config, save_config,
    backup_db, restore_db, design_ascii, listen_command, match_tv_command,
)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import speech_recognition
    HAS_SR = True
except ImportError:
    HAS_SR = False

try:
    import wikipedia
    HAS_WIKI = True
except ImportError:
    HAS_WIKI = False

os.environ.setdefault("DISPLAY", ":0")
try:
    import pywhatkit
    HAS_PYWHATKIT = True
except Exception:
    HAS_PYWHATKIT = False


class TestUtils(unittest.TestCase):
    def test_design_ascii_box(self):
        result = design_ascii("Hello", style="box")
        self.assertIn("Hello", result)
        self.assertIn("┌", result)
        self.assertIn("┘", result)

    def test_design_ascii_star(self):
        result = design_ascii("Hi", style="star")
        self.assertIn("Hi", result)
        self.assertIn("*", result)

    def test_match_tv_command_on(self):
        device, command = match_tv_command("turn on the TV")
        self.assertEqual(command, "on")

    def test_match_tv_command_volume_up(self):
        device, command = match_tv_command("volume up")
        self.assertEqual(command, "volume_up")

    def test_match_tv_command_no_match(self):
        device, command = match_tv_command("hello world")
        self.assertEqual(command, "")

    def test_load_config_missing_file(self):
        config = load_config("/nonexistent/path/friday.ini")
        self.assertEqual(config, {})

    def test_save_and_load_config(self):
        import tempfile
        import os
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".ini")
        temp.close()
        config = {"friday": {"theme": "dark", "volume": "50"}}
        save_config(config, temp.name)
        loaded = load_config(temp.name)
        self.assertEqual(loaded["friday"]["theme"], "dark")
        os.unlink(temp.name)

    def test_backup_db_missing(self):
        with patch("os.path.exists", return_value=False):
            result = backup_db("/nonexistent/friday.db")
        self.assertIn("No database found", result)

    def test_restore_db_missing(self):
        with patch("os.path.exists", return_value=False):
            result = restore_db("/nonexistent/backup.db")
        self.assertIn("Backup file not found", result)

    @patch("webbrowser.open")
    def test_open_url(self, mock_open):
        open_url("https://example.com")
        mock_open.assert_called_once_with("https://example.com")

    @patch("builtins.print")
    def test_speak_text_fallback(self, mock_print):
        with patch.dict("sys.modules", {"pyttsx3": None}):
            speak_text("hello")
        mock_print.assert_called_with("[Speak] hello")

    @unittest.skipUnless(HAS_REQUESTS, "requests not installed")
    def test_get_weather_no_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            result = get_weather("Vancouver")
        self.assertIn("OPENWEATHER_API_KEY", result)

    @unittest.skipUnless(HAS_REQUESTS, "requests not installed")
    @patch("requests.get")
    def test_get_weather_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "main": {"temp": 15.5},
            "weather": [{"description": "clear sky"}]
        }
        mock_get.return_value = mock_response
        with patch.dict("os.environ", {"OPENWEATHER_API_KEY": "fake-key"}):
            result = get_weather("Vancouver")
            self.assertIn("15.5", result)
            self.assertIn("clear sky", result)

    @unittest.skipUnless(HAS_WIKI, "wikipedia not installed")
    @patch("wikipedia.summary")
    def test_answer_question_success(self, mock_summary):
        mock_summary.return_value = "Test summary"
        result = answer_question("test query")
        self.assertEqual(result, "Test summary")

    @unittest.skipUnless(HAS_WIKI and HAS_PYWHATKIT, "wikipedia or pywhatkit not installed")
    @patch("wikipedia.summary")
    @patch("pywhatkit.search")
    def test_answer_question_fallback(self, mock_search, mock_summary):
        mock_summary.side_effect = Exception("no wiki")
        mock_search.return_value = None
        result = answer_question("test")
        self.assertIn("Searching web", result)

    @unittest.skipUnless(HAS_SR, "speech_recognition not installed")
    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.Microphone")
    def test_listen_command(self, mock_mic_class, mock_recog_class):
        mock_recognizer = MagicMock()
        mock_recog_class.return_value = mock_recognizer
        mock_recognizer.recognize_google.return_value = "turn on TV"
        mock_mic = MagicMock()
        mock_mic_class.return_value = mock_mic
        mock_mic.__enter__ = MagicMock(return_value=mock_mic)
        mock_mic.__exit__ = MagicMock(return_value=False)
        result = listen_command("Google")
        self.assertIn("turn on TV", result)


if __name__ == "__main__":
    unittest.main()
