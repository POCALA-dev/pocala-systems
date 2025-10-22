import os
import langid
import subprocess
import threading
from inout.whisper_transcriber import transcribe_auto
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from utils.response_check import is_yes, is_no, is_exit
from utils.path_helper import get_resource_path
from control.volume_control import get_current_volume


HELP_KEYWORDS = {
    "home": ["home", "menu", "utama", "beranda"],
    "online": ["online", "mode online", "daring"],
    "offline": ["offline", "mode offline", "off", "luring"],
    "vocabulary": ["vocabulary", "kosakata", "arti kata", "fuck", "fck", "bul", "lary", "lari"],
    "translator": ["trans", "penerjemah"],
    "assistant": ["assist", "asisten"],
    "grammar": ["gra", "mar", "tata bahasa", "tata"],
    "question": ["question", "soal", "exercise"],
    "ask": ["ask", "tanya"],
    "speaking": ["speaking", "bicara", "partner"],
    "button": ["but", "ton", "tom", "bol", "reset"],
    "volume": ["vol", "suara", "keras", "lembut"],
    "about": ["about", "tentang", "siapa", "who"],
}

# Muat stopword ID sekali saja
STOPWORDS_ID = set()
stopword_path = get_resource_path("resource", "stopword-id.txt")
if os.path.exists(stopword_path):
    with open(stopword_path, "r", encoding="utf-8") as f:
        STOPWORDS_ID = {line.strip().lower() for line in f if line.strip()}


def detect_lang(text: str) -> str:
    """
    Deteksi bahasa user (id/en).
    Urutan:
      1. Keyword check
      2. langid classify
      3. fallback stopword
    """
    lowered = text.lower().strip()

    # 1. Keyword explicit
    if lowered.startswith("indonesia:") or lowered.startswith("bahasa:"):
        return "id"
    if lowered.startswith("english:") or lowered.startswith("inggris:"):
        return "en"

    # 2. Langid classify
    try:
        lang, _ = langid.classify(text)
    except Exception:
        lang = None

    # 3. Fallback stopword check
    if lang not in ("id", "en"):
        words = {w for w in lowered.split()}
        if words:
            id_matches = words & STOPWORDS_ID
            if len(id_matches) / len(words) > 0.2:  # threshold 20%
                lang = "id"
            else:
                lang = "en"
        else:
            lang = "en"

    return lang


def detect_help_topic(text: str):
    """Return the help topic name based on detected keywords."""
    text = text.lower()
    for topic, keywords in HELP_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return topic
    return None


def load_help_text(topic: str, lang: str) -> str:
    """Membaca teks bantuan dari file txt."""
    txt_path = get_resource_path("help", f"{lang}/{topic}.txt")
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def play_help(topic: str, lang: str = "en", lcd=None):
    """Tampilkan teks + mainkan audio help berdasarkan topik & bahasa."""
    text = load_help_text(topic, lang)
    if not text:
        speak_and_display("Sorry, I don't have help for that topic.", lang="en", lcd=lcd)
        return

    audio_path = get_resource_path("help", f"{lang}/{topic}.wav")
    if not os.path.exists(audio_path):
        # fallback kalau audio tidak ada → tetap tampilkan teks
        speak_and_display(text, lang=lang, lcd=lcd, mode="scroll")
        print(f"[HELP] Audio not found for {topic} ({lang})")
        return

    # jalankan audio di thread terpisah
    def play_audio():
        subprocess.run(["aplay", audio_path])
    
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()

    # tampilkan teks saat audio mulai
    if lcd:
        lcd.scroll_text(text, speed=0.08)

    # tunggu audio selesai sebelum lanjut
    audio_thread.join()


def tanya_ulang_help(lcd=None) -> bool:
    """Tanya user apakah mau minta bantuan topik lain."""
    speak_and_display("Do you want another help?", lang="en", lcd=lcd)

    while True:
        audio = record_once(filename="ask_repeat_help.wav", lcd=lcd)
        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        reply = (transcribe_auto(audio, lcd=lcd) or "").lower()
        print(f"[HELP REPLY] {reply}")

        if is_no(reply):
            speak_and_display("Exiting help. Goodbye!", lang="en", lcd=lcd)
            return False
        if is_yes(reply):
            return True

        speak_and_display("I didn't understand. Please say yes or no.", lang="en", lcd=lcd)


def help_mode(lcd=None):
    """
    Flow utama Help Mode:
    1. Tanya "How can I help you?"
    2. Rekam suara user
    3. Deteksi topik + bahasa
    4. Tampilkan teks & mainkan audio sesuai topik
    5. Tanya apakah mau help topik lain
    """
    speak_and_display("Welcome to help menu", lang="en", lcd=lcd)

    while True:
        speak_and_display(
            "How can I help you?",
            lang="en",
            lcd=None
        )
        if lcd:
            lcd.display_text("Home, Online, Offline, Vocabulary, Translator, Assistant, "
                             "Grammar, Ask, Question, Speaking, Button, Volume, About")

        while True:
            audio = record_once(filename="help_mode_input.wav", lcd=lcd)
            if audio is None:
                speak_and_display("No audio detected. Let's try again.", lang="en", lcd=lcd)
                continue

            user_input = (transcribe_auto(audio, lcd=lcd) or "").strip().lower()
            if not user_input:
                speak_and_display("Sorry, I didn't catch that. Let's try again.", lang="en", lcd=lcd)
                continue
                
            print(f"[HELP MODE INPUT]: {user_input}")
            
            if is_exit(user_input):
                speak_and_display(
                    "Exiting help menu.", 
                    lang="en", 
                    lcd=lcd, 
                    clear_after=True
                )
                return
                
            topic = detect_help_topic(user_input)

            if topic is None:
                speak_and_display("Sorry, I didn't recognize that help. Please try again.", lang="en", lcd=lcd)
                continue
            break

        lang = detect_lang(user_input)
        print(f"[HELP DETECTED LANG] {lang}")

        # Khusus volume langsung generate TTS
        if topic == "volume":
            vol = get_current_volume()
            if lang == "id":
                speak_and_display(f"Volume saat ini adalah {vol} persen.", lang="id", lcd=lcd)
            else:
                speak_and_display(f"The current volume is {vol} percent.", lang="en", lcd=lcd)
        else:
            play_help(topic, lang=lang, lcd=lcd)

        if not tanya_ulang_help(lcd=lcd):
            break
