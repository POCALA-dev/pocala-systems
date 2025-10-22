import re
import os
from pathlib import Path
from clients.gcp_client import gcp_transcribe_audio


def clean_transcript(text):
    """
    Membersihkan hasil transkripsi dari karakter non-alfanumerik 
    kecuali spasi, tanda hubung (dash), titik, koma, tanda tanya, dan tanda seru.
    """
    if not text:
        return ""
    
    # Hapus keterangan non-verbal dalam tanda kurung siku
    text = re.sub(r'\[.*?\]', '', text)
    
    # Ganti spasi ganda atau lebih menjadi satu spasi
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def gcp_transcribe(audio_path, language_code="und", lcd=None):
    """
    Menjalankan transkripsi menggunakan Google Cloud Speech-to-Text dari file audio.

    Parameter:
        - audio_path: path ke file audio .wav.
        - language_code: Kode bahasa GCP ('id-ID', 'en-US', 'und' untuk auto).
        - lcd: objek LCD (opsional) untuk menampilkan status.

    Output:
        - Hasil transkripsi dalam bentuk teks yang sudah dibersihkan.
    """
    if not Path(audio_path).exists():
        print(f"[ERROR] File audio tidak ditemukan di: {audio_path}")
        return ""

    if lcd:
        lcd.clear()
        lcd.display_text("Membaca file...")

    print(f"[*] Membaca file audio dari: {audio_path}")
    try:
        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
    except IOError as e:
        print(f"[ERROR] Gagal membaca file audio: {e}")
        return ""
    
    # Setelah dibaca, file asli bisa langsung dihapus
    try:
        os.remove(audio_path)
        print(f"[*] File audio sementara '{audio_path}' telah dihapus.")
    except OSError as e:
        print(f"[WARNING] Gagal menghapus file audio sementara: {e}")


    if lcd:
        lcd.display_text("Transkripsi...")

    print(f"[*] Mengirim audio ke Google Cloud STT (bahasa: {language_code})...")
    raw_transcript = gcp_transcribe_audio(
        audio_bytes=audio_bytes,
        language_code=language_code
    )

    if not raw_transcript:
        print("[WARNING] Transkripsi tidak menghasilkan teks.")
        return ""

    print(f" [RAW TEXT]: {raw_transcript}")
    
    cleaned_transcript = clean_transcript(raw_transcript)
    print(f" [CLEANED]: {cleaned_transcript}")

    return cleaned_transcript


def transcribe_auto(audio_path, lcd=None): 
    """Pintasan untuk transkripsi dengan deteksi bahasa otomatis."""
    return gcp_transcribe(audio_path, language_code="und", lcd=lcd)


def transcribe_id(audio_path, lcd=None): 
    """Pintasan untuk transkripsi Bahasa Indonesia."""
    return gcp_transcribe(audio_path, language_code="id-ID", lcd=lcd)


def transcribe_en(audio_path, lcd=None):
    """Pintasan untuk transkripsi Bahasa Inggris."""
    return gcp_transcribe(audio_path, language_code="en-US", lcd=lcd)
