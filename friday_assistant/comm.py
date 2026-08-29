import shutil
import subprocess
from typing import Optional


def send_sms(phone: str, message: str) -> None:
    if shutil.which("termux-sms-send"):
        subprocess.run(["termux-sms-send", "-n", phone, message], check=False)
    else:
        print(f"[SMS to {phone}] {message}")


def send_whatsapp(phone: str, message: str) -> None:
    if shutil.which("termux-open"):
        url = f"https://wa.me/{phone}?text={message.replace(' ', '%20')}"
        subprocess.run(["termux-open", url], check=False)
    else:
        print(f"[WhatsApp to {phone}] {message}")


def make_call(phone: str) -> None:
    if shutil.which("termux-telephony-call"):
        subprocess.run(["termux-telephony-call", phone], check=False)
    else:
        print(f"[Call] {phone}")


def ir_send(device_name: str, command: str) -> None:
    if shutil.which("termux-infrared-transmit"):
        subprocess.run(["termux-infrared-transmit", "-d", device_name, command], check=False)
    else:
        print(f"[IR {device_name}] {command}")
