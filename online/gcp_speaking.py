# Mode percakapan interaktif (speaking partner) menggunakan Google Cloud Platform.
from inout.gcp_transcriber import transcribe_auto, transcribe_en, transcribe_id
from clients.gcp_client import gcp_gemini_generate_chat, gemini_model
from utils.gcp_context_builder import GcpChatContext
from inout.recorder import record_once
from inout.gcp_output import speak_and_display
from utils.response_check import is_exit, is_clear_context
from utils.cleaned_text import hapus_emoji_dan_ekspresi


def pilih_bahasa_input(lcd=None):
    """Meminta pengguna memilih bahasa input untuk percakapan."""
    speak_and_display("Welcome to speaking function", lang="en", lcd=lcd)
    speak_and_display("Please choose your input language English or Indonesia.", lang="en", lcd=lcd)

    while True:
        audio = record_once(filename="lang_choice_speaking.wav", lcd=lcd)
        if not audio:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        lang_input = transcribe_auto(audio, lcd=lcd).lower()

        if "english" in lang_input or "inggris" in lang_input:
            speak_and_display("Language set to English.", lang="en", lcd=lcd)
            return "en"
        elif "indonesia" in lang_input or "indo" in lang_input:
            speak_and_display("Bahasa diatur ke Indonesia.", lang="id", lcd=lcd)
            return "id"
        else:
            speak_and_display("Language not recognized. Please try again.", lang="en", lcd=lcd)


def speaking_mode(lcd=None):
    """Mode percakapan dengan Gemini sebagai speaking partner."""
    if not gemini_model:
        speak_and_display(
            "Speaking mode cannot be started. Gemini API key is missing.",
            "en",
            lcd,
        )
        turn

    lang = pilih_bahasa_input(lcd=lcd)
    if not lang:
        turn

    # Sapa pengguna berdasarkan bahasa yang dipilih
    if lang == "en":
        speak_and_display(
            "Hello, my name is Pocala. I will be your speaking partner.",
            lang="en",
            lcd=lcd,
        )
    else:
        speak_and_display(
            "Halo, nama saya Pocala. Aku akan jadi teman berbicaramu.",
            lang="id",
            lcd=lcd,
        )
        
    # system prompt yang sesuai untuk Gemini
    system_prompt = (
        "You are Pocala, a friendly, patient, and supportive English-speaking conversation partner. "
        "Keep your responses natural, engaging, and not too long. Encourage the user to keep talking but not to much asking."
        if lang == "en"
        else "Kamu adalah Pocala, teman berbicara yang ramah, sabar, dan suportif dalam Bahasa Indonesia. "
        "Jaga agar balasanmu alami, menarik, dan tidak terlalu panjang. Ajak pengguna untuk terus berbicara tapi jangan terlalu banyak bertanya."
    )

    # Gunakan GcpChatContext untuk mengelola percakapan
    context = GcpChatContext(system_prompt=system_prompt, max_messages=10)
    transcribers = {"en": transcribe_en, "id": transcribe_id}
    interaction_count = 0
    
    speak_and_display(
        "Please speak." if lang == "en" else "Silakan berbicara.",
        lang=lang, lcd=lcd
    )
    
    while True:
        # Loop hingga mendapat input suara yang valid
        while True:
            audio = record_once(filename="speaking_input.wav", lcd=lcd)

            if audio is None:
                speak_and_display(
                    "No audio detected. Please try again." if lang == "en"
                    else "Tidak ada audio. Coba ulangi",
                    lang=lang,
                    lcd=lcd,
                )
                continue

            user_input = transcribers[lang](audio, lcd=lcd).strip()
            user_input = hapus_emoji_dan_ekspresi(user_input)

            if not user_input:
                speak_and_display(
                    "I didn't catch that. Please try again." if lang == "en"
                    else "Saya tidak menangkapnya. Coba ulangi",
                    lang=lang,
                    lcd=lcd,
                )
                continue

            break  # Input valid, lanjut ke proses

        # Deteksi perintah keluar
        if is_exit(user_input):
            goodbye_msg = (
                "It was nice talking to you. Goodbye!"
                if lang == "en"
                else "Senang berbicara denganmu. Sampai jumpa!"
            )
            speak_and_display(goodbye_msg, lang=lang, lcd=lcd)
            break

        # Deteksi perintah hapus konteks
        if is_clear_context(user_input):
            context.clear()
            speak_and_display(
                "Context cleared. Let's start a new topic." if lang == "en"
                else "Konteks dihapus. Mari mulai topik baru.",
                lang=lang,
                lcd=lcd,
            )
            continue
          
        # Tambahkan pesan pengguna ke konteks
        cleaned_input = (
            user_input[0].capitalize() + user_input[1:]
            if user_input
            else user_input
        )
        
        context.add_user_message(cleaned_input)
        print(f"[USER]: {cleaned_input}")
        
        if lcd:
            lcd.flash_message(f"User: {cleaned_input}", duration=2)
            lcd.display_text("Thinking..." if lang == "en" else "Berpikir...")
        
        # Retry maksimal 3x jika model tidak membalas
        response = ""
        for attempt in range(1, 4):
            try:
                # Kirim ke Gemini dengan seluruh riwayat percakapan
                response = gcp_gemini_generate_chat(context.get_context())
            except Exception as e:
                print(f"[ERROR] Gemini chat failed: {e}")
                response = ""
        
            # Bersihkan respon dari emoji, tanda kurung, dan simbol *
            response = hapus_emoji_dan_ekspresi(response.replace("*", "")).strip()
        
            if response:
                context.add_assistant_message(response)
                break
        
            print(f"[WARNING] Model tidak merespon, percobaan {attempt}/3")
            if lcd:
                lcd.flash_message(
                    f"Retry {attempt}/3" if lang == "en" else f"Mencoba ulang {attempt}/3",
                    duration=2
                )
            if attempt < 3:
                time.sleep(1)
        
        # Jika tetap tidak ada respons
        if not response:
            speak_and_display(
                "I couldn't get a response from the model." if lang == "en"
                else "Tidak ada respons dari model.",
                lang=lang, lcd=lcd
            )
            continue
        
        # Tampilkan dan bacakan respons
        speak_and_display(response, lang=lang, mode="scroll", lcd=lcd, scroll_speed=0.08)
        
        # Hitung interaksi, beri pesan setiap kelipatan 5
        interaction_count += 1
        if interaction_count % 5 == 0:
            speak_and_display(
                "You can talk again, or say 'exit' to leave speaking mode."
                if lang == "en" else
                "Kamu bisa bicara lagi, atau ucapkan 'exit' untuk berhenti.",
                lang=lang, lcd=lcd
            )
            if lcd:
                lcd.display_text("say 'exit' to quit" if lang == "en" else "ucap 'exit' untuk berhenti")
        else:
            speak_and_display(
                "You can talk again!" if lang == "en" else "Kamu bisa bicara lagi!",
                lang=lang, lcd=lcd
            )
            if lcd:
                lcd.display_text("Listening to input..." if lang == "en" else "Mendengarkan...")
