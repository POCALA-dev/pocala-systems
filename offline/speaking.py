import re
import time
from inout.whisper_transcriber import transcribe_auto, transcribe_en, transcribe_id
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from clients.ollama_client import OllamaClient
from utils.response_check import is_yes, is_no, is_exit, is_clear_context
from utils.ollama_context_builder import ChatContext
from utils.cleaned_text import hapus_emoji_dan_ekspresi


def pilih_bahasa_input(lcd=None) -> str:
    """Meminta pengguna memilih bahasa input via suara."""
    speak_and_display("Welcome to speaking function", lang="en", lcd=lcd)
    speak_and_display(
        "Please choose your input language English or Indonesia",
        lang="en", lcd=lcd
    )

    while True:
        audio = record_once(filename="lang_choice_speaking.wav", lcd=lcd)
        if not audio:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        lang_input = transcribe_auto(audio, lcd=lcd).lower()
        if "english" in lang_input or "inggris" in lang_input:
            speak_and_display("Input language set to English.", lang="en", lcd=lcd)
            return "en"
        elif "indonesia" in lang_input or "indo" in lang_input:
            speak_and_display("Bahasa input diatur ke Indonesia.", lang="id", lcd=lcd)
            return "id"
        else:
            speak_and_display("Language not recognized. Let's try again.", lang="en", lcd=lcd)


def speaking_mode(lcd=None):
    """Mode percakapan interaktif dengan AI sebagai speaking partner."""
    lang = pilih_bahasa_input(lcd=lcd)
    if not lang:
        return

    speak_and_display(
        "Hello, my name is Pocala. I will be your speaking partner."
        if lang == "en" else
        "Halo, nama saya Pocala. Aku akan jadi teman berbicaramu.",
        lang=lang, lcd=lcd
    )

    ollama = OllamaClient(model="gemma3:1b")
    system_prompt = (
        "You are pocala, a friendly English-speaking conversation partner. "
        "Keep the dialogue natural, helpful, and concise."
        if lang == "en" else
        "Kamu adalah pocala, teman berbicara yang ramah dalam Bahasa Indonesia. "
        "Buat obrolan terasa alami, tidak terlalu panjang, dan selalu gunakan bahasa Indonesia."
    )
    context = ChatContext(max_messages=10, system_prompt=system_prompt)
    transcribers = {"en": transcribe_en, "id": transcribe_id}
    interaction_count = 0
    
    speak_and_display(
        "Please speak." if lang == "en" else "Silakan berbicara.",
        lang=lang, lcd=lcd
    )
    
    while True:
        # Ambil input suara
        while True:
            audio = record_once(filename="speaking_input.wav", lcd=lcd)
            if not audio:
                speak_and_display(
                    "No audio detected. Please try again." if lang == "en"
                    else "Tidak ada audio. Coba ulangi",
                    lang=lang, lcd=lcd
                )
                continue

            user_input = transcribers[lang](audio, lcd=lcd).strip()
            user_input = hapus_emoji_dan_ekspresi(user_input)

            if not user_input:
                speak_and_display(
                    "I didn't catch that. Please try again." if lang == "en"
                    else "Saya tidak menangkapnya. Coba ulangi",
                    lang=lang, lcd=lcd
                )
                continue
            break

        # Perintah keluar
        if is_exit(user_input):
            speak_and_display(
                "Exiting speaking mode. Goodbye!" if lang == "en"
                else "Keluar dari speaking mode. Sampai jumpa!",
                lang=lang, lcd=lcd
            )
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

        cleaned_input = user_input.capitalize()
        print(f"[USER]: {cleaned_input}")

        if lcd:
            lcd.flash_message(f"User: {cleaned_input}", duration=2)
            lcd.display_text("Thinking..." if lang == "en" else "Berpikir...")

        # Retry maksimal 3x jika model tidak membalas
        response = ""
        for attempt in range(1, 4):
            try:
                response = ollama.chat(cleaned_input, context=context)
            except Exception as e:
                print(f"[ERROR] Ollama chat failed: {e}")
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
                
        if not response:
            speak_and_display(
                "I couldn't get a response from the model." if lang == "en"
                else "Tidak ada respons dari model.",
                lang=lang, lcd=lcd
            )
            continue

        speak_and_display(response, lang=lang, mode="scroll", lcd=lcd, scroll_speed=0.06)

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
