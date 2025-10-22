from inout.whisper_transcriber import transcribe_en
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from clients.ollama_client import OllamaClient
from utils.response_check import is_yes, is_no


def tanya_ulang_grammar(lcd=None):
    """
    Menanyakan kepada pengguna apakah ingin memeriksa kalimat lain.

    Args:
        lcd: Objek LCD opsional untuk menampilkan teks di layar.

    Returns:
        bool: True jika pengguna menjawab 'yes', False jika menjawab 'no'.
    """
    speak_and_display(
        "Do you want to check another sentence?",
        lang="en",
        lcd=lcd
    )

    while True:
        audio = record_once(filename="ask_again_grammar.wav", lcd=lcd)

        if audio is None:
            speak_and_display(
                "No audio detected. Please try again.",
                lang="en",
                lcd=lcd
            )
            continue

        reply = transcribe_en(audio, lcd=lcd).lower()
        print(f"[USER REPLY]: {reply}")

        if is_no(reply):
            speak_and_display(
                "Exiting grammar function. Goodbye!",
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


def grammar_mode(lcd=None):
    """
    Mode untuk memeriksa dan memperbaiki tata bahasa kalimat yang diucapkan pengguna.

    Proses:
        1. Merekam suara pengguna.
        2. Mentranskripsi menjadi teks.
        3. Mengirim prompt ke LLM untuk koreksi grammar dan penjelasan dalam Bahasa Indonesia.
        4. Menampilkan dan membacakan hasil.

    Args:
        lcd: Objek LCD opsional untuk menampilkan teks di layar.
    """
    ollama = OllamaClient(model="gemma3:1b")

    speak_and_display(
        "Grammar function selected.",
        lang="en",
        lcd=lcd
    )

    while True:
        speak_and_display(
            "Please say a sentence you want me to check.",
            lang="en",
            lcd=lcd
        )

        # Minta input kalimat sampai valid
        while True:
            audio = record_once(filename="grammar_input.wav", lcd=lcd)

            if audio is None:
                speak_and_display(
                    "No audio detected. Please try again.",
                    lang="en",
                    lcd=lcd
                )
                continue

            sentence = transcribe_en(audio, lcd=lcd).strip()
            if not sentence:
                speak_and_display(
                    "Sorry, I didn't catch that. Please try again.",
                    lang="en",
                    lcd=lcd
                )
                continue

            break

        print(f"[TRANSCRIBED INPUT]: {sentence}")

        # Tampilkan status di LCD
        if lcd:
            lcd.flash_message(f"Input Sentence: {sentence}", duration=3)
            lcd.display_text("Checking grammar...")

        # Prompt untuk LLM
        prompt = (
            f"Pengguna mengucapkan: \"{sentence}\"\n"
            "Perbaiki tata bahasa dari kalimat tersebut (kalimat dalam Bahasa Inggris).\n"
            "Kemudian berikan penjelasan singkat dalam Bahasa Indonesia tentang kesalahan yang diperbaiki.\n\n"
            "Balas dengan format:\n"
            "[Corrected] kalimat yang sudah diperbaiki.\n"
            "[Explanation] penjelasan dalam Bahasa Indonesia."
        )

        result = ollama.generate(prompt).strip()
        result = result.replace("*", "")

        # Parsing hasil
        if "[Corrected]" in result and "[Explanation]" in result:
            parts = result.split("[Explanation]")
            corrected = parts[0].replace("[Corrected]", "").strip()
            explanation = parts[1].strip()
        else:
            corrected = result
            explanation = ""

        # Tampilkan hasil
        speak_and_display(
            f"Corrected sentence: {corrected}",
            lang="en",
            mode="scroll",
            lcd=lcd
        )

        if explanation:
            speak_and_display(
                f"Penjelasan: {explanation}",
                lang="id",
                mode="scroll",
                lcd=lcd
            )

        # Tanya ulang
        if not tanya_ulang_grammar(lcd=lcd):
            break
