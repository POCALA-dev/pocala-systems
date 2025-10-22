# main_offline.py
from inout.piper_output import speak_and_display
from inout.recorder import record_once
from inout.whisper_transcriber import transcribe_auto
from utils.response_check import is_yes, is_no, is_help, is_exit
from offline.translator_mode import translator_mode
from offline.vocabulary_mode import vocabulary_mode
from offline.assistant_mode import assistant_mode


MODE_KEYWORDS = {
    "translator": ["translate", "translator", "terjemahan", "penerjemah", "trans"],
    "vocabulary": [
        "vocabulary", "kosa", "kata", "vocab", "fok",
        "bulari", "bulary", "fuck", "fck", "fa"
    ],
    "assistant": [
        "assistant", "asisten", "pembantu",
        "asistan", "assist", "assister"
    ]
}


def tetap_di_offline_mode(lcd=None):
    """Return True if user wants to stay in offline mode, else False."""
    speak_and_display("Do you want to stay in offline mode?", lang="en", lcd=lcd)

    while True:
        audio = record_once(filename="ask_return_connection_mode.wav", lcd=lcd)

        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        reply_raw = transcribe_auto(audio, lcd=lcd) or ""
        reply = reply_raw.strip().lower()
        print(f"[USER REPLY] {reply}")

        if is_no(reply):
            return False
        if is_yes(reply):
            return True

        speak_and_display(
            "I didn't understand. Please say yes or no.",
            lang="en",
            lcd=lcd
        )


def prompt_mode_selection(lcd=None):
    """Prompt the user to choose between available offline modes."""
    speak_and_display(
        "Choose a Mode Between Translator, Vocabulary, or Assistant to begin.",
        lang="en",
        lcd=lcd
    )


def offline_mode(lcd=None):
    """
    Main function to display the offline mode menu and handle mode selection.
    Supports Translator, Vocabulary, and Assistant modes.
    """
    speak_and_display("Welcome to offline mode POCALA!", lang="en", lcd=lcd)

    while True:
        prompt_mode_selection(lcd=lcd)
        audio = record_once(filename="main_mode_input.wav", lcd=lcd)

        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        command_raw = transcribe_auto(audio, lcd=lcd) or ""
        command = command_raw.strip().lower()

        if not command:
            speak_and_display(
                "Sorry, I didn't catch that. Please try again.",
                lang="en",
                lcd=lcd
            )
            continue
            
        print(f"[MODE SELECTED]: {command}")
        # Cek perintah global dulu
        if is_help(command):
            from help.help import help_mode
            help_mode(lcd=lcd)
            command = ""  # bersihkan input sebelumnya
            continue
        
        if is_exit(command):
            speak_and_display(
                "Exiting offline mode.", 
                lang="en", 
                lcd=lcd, 
                clear_after=True
            )
            break

        try:
            if any(k in command for k in MODE_KEYWORDS["translator"]):
                translator_mode(lcd=lcd)
            elif any(k in command for k in MODE_KEYWORDS["vocabulary"]):
                vocabulary_mode(lcd=lcd)
            elif any(k in command for k in MODE_KEYWORDS["assistant"]):
                assistant_mode(lcd=lcd)
            else:
                speak_and_display(
                    "Unknown mode. Please try again!",
                    lang="en",
                    lcd=lcd
                )
                continue
        except Exception as e:
            speak_and_display(f"An error occurred: {e}", lang="en", lcd=lcd)
            continue

        if not tetap_di_offline_mode(lcd=lcd):
            break
