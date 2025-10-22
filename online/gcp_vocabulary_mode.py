# gcp_vocabulary_mode.py
import eng_to_ipa
from clients.gcp_client import gcp_translate_text, gcp_gemini_generate, gemini_model
from inout.gcp_transcriber import transcribe_id, transcribe_en, transcribe_auto
from inout.recorder import record_once
from inout.gcp_output import speak_and_display
from utils.response_check import is_yes, is_no
from utils.extract_word import extract_vocab_word


def pilih_bahasa_input(lcd=None):
    """
    Menanyakan pilihan bahasa input ke pengguna (ID atau EN).
    """
    speak_and_display(
        "Welcome to vocabulary mode. Please choose your input language: "
        "English or Indonesia.",
        lang="en", lcd=lcd
    )
    while True:
        audio = record_once(filename="lang_choice.wav", lcd=lcd)
        if not audio:
            speak_and_display(
                "No audio detected. Please try again.", lang="en", lcd=lcd
            )
            continue

        lang_input = transcribe_auto(audio, lcd=lcd).lower()

        if "english" in lang_input or "inggris" in lang_input:
            speak_and_display(
                "Input language is set to English.", lang="en", lcd=lcd
            )
            return "en"
        elif "indonesia" in lang_input or "indo" in lang_input:
            speak_and_display(
                "Bahasa input diatur ke Indonesia.", lang="id", lcd=lcd
            )
            return "id"
        else:
            speak_and_display(
                "Language not recognized. Let's try again.", lang="en", lcd=lcd
            )


def ambil_kata(lang, lcd=None):
    """
    Merekam, mengenali, dan mengekstrak kata kunci dari ucapan pengguna.
    """
    speak_and_display(
        "Silakan sampaikan kata apa yang ingin Kamu tau."
        if lang == "id"
        else "Please say the word you want to know.",
        lang=lang, lcd=lcd
    )

    while True:
        audio = record_once(filename="vocab_input.wav", lcd=lcd)
        if audio is None:
            speak_and_display(
                "Tidak ada audio. Coba lagi."
                if lang == "id"
                else "No audio detected. Try again.",
                lang=lang, lcd=lcd
            )
            continue  # ulangi loop

        # Gunakan transcriber sesuai bahasa
        transcribe_func = transcribe_id if lang == "id" else transcribe_en
        raw_text = transcribe_func(audio, lcd=lcd).strip()

        if not raw_text:
            speak_and_display(
                "Maaf tidak terdengar jelas. Coba ulangi."
                if lang == "id"
                else "Sorry, I couldn't catch that. Try again.",
                lang=lang, lcd=lcd
            )
            continue  # ulangi loop

        # Ekstraksi kata dari hasil transkripsi
        word = extract_vocab_word(raw_text, lang=lang)
        print(f"[RAW TEXT] {raw_text}")
        print(f"[EXTRACTED WORD] {word}")

        if word == "":
            speak_and_display(
                "Maaf kata tidak terdeteksi. Coba lagi."
                if lang == "id"
                else "Sorry, no valid word detected. Try again.",
                lang=lang, lcd=lcd
            )
            continue  # ulangi loop

        if lcd:
            lcd.flash_message(f"Kata: {word}", duration=2)

        return word



def ambil_definisi_gcp(word, lang):
    """
    Mengambil IPA, definisi, contoh kalimat, dan terjemahan contoh
    dari Google Gemini.
    """
    word_en = word

    if lang == 'id':
        word_en = gcp_translate_text(
            word, target_language='en', source_language='id'
        )
        prompt_word = word_en
    else:
        prompt_word = word

    prompt = (
        f"Word: '{prompt_word}'. "
        f"Return in this format: [IPA]: <IPA> [DEFINITION]: "
        f"<Explain only Indonesian definition> [EXAMPLE]: <English example> "
        f"[TRANSLATE]: <Example Indonesia>. Keep it short."
    )

    result = gcp_gemini_generate(prompt).strip().replace("*", "")

    ipa, definition, example_en, example_id = "", "", "", ""
    try:
        if "[IPA]:" in result:
            ipa = result.split("[IPA]:", 1)[1].split(
                "[DEFINITION]:", 1
            )[0].strip()

        if "[DEFINITION]:" in result:
            definition = result.split("[DEFINITION]:", 1)[1].split(
                "[EXAMPLE]:", 1
            )[0].strip()

        if "[EXAMPLE]:" in result:
            example_en = result.split("[EXAMPLE]:", 1)[1].split(
                "[TRANSLATE]:", 1
            )[0].strip()

        if "[TRANSLATE]:" in result:
            example_id = result.split("[TRANSLATE]:", 1)[1].strip()

    except Exception:
        return "", "Maaf, parsing gagal.", "", ""

    # Fallback IPA
    if not ipa:
        try:
            ipa_source = word_en or prompt_word
            ipa_list = eng_to_ipa.convert(ipa_source)
            if ipa_list:
                ipa = ipa_list
        except Exception as e:
            print(f"[WARNING] Gagal fallback IPA: {e}")

    # Fallback jika definisi & contoh kosong
    if not definition and not example_en:
        return ipa, "Maaf, saya tidak dapat menemukan data yang sesuai.", "", ""

    return ipa, definition, example_en, example_id


