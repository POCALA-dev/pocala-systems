from inout.whisper_transcriber import transcribe_auto
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from utils.response_check import is_yes, is_no
from offline.grammar import grammar_mode
from offline.ask import ask_mode
from offline.question import question_mode
from offline.speaking import speaking_mode

ASSISTANT_KEYWORDS = {
    "grammar": ["grammar", "tata bahasa", "ram", "mar", "gra"],
    "ask": ["ask", "tanya", "asking", "tanya jawab"],
    "question": ["exercise", "soal", "question"],
    "speaking": ["speaking", "speaking partner", "bicara"]
}


def detect_assistant_function(text):
    """Return the requested function name based on detected keywords."""
    text = text.lower()
    for mode, keywords in ASSISTANT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return mode
    return None


def tanya_ulang_assistant(lcd=None):
    """
    Ask the user if they want to try another assistant function.

    Returns True if user answers yes, False if no.
    """
    speak_and_display(
        "Welcome back, Do you want to try another function?",
        lang="en",
        lcd=lcd
    )

    while True:
        audio = record_once(filename="ask_repeat_assistant.wav", lcd=lcd)

        if audio is None:
            speak_and_display(
                "No audio detected. Please try again.",
                lang="en",
                lcd=lcd
            )
            continue

        reply = (transcribe_auto(audio, lcd=lcd) or "").lower()
        print(f"[USER REPLY] {reply}")

        if is_no(reply):
            speak_and_display(
                "Exiting assistant mode. Goodbye!",
                lang="en",
                lcd=lcd
            )
            return False
        if is_yes(reply):
            return True

        speak_and_display(
            "I didn't understand. Please say yes or no.",
            lang="en",
            lcd=lcd
        )


def assistant_mode(lcd=None):
    """
    Run the Assistant Mode.

    Asks the user to choose a function, executes it, and then asks if they
    want to try another function.
    """
    speak_and_display("Welcome to assistant mode", lang="en", lcd=lcd)

    while True:
        speak_and_display(
            "Choose a function: Grammar, Ask, Question, or Speaking.",
            lang="en",
            lcd=lcd
        )

        while True:
            audio = record_once(filename="assistant_mode_input.wav", lcd=lcd)

            if audio is None:
                speak_and_display(
                    "No audio detected. Let's try again.",
                    lang="en",
                    lcd=lcd
                )
                continue

            user_input = (transcribe_auto(audio, lcd=lcd) or "").strip()
            if not user_input:
                speak_and_display(
                    "Sorry, I didn't catch that. Let's try again.",
                    lang="en",
                    lcd=lcd
                )
                continue

            print(f"[ASSISTANT MODE INPUT]: {user_input}")
            selected_mode = detect_assistant_function(user_input)

            if selected_mode is None:
                speak_and_display(
                    "Sorry, I didn't recognize that function. Please try again.",
                    lang="en",
                    lcd=lcd
                )
                continue
            break

        if selected_mode == "grammar":
            grammar_mode(lcd=lcd)
        elif selected_mode == "ask":
            ask_mode(lcd=lcd)
        elif selected_mode == "question":
            question_mode(lcd=lcd)
        elif selected_mode == "speaking":
            speaking_mode(lcd=lcd)

        if not tanya_ulang_assistant(lcd=lcd):
            break
