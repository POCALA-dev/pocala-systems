import time
from inout.whisper_transcriber import transcribe_en, transcribe_id, transcribe_auto
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from clients.ollama_client import OllamaClient
from utils.response_check import is_yes, is_no

def pilih_bahasa_input(lcd=None):
    """
    Meminta pengguna memilih bahasa input (Bahasa Indonesia atau English).

    Args:
        lcd: Objek LCD opsional untuk menampilkan teks.

    Returns:
        str: 'en' jika pengguna memilih English, 'id' jika memilih Bahasa Indonesia.
    """
    speak_and_display(
        "Welcome to ask mode. Please choose your input language. English or Indonesia",
        lang="en",
        lcd=lcd
    )

    while True:
        audio = record_once(filename="lang_choice_ask.wav", lcd=lcd)

        if audio is None:
            speak_and_display(
                "No audio detected. Please try again.",
                lang="en",
                lcd=lcd
            )
            continue

        lang_input = transcribe_auto(audio, lcd=lcd).lower()

        if "english" in lang_input or "inggris" in lang_input:
            speak_and_display(
                "Input language set to English.",
                lang="en",
                lcd=lcd
            )
            return "en"

        if "indonesia" in lang_input or "indo" in lang_input:
            speak_and_display(
                "Bahasa input disetel ke Indonesia.",
                lang="id",
                lcd=lcd
            )
            return "id"

        speak_and_display(
            "Language not recognized. Let's try again.",
            lang="en",
            lcd=lcd
        )


def tanya_ulang_ask(lang="en", lcd=None):
    """
    Menanyakan kepada pengguna apakah ingin bertanya lagi.

    Args:
        lang (str): Kode bahasa ('en' atau 'id') untuk menyesuaikan pesan.
        lcd: Objek LCD opsional untuk menampilkan teks.

    Returns:
        bool: True jika pengguna ingin bertanya lagi, False jika tidak.
    """
    speak_and_display(
        "Do you want to ask another question?"
        if lang == "en" else "Ingin tanya lagi?",
        lang=lang,
        lcd=lcd
    )

    while True:
        audio = record_once(filename="ask_again_ask.wav", lcd=lcd)

        if audio is None:
            speak_and_display(
                "No audio detected. Please try again."
                if lang == "en" else "Tidak ada audio. Coba lagi.",
                lang=lang,
                lcd=lcd
            )
            continue

        reply = transcribe_auto(audio, lcd=lcd).lower()
        print(f"[USER REPLY]: {reply}")

        if is_no(reply):
            speak_and_display(
                "Exiting ask function. Goodbye!"
                if lang == "en" else "Keluar dari fungsi tanya. Sampai jumpa!",
                lang=lang,
                lcd=lcd
            )
            return False

        if is_yes(reply):
            return True

        speak_and_display(
            "I didn't understand. Please say yes or no."
            if lang == "en" else "Saya tidak mengerti. Ucapkan ya atau tidak.",
            lang=lang,
            lcd=lcd
        )


def ask_mode(lcd=None):
    """
    Mode interaktif untuk bertanya kepada LLM menggunakan suara.

    Proses:
        1. Memilih bahasa input.
        2. Merekam dan mentranskripsi pertanyaan.
        3. Mengirim pertanyaan ke model LLM (Ollama).
        4. Menampilkan dan membacakan jawaban.
        5. Menanyakan apakah ingin bertanya lagi.

    Args:
        lcd: Objek LCD opsional untuk menampilkan teks.
    """
    lang = pilih_bahasa_input(lcd=lcd)
    ollama = OllamaClient(model="gemma3:1b")

    while True:
        speak_and_display(
            "Please ask your question."
            if lang == "en" else "Silakan ajukan pertanyaan Anda.",
            lang=lang,
            lcd=lcd
        )

        # Rekam pertanyaan sampai valid
        while True:
            audio = record_once(filename="ask_question.wav", lcd=lcd)

            if audio is None:
                speak_and_display(
                    "No audio detected. Please try again."
                    if lang == "en" else "Tidak ada audio. Coba lagi.",
                    lang=lang,
                    lcd=lcd
                )
                continue

            question = transcribe_auto(audio, lcd=lcd).strip()
            if not question:
                speak_and_display(
                    "I didn't quite catch that. Could you repeat?"
                    if lang == "en"
                    else "Saya tidak mendengar pertanyaannya. Bisakah kamu ulangi?",
                    lang=lang,
                    lcd=lcd
                )
                continue
            break

        print(f"[QUESTION] {question}")

        if lcd:
            lcd.flash_message(f"Questions: {question}", duration=3)
            lcd.display_text(
                "Generating..." if lang == "en" else "Menjawab..."
            )

        # Prompt disesuaikan bahasa
        prompt = (
            f"Please answer this question briefly and to the point:\n{question}"
            if lang == "en"
            else f"Jawablah pertanyaan berikut secara ringkas dan langsung ke intinya:\n{question}"
        )

        answer = ollama.generate(prompt).strip().replace("*", "")

        if not answer:
            speak_and_display(
                "Sorry, I can't answer that now."
                if lang == "en" else "Maaf, tidak bisa menjawab saat ini.",
                lang=lang,
                lcd=lcd
            )
            continue

        speak_and_display(
            f"the answer is {answer}"
            if lang == "en" else f"jawabannya adalah {answer}",
            lang=lang,
            mode="scroll",
            lcd=lcd
        )
        time.sleep(1)

        if not tanya_ulang_ask(lang=lang, lcd=lcd):
            break