def tampilkan_hasil(
    word, translated, ipa, definition, example_en, example_id, lang, lcd=None
):
    """
    Menampilkan hasil akhir kepada pengguna secara berurutan.
    """
    if lang == "id":
        # Input: Indonesia -> Output: Inggris
        speak_and_display(
            f"Translate to English: {translated}", lang="en", lcd=lcd
        )
        if lcd:
            lcd.display_text(f"Phonetic: {ipa}")
        speak_and_display(f"Phonetic: {translated}", lang="en", lcd=None)
        speak_and_display(definition, lang="id", mode="scroll", lcd=lcd)
        if example_en:
            speak_and_display(
                f"Example of use: {example_en}",
                lang="en", mode="scroll", lcd=lcd
            )
        if example_id:
            speak_and_display(
                f"Terjemahan: {example_id}",
                lang="id", mode="scroll", lcd=lcd
            )

    else:
        # Input: Inggris -> Output: Indonesia
        if lcd:
            lcd.display_text(f"Phonetic: {ipa}")
        speak_and_display(f"Phonetic: {word}", lang="en", lcd=None)
        speak_and_display(
            f"Terjemahan ke Indonesia: {translated}", lang="id", lcd=lcd
        )
        speak_and_display(definition, lang="id", mode="scroll", lcd=lcd)
        if example_en:
            speak_and_display(
                f"Example of use: {example_en}",
                lang="en", mode="scroll", lcd=lcd
            )
        if example_id:
            speak_and_display(
                f"Terjemahan: {example_id}",
                lang="id", mode="scroll", lcd=lcd
            )


def tanya_ulang(lang, lcd=None):
    """
    Menanyakan apakah pengguna ingin mencoba kata lain.
    """
    speak_and_display(
        "Ingin coba kata lain?"
        if lang == "id"
        else "Do you want to try another word?",
        lang=lang, lcd=lcd
    )

    while True:
        audio = record_once(filename="ask_again.wav", lcd=lcd)

        if audio is None:
            speak_and_display(
                "Tidak ada audio. Coba ulangi."
                if lang == "id"
                else "No audio detected. Please try again.",
                lang=lang, lcd=lcd
            )
            continue

        reply = transcribe_auto(audio, lcd=lcd).lower()
        print(f"[USER REPLY] {reply}")

        if is_no(reply):
            return False
        if is_yes(reply):
            return True

        speak_and_display(
            "Jawaban tidak dikenali. Ucapkan ya atau tidak."
            if lang == "id"
            else "I didn't understand. Please say yes or no.",
            lang=lang, lcd=lcd
        )


def gcp_vocabulary_mode(lcd=None):
    """
    Fungsi utama untuk menjalankan Vocabulary Mode dengan GCP.
    """
    if not gemini_model:
        speak_and_display(
            "Mode Kosakata tidak bisa dijalankan karena kunci API Gemini tidak ada.",
            lang="id", lcd=lcd
        )
        return

    lang = pilih_bahasa_input(lcd=lcd)

    while True:
        word = ambil_kata(lang, lcd=lcd)

        try:
            if lcd:
                lcd.display_text(
                    "Memproses..." if lang == "id" else "Processed..."
                )

            # Tentukan arah terjemahan
            source_lang, target_lang = (
                (lang, 'en') if lang == 'id' else ('en', 'id')
            )

            # Terjemahkan kata menggunakan GCP Translate
            translated = gcp_translate_text(
                word, target_language=target_lang, source_language=source_lang
            )

            # Dapatkan IPA, definisi dan contoh dari GCP Gemini
            ipa, definition, example_en, example_id = ambil_definisi_gcp(
                word, lang
            )

            # Tampilkan semua hasilnya ke pengguna
            tampilkan_hasil(
                word, translated, ipa, definition,
                example_en, example_id, lang, lcd
            )

        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan di alur utama: {e}")
            speak_and_display(
                "Terjadi kesalahan sistem. Coba lagi."
                if lang == "id"
                else "System error occurred. Please try again.",
                lang=lang, lcd=lcd
            )
            continue

        if not tanya_ulang(lang=lang, lcd=lcd):
            goodbye = (
                "Keluar Dari Mode Kosa Kata, Sampai jumpa!"
                if lang == "id"
                else "Exiting Vocabulary Mode, Goodbye!"
            )
            speak_and_display(
                goodbye, lang=lang, lcd=lcd, clear_after=True
            )
            break
