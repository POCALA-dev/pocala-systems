# Mode untuk tanya jawab interaktif menggunakan Google Cloud Platform.
import time
from clients.gcp_client import gcp_gemini_generate, gemini_model
from inout.gcp_transcriber import transcribe_auto
from inout.recorder import record_once
from inout.gcp_output import speak_and_display
from utils.response_check import is_yes, is_no


def pilih_bahasa_input(lcd=None):
    """
    Meminta pengguna memilih bahasa input (Bahasa Indonesia atau English).
    Mengembalikan string kode bahasa: 'en' atau 'id'.
    """
    speak_and_display(
        "Welcome to ask mode. Please choose your input language. English or Indonesia",
        lang="en", lcd=lcd
    )

    while True:
        audio = record_once(filename="lang_choice_ask.wav", lcd=lcd)
        if not audio:
            continue

        lang_input = transcribe_auto(audio, lcd=lcd).lower()

        if "english" in lang_input or "inggris" in lang_input:
            speak_and_display(
                "Input language set to English.", lang="en", lcd=lcd
            )
            return "en"
        elif "indonesia" in lang_input or "indo" in lang_input:
            speak_and_display(
                "Bahasa input disetel ke Indonesia.", lang="id", lcd=lcd
            )
            return "id"
        else:
            speak_and_display(
                "Language not recognized. Let's try again.",
                lang="en", lcd=lcd
            )


def tanya_ulang_ask(lang="en", lcd=None):
    """
    Menanyakan kepada pengguna apakah ingin bertanya lagi.
    """
    prompt = (
        "Do you want to ask another question?"
        if lang == "en"
        else "Ingin tanya lagi?"
    )
    speak_and_display(prompt, lang=lang, lcd=lcd)

    while True:
        audio = record_once(filename="ask_again_ask.wav", lcd=lcd)
        if not audio:
            continue

        reply = transcribe_auto(audio, lcd=lcd).lower()
        print(f"[USER REPLY]: {reply}")

        if is_no(reply):
            goodbye_prompt = (
                "Exiting ask function. Goodbye!"
                if lang == "en"
                else "Keluar dari fungsi tanya. Sampai jumpa!"
            )
            speak_and_display(goodbye_prompt, lang=lang, lcd=lcd)
            return False
        elif is_yes(reply):
            return True
        else:
            error_prompt = (
                "I didn't understand. Please say yes or no."
                if lang == "en"
                else "Saya tidak mengerti. Ucapkan ya atau tidak."
            )
            speak_and_display(error_prompt, lang=lang, lcd=lcd)


def ask_mode(lcd=None):
    """
    Mode untuk bertanya kepada Gemini secara interaktif
    tanpa konteks percakapan.
    """
    if not gemini_model:
        speak_and_display(
            "Ask mode cannot be started. Gemini API key is missing.",
            "en", lcd
        )
        return

    lang = pilih_bahasa_input(lcd=lcd)

    while True:
        prompt_ask = (
            "Please ask your question."
            if lang == "en"
            else "Silakan ajukan pertanyaan Anda."
        )
        speak_and_display(prompt_ask, lang=lang, lcd=lcd)

        # Rekam pertanyaan sampai valid
        while True:
            audio = record_once(filename="ask_question.wav", lcd=lcd)
            if not audio:
                continue

            question = transcribe_auto(audio, lcd=lcd).strip()
            if not question:
                speak_and_display(
                    "I didn't catch that. Please try again.",
                    lang=lang, lcd=lcd
                )
                continue

            break

        print(f"[QUESTION] {question}")
        if lcd:
            lcd.display_text("Generating...")

        prompt_to_gemini = (
            f"Please answer this question briefly and to the point:\n{question}"
            if lang == "en"
            else f"Jawablah pertanyaan berikut secara ringkas "
                 f"dan langsung ke intinya:\n{question}"
        )

        answer = gcp_gemini_generate(prompt_to_gemini).strip().replace("*", "")

        if not answer:
            answer = (
                "Sorry, I can't answer that right now."
                if lang == "en"
                else "Maaf, tidak bisa menjawab saat ini."
            )

        # Tampilkan dan bacakan jawaban
        speak_and_display(
            f"the answer is {answer}"
            if lang == "en"
            else f"jawabannya adalah {answer}",
            lang=lang, mode="scroll", lcd=lcd
        )
        time.sleep(1)

        # Tanyakan apakah ingin bertanya lagi
        if not tanya_ulang_ask(lang=lang, lcd=lcd):
            break
