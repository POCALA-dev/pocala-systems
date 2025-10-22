from inout.whisper_transcriber import transcribe_auto, transcribe_id, transcribe_en
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from transformers import MarianTokenizer, MarianMTModel
from clients.ollama_client import OllamaClient
from utils.extract_word import extract_vocab_word
from utils.path_helper import get_resource_path
from utils.response_check import is_yes, is_no


class VocabTranslator:
    def __init__(self, direction="id_en"):
        """
        Inisialisasi model translator satu arah (id_en atau en_id).
        Menggunakan MarianMT dengan model lokal (offline).
        """
        assert direction in ["id_en", "en_id"]
        self.model_path = get_resource_path("MT_Model", direction)
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_path)
        self.model = MarianMTModel.from_pretrained(self.model_path)

    def translate(self, text):
        """
        Menerjemahkan teks input (kata atau frasa pendek).
        """
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        output = self.model.generate(**inputs)
        return self.tokenizer.decode(output[0], skip_special_tokens=True)


def pilih_bahasa_input(lcd=None):
    """
    Menanyakan pilihan bahasa input ke pengguna.
    """
    speak_and_display(
        "Welcome to vocabulary mode. Please choose language: English or Indonesia.",
        lang="en", lcd=lcd)
    while True:
        audio = record_once(filename="lang_choice.wav", lcd=lcd)
        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        lang_input = transcribe_auto(audio, lcd=lcd).lower()

        if "english" in lang_input or "inggris" in lang_input:
            speak_and_display("Input language is set to English.", lang="en", lcd=lcd)
            return "en"
        elif "indonesia" in lang_input or "indo" in lang_input:
            speak_and_display("Bahasa input diatur ke Indonesia.", lang="id", lcd=lcd)
            return "id"
        else:
            speak_and_display("Language not recognized. Let's try again.", lang="en", lcd=lcd)


def load_model_dan_tools(lang, lcd=None):
    """
    Memuat model translator dan phonetic converter untuk bahasa Inggris.
    """
    import eng_to_ipa
    direction = "id_en" if lang == "id" else "en_id"
    speak_and_display("Loading System..." if lang == "en" else "Memuat Sistem...", lang=lang, lcd=lcd)
    translator = VocabTranslator(direction=direction)
    return translator, lambda word: eng_to_ipa.convert(word)


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


def ambil_definisi(word, lang, ollama):
    """
    Mengambil definisi dan contoh kalimat dari model Ollama.
    Output dalam format khusus: [Definition] ... [Example] ...
    """
    prompt = (
        f"Jelaskan arti dari kata '{word}' dalam Bahasa Indonesia secara singkat dan to the point. "
        f"Kemudian berikan satu contoh kalimat penggunaannya dalam Bahasa Inggris.\n\n"
        f"Format output:\n[Definition] ...\n[Example] ..."
    )

    result = ollama.generate(prompt).strip().replace("*", "")
    
    if "[Definition]" in result and "[Example]" in result:
        parts = result.split("[Example]")
        definition = parts[0].replace("[Definition]", "").strip()
        example = parts[1].strip()
        return definition, example

    return result.strip(), ""



def tampilkan_hasil(word, translated, ipa, definition, example, lang, lcd=None):
    """
    Menampilkan hasil akhir kepada pengguna: terjemahan, IPA, definisi, dan contoh.
    """
    if not translated or not ipa:
        speak_and_display(
            "Terjadi kesalahan saat menerjemahkan atau mengambil pelafalan."
            if lang == "id" else
            "Sorry, I couldn’t get the translation or pronunciation.",
            lang=lang, lcd=lcd
        )
        return

    if lang == "id":
        speak_and_display(f"Translate to English: {translated}", lang="en", lcd=lcd)
        if lcd:
            lcd.display_text(f"Phonetic: {ipa}")
        speak_and_display(f"Phonetic: {translated}", lang="en", lcd=None)
        speak_and_display(definition, lang="id", mode="scroll", lcd=lcd)
        if example:
            speak_and_display(f"Example of use: {example}", lang="en", mode="scroll", lcd=lcd)
    else:
        if lcd:
            lcd.display_text(f"Phonetic: {ipa}")
        speak_and_display(f"Phonetic: {word}", lang="en", lcd=None)
        speak_and_display(f"Terjemahan ke Indonesia: {translated}", lang="id", lcd=lcd)
        speak_and_display(definition, lang="id", mode="scroll", lcd=lcd)
        if example:
            speak_and_display(f"Example of use: {example}", lang="en", mode="scroll", lcd=lcd)


def tanya_ulang(lang="id", lcd=None):
    """
    Menanyakan apakah ingin mengulang sesi dengan kata lain.
    """
    speak_and_display(
        "Ingin coba kata lain?" if lang == "id"
        else "Do you want to try another word?",
        lang=lang, lcd=lcd
    )
    while True:
        audio = record_once(filename="ask_again.wav", lcd=lcd)

        if audio is None:
            speak_and_display(
                "Tidak ada audio. Coba ulangi." if lang == "id"
                else "No audio detected. Please try again.",
                lang=lang, lcd=lcd
            )
            continue

        reply = transcribe_auto(audio, lcd=lcd).lower()
        print(f"[USER REPLY] {reply}")

        if is_no(reply):
            return False
        elif is_yes(reply):
            return True
        else:
            speak_and_display(
                "Jawaban tidak dikenali. Ucapkan ya atau tidak." if lang == "id"
                else "I didn't understand. Please say yes or no.",
                lang=lang, lcd=lcd
            )


def vocabulary_mode(lcd=None):
    """
    Fungsi utama untuk menjalankan Vocabulary Mode.
    Proses:
    - Pilih bahasa
    - Muat model + phonetic
    - Dapatkan input kata dari user
    - Terjemahkan + ambil definisi
    - Tampilkan dan loop ulang jika diminta
    """
    lang = pilih_bahasa_input(lcd=lcd)
    translator, g2p_en = load_model_dan_tools(lang, lcd=lcd)
    ollama = OllamaClient(model="gemma3:1b")

    while True:
        word = ambil_kata(lang, lcd=lcd)
        print(f"[WORD DETECTED] {word}")

        try:
            if lang == "en":
                ipa = g2p_en(word)
                translated = translator.translate(word)
            else:
                translated = translator.translate(word)
                ipa = g2p_en(translated)

            if lcd:
                lcd.display_text("Mendapatkan definisi..." if lang == "id" else "Getting definition...")

            definition, example = ambil_definisi(word, lang, ollama)
            tampilkan_hasil(word, translated, ipa, definition, example, lang, lcd=lcd)

        except Exception as e:
            print("[ERROR]", e)
            speak_and_display(
                "Terjadi kesalahan sistem. Coba lagi." if lang == "id"
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
            speak_and_display(goodbye, lang=lang, lcd=lcd, clear_after=True)
            break
