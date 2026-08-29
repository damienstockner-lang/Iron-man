import random
import time
from typing import Optional


def open_url(url: str) -> None:
    import webbrowser
    webbrowser.open(url)


def speak_text(text: str) -> None:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        print(f"[Speak] {text}")


def translate_text(text: str, target_lang: str = "en") -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return f"[Translate to {target_lang}] {text}"


def analyze_image(image_path: str) -> str:
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text or "No readable text found in image."
    except Exception:
        return f"[Vision] Analyzed image: {image_path}"


def answer_question(question: str) -> str:
    try:
        import wikipedia
        return wikipedia.summary(question, sentences=2)
    except Exception:
        try:
            import pywhatkit
            pywhatkit.search(question)
            return f"Searching web for: {question}"
        except Exception:
            return f"[Q&A] {question}"


def helmet_mode() -> None:
    colors = ["\033[91m", "\033[92m", "\033[93m", "\033[94m", "\033[95m", "\033[96m"]
    reset = "\033[0m"
    lines = [
        "INITIALIZING HELMET INTERFACE...",
        "LOADING TARGETING SYSTEMS...",
        "CALIBRATING HEADS-UP DISPLAY...",
        "SCANNING ENVIRONMENT...",
        "MODE: IRON MAN",
    ]
    for line in lines:
        color = random.choice(colors)
        print(f"{color}{line}{reset}")
        time.sleep(0.5)
    print(f"\n{colors[3]}HELMET ACTIVE{reset}")
    try:
        while True:
            data = f"TARGET: {random.randint(100,999)} | SPEED: {random.randint(0,1200)} km/h | ALT: {random.randint(0,50000)} m"
            print(f"{random.choice(colors)}{data}{reset}", end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n{colors[0]}HELMET DISENGAGED{reset}")


def design_ascii(text: str, style: str = "box") -> str:
    lines = text.split("\n")
    width = max(len(line) for line in lines) + 4
    if style == "box":
        top = "┌" + "─" * (width - 2) + "┐"
        bottom = "└" + "─" * (width - 2) + "┘"
        middle = "\n".join("│ " + line.ljust(width - 4) + " │" for line in lines)
        return f"{top}\n{middle}\n{bottom}"
    elif style == "star":
        top = "*" * width
        bottom = "*" * width
        middle = "\n".join("* " + line.ljust(width - 4) + " *" for line in lines)
        return f"{top}\n{middle}\n{bottom}"
    return text
