# whisper_transcriber.py (offline)
import os
import re
import subprocess
from pathlib import Path
from utils.path_helper import get_resource_path

def clean_transcript(text):
    """Membersihkan hasil transkripsi dari karakter non-alfanumerik."""
        # Hapus karakter selain huruf, angka, spasi, dash, titik, koma, dan ?
    text = re.sub(r"[^\w\s\-\.,\?]", "", text)
    
    # Ganti spasi ganda atau lebih menjadi satu spasi
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def transcribe_whisper(audio_path, language="auto", lcd=None):
    """
    Menjalankan whisper.cpp CLI untuk melakukan transkripsi dari file audio.

    Parameter:
        audio_path : str atau Path
            Path ke file audio .wav.
        language : str
            'auto', 'id', atau 'en'.
        lcd : objek LCD (opsional)
            Untuk menampilkan status ke pengguna.

    Output:
        str : hasil transkripsi dalam bentuk teks (tanpa karakter asing).
    """
    whisper_bin = get_resource_path("whisper.cpp", "build", "bin", "whisper-cli")
    model_path = get_resource_path("whisper.cpp", "models", "ggml-base.bin")
    
    if lcd:
        lcd.clear()
        lcd.display_text("Memproses audio...")

    print(f"Memulai transkripsi dengan whisper.cpp (bahasa: {language}) ...")

    try:
        subprocess.run(
            [
                whisper_bin,
                "-m", model_path,
                "-f", audio_path,
                "-otxt",
                "-l", language,
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Proses whisper.cpp gagal: {e}")
        return ""

    result_file = Path(audio_path).with_suffix(".wav.txt")
    if not result_file.exists():
        print("[ERROR] File hasil transkripsi tidak ditemukan.")
        return ""

    with open(result_file, "r", encoding="utf-8") as f:
        result_text = f.read().strip()

    cleaned_transcript = clean_transcript(result_text)

    # Bersihkan file sementara
    os.remove(audio_path)
    os.remove(result_file)

    return cleaned_transcript


def transcribe_auto(audio_path, lcd=None):
    return transcribe_whisper(audio_path, language="auto", lcd=lcd)


def transcribe_id(audio_path, lcd=None):
    return transcribe_whisper(audio_path, language="id", lcd=lcd)


def transcribe_en(audio_path, lcd=None):
    return transcribe_whisper(audio_path, language="en", lcd=lcd)
