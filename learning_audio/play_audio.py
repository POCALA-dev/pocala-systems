import os
import random
import subprocess
import signal
import time
from inout.recorder import record_once, button  
from inout.whisper_transcriber import transcribe_auto
from inout.piper_output import speak_and_display
from utils.response_check import is_yes, is_no, is_repeat, is_exit
from utils.path_helper import get_resource_path

# Folder utama tempat audio learning
AUDIO_BASE = get_resource_path("learning_audio")

GENRES = {
    "recommended": ["recommended", "song", "so", "lag", "rec", "music"],
    "podcast": ["podcast", "story", "talk", "pot", "pod", "cas"],
    "kids_learning": ["kids", "anak", "learning", "learn", "belajar"],
    "instrumental": ["instrumental", "ins", "acoustic", "instrumen"]
}


def detect_genre(user_input: str):
    """Deteksi genre berdasarkan keyword."""
    lowered = user_input.lower()
    for genre, keywords in GENRES.items():
        if any(kw in lowered for kw in keywords):
            return genre
    return None


def list_audio_files(genre):
    """Ambil daftar file audio dari folder genre tertentu."""
    folder = os.path.join(AUDIO_BASE, genre)
    if not os.path.exists(folder):
        return []
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".mp3", ".wav"))
    ]


def play_audio_file(file_path, lcd=None):
    """Putar file audio dengan aplay/mpg123, bisa di-skip dengan tombol."""
    filename = os.path.basename(file_path)
    title = os.path.splitext(filename)[0]
    if lcd:
        lcd.display_text(f"Now Playing:\n{title}")
    print(f"[PLAYING] {title}")

    try:
        if file_path.lower().endswith(".wav"):
            process = subprocess.Popen(["aplay", "-q", file_path])
        elif file_path.lower().endswith(".mp3"):
            process = subprocess.Popen(["mpg123", "-q", file_path])
        else:
            return False

        while process.poll() is None:
            if not button.is_pressed:  # ditekan → skip
                print("[SKIP] Audio diskip.")
                process.send_signal(signal.SIGTERM)
                time.sleep(0.2)  # debounce
                return True
            time.sleep(0.1)
        
        return False  # False = selesai normal
            
    except Exception as e:
        print(f"[ERROR] gagal memutar {file_path}: {e}")
        return False


def play_playlist(files, lcd=None):
    """Putar semua file di playlist dengan fitur skip."""
    for f in files:
        skipped = play_audio_file(f, lcd=lcd)
        if skipped:
            continue  # langsung lompat ke file berikutnya


def ask_replay(lcd=None) -> bool:
    """Tanya apakah user mau memutar playlist lain."""
    speak_and_display("Do you want to play another playlist?", lang="en", lcd=lcd)

    while True:
        audio = record_once(filename="ask_replay_audio.wav", lcd=lcd)
        if audio is None:
            speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
            continue

        reply = (transcribe_auto(audio, lcd=lcd) or "").lower()
        print(f"[REPLAY REPLY] {reply}")

        if is_repeat(reply):
            speak_and_display("Do you want to play another playlist?", lang="en", lcd=lcd)
            continue
        if is_yes(reply):
            return True
        if is_no(reply):
            speak_and_display("Exiting learning audio mode.", lang="en", lcd=lcd)
            return False

        speak_and_display("Please say yes or no.", lang="en", lcd=lcd)


def learning_audio_mode(lcd=None):
    """
    Flow utama Learning Audio:
    1. Tanya genre
    2. Putar playlist genre tsb
    3. Setelah habis → tanya apakah mau putar lagi
    """
    speak_and_display("Welcome to learning audio mode.", lang="en", lcd=lcd)

    while True:
        # Tanyakan genre
        speak_and_display(
            "What do you want to play? You can say: Recommended songs, podcast, kids and learning songs, or instrumental?",
            lang="en",
            lcd=lcd
        )

        genre = None
        while genre is None:
            audio = record_once(filename="choose_genre.wav", lcd=lcd)
            if audio is None:
                speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
                continue

            user_input = (transcribe_auto(audio, lcd=lcd) or "").lower()
            print(f"[GENRE INPUT] {user_input}")

            if is_exit(user_input):
                speak_and_display(
                    "Exiting audio mode.",
                    lang="en",
                    lcd=lcd,
                    clear_after=True
                )
                return

            genre = detect_genre(user_input)

            if genre is None:
                speak_and_display("Sorry, I didn't recognize that playlist. Please try again.", lang="en", lcd=lcd)

        # Ambil daftar file audio
        files = list_audio_files(genre)
        if not files:
            speak_and_display("No audio files found in this category.", lang="en", lcd=lcd)
        else:
            # Acak urutan biar tidak monoton, tapi masih dalam satu genre
            random.shuffle(files)
            play_playlist(files, lcd=lcd)

        # Tanya apakah mau ulang
        if not ask_replay(lcd=lcd):
            break
