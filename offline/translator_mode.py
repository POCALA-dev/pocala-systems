from offline.translator_init import Translator
from inout.whisper_transcriber import transcribe_auto
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from utils.response_check import is_exit


def translator_mode(lcd=None):
    """
    Mode penerjemah interaktif yang mendeteksi bahasa input otomatis.
    Mendukung perintah keluar dan menampilkan hasil terjemahan.
    """
    speak_and_display("Welcome to translator mode. Loading...", lang="en", lcd=lcd)

    # loading model
    translator = Translator()

    speak_and_display("Translator is Ready! Now input your sentence.", lang="en", lcd=lcd)

    interaction_count = 0  # hitung berapa kali user sudah input

    while True:
        # Rekam input suara pengguna
        audio = record_once(filename="translator_input.wav", lcd=lcd)

        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        # Transkripsi otomatis (deteksi bahasa)
        text = transcribe_auto(audio, lcd=lcd).strip()

        if not text:
            speak_and_display("Sorry, I didn't catch that. Please try again.", lang="en", lcd=lcd)
            continue

        print(f"[INPUT] {text}")

        # Deteksi perintah keluar eksplisit
        if is_exit(text):
            speak_and_display("Exiting translator mode. Goodbye!", lang="en", lcd=lcd, clear_after=True)
            break

        try:
            # Lakukan terjemahan dengan model yang sesuai arah bahasanya
            result = translator.translate(text)
            print(f"[TRANSLATION] {result}")

            # Deteksi arah bahasa
            lang, target_lang, _ = translator.detect_direction(text)

            # Tampilkan hasil terjemahan dengan mode scroll agar panjang bisa terbaca
            speak_and_display(result, lang=target_lang, mode="scroll", lcd=lcd)

        except Exception as e:
            # Tangani error jika model gagal menerjemahkan
            speak_and_display(
                "Sorry, I couldnâ€™t translate that. Please try speaking in Indonesian or English.",
                lang="en", lcd=lcd
            )
            print("[ERROR]", e)
            continue

        interaction_count += 1

        # Informasi ke pengguna bahwa sistem siap input lagi
        if interaction_count % 5 == 0:
            # Pengingat keluar setiap 5 interaksi
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
