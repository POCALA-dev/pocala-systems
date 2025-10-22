from online.gcp_translator_init import GcpTranslator
from offline.translator_init import Translator  # fallback offline
from inout.gcp_transcriber import transcribe_auto
from inout.recorder import record_once
from inout.gcp_output import speak_and_display
from utils.response_check import is_exit


def gcp_translator_mode(lcd=None):
    """
    Mode penerjemah interaktif berbasis suara menggunakan GCP.
    Jika GCP gagal, otomatis fallback ke translator offline.
    """
    speak_and_display("Welcome to Translator Mode. Loading System..", lang="en", lcd=lcd)

    # Muat translator online dan offline sekali di awal
    gcp_translator = GcpTranslator()
    offline_translator = Translator()

    speak_and_display("Translator is ready! Press the button and then speak.", lang="en", lcd=lcd)

    interaction_count = 0

    while True:
        # Rekam input suara
        audio_file = record_once(filename="gcp_translate_input.wav", lcd=lcd)
        if not audio_file:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        # Transkripsi
        if lcd:
            lcd.display_text("Memproses...")
        user_text = transcribe_auto(audio_file, lcd=lcd).strip()

        if not user_text:
            speak_and_display("I didn't catch that. Please try again.", lang="en", lcd=lcd)
            continue

        print(f"[INPUT] {user_text}")
        if lcd:
            lcd.flash_message(f"Anda:\n{user_text}", duration=2)

        # Perintah keluar
        if is_exit(user_text):
            speak_and_display("Exiting Translator Mode, Good Bye!!", lang="en", lcd=lcd, clear_after=True)
            break

        # Proses terjemahan
        try:
            translated_text, target_lang = gcp_translator.translate(user_text)
            if not translated_text:
                raise ValueError("Hasil terjemahan kosong")
        except Exception as e:
            print(f"[WARNING] GCP gagal, fallback offline. Error: {e}")
            translated_text = offline_translator.translate(user_text)
            target_lang = "en" if offline_translator.detect_direction(user_text)[0] == "id-en" else "id"

        # Tampilkan hasil terjemahan
        speak_and_display(translated_text, lang=target_lang, mode="scroll", lcd=lcd)

        interaction_count += 1

        # Pengingat setiap 5 interaksi
        if interaction_count % 5 == 0:
            speak_and_display(
                "You can talk again, or say 'exit' to leave translator mode.",
                lang="en", lcd=lcd
            )
            if lcd:
                lcd.display_text("say 'exit' to quit")
        else:
            speak_and_display("You can talk again!", lang="en", lcd=None)
            if lcd:
                lcd.display_text("Listening to input...")
