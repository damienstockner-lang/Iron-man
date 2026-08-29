import unittest
from unittest.mock import patch, MagicMock
from friday_assistant.comm import send_sms, send_whatsapp, make_call, ir_send


class TestComm(unittest.TestCase):
    @patch("shutil.which")
    @patch("subprocess.run")
    def test_send_sms_with_termux(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/termux-sms-send"
        send_sms("1234567890", "Hello")
        mock_run.assert_called_once_with(["termux-sms-send", "-n", "1234567890", "Hello"], check=False)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_send_sms_without_termux(self, mock_run, mock_which):
        mock_which.return_value = None
        with patch("builtins.print") as mock_print:
            send_sms("1234567890", "Hello")
            mock_print.assert_called_with("[SMS to 1234567890] Hello")

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_send_whatsapp_with_termux(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/termux-open"
        send_whatsapp("1234567890", "Hello")
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "termux-open")
        self.assertIn("wa.me/1234567890", args[1])

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_send_whatsapp_without_termux(self, mock_run, mock_which):
        mock_which.return_value = None
        with patch("builtins.print") as mock_print:
            send_whatsapp("1234567890", "Hello World")
            mock_print.assert_called_with("[WhatsApp to 1234567890] Hello World")

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_make_call_with_termux(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/termux-telephony-call"
        make_call("1234567890")
        mock_run.assert_called_once_with(["termux-telephony-call", "1234567890"], check=False)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_make_call_without_termux(self, mock_run, mock_which):
        mock_which.return_value = None
        with patch("builtins.print") as mock_print:
            make_call("1234567890")
            mock_print.assert_called_with("[Call] 1234567890")

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_ir_send_with_termux(self, mock_run, mock_which):
        mock_which.return_value = "/usr/bin/termux-infrared-transmit"
        ir_send("TV", "POWER")
        mock_run.assert_called_once_with(["termux-infrared-transmit", "-d", "TV", "POWER"], check=False)

    @patch("shutil.which")
    @patch("subprocess.run")
    def test_ir_send_without_termux(self, mock_run, mock_which):
        mock_which.return_value = None
        with patch("builtins.print") as mock_print:
            ir_send("TV", "POWER")
            mock_print.assert_called_with("[IR TV] POWER")


if __name__ == "__main__":
    unittest.main()
