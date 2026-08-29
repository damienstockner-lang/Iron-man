from setuptools import setup, find_packages

setup(
    name="friday-assistant",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyttsx3>=2.90",
        "deep-translator>=1.11.4",
        "Pillow>=9.0.0",
        "pytesseract>=0.3.10",
        "wikipedia>=1.4.0",
        "pywhatkit>=5.4",
        "SpeechRecognition>=3.10.0",
        "requests>=2.31.0",
        "plyer>=2.1.0",
        "babel>=2.14.0",
    ],
    entry_points={
        "console_scripts": [
            "friday=friday_assistant.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Damien Stockner",
    description="Friday personal assistant CLI",
)
