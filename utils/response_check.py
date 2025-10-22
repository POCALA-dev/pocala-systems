def is_yes(text):
    """
    Deteksi apakah input teks mengandung ekspresi afirmatif (setuju).
    """
    yes_keywords = [
        "yes", "ya", "yup", "sure", "oke",
        "iya", "ayo", "lanjut", "yeah", "yea", "betul"
    ]
    text = text.lower().strip()
    return any(word in text for word in yes_keywords)


def is_no(text):
    """
    Deteksi apakah input teks mengandung ekspresi negatif (menolak).
    """
    no_keywords = [
        "no", "tidak", "gak", "nggak", "ga",
        "cukup", "nope", "not", "jangan", "nein"
    ]
    text = text.lower().strip()
    return any(word in text for word in no_keywords)


def is_exit(text):
    """
    Deteksi apakah input teks mengandung perintah keluar eksplisit.
    """
    exit_keywords = [
        "exit", "x it", "x-sit"
    ]
    text = text.lower().strip()
    return any(word in text for word in exit_keywords)


def is_clear_context(text):
    """
    Deteksi apakah input teks mengandung perintah untuk menghapus atau mereset konteks.
    """
    clear_keywords = [
        "hapus konteks", "reset konteks", "lupakan", "forget context",
        "clear context", "bersihkan konteks", "reset memory", "clear memory",
        "forget memory", "hapus memori", "hapus ingatan", "bersihkan ingatan"
    ]
    text = text.lower().strip()
    return any(word in text for word in clear_keywords)


def is_repeat(text):
    """
    Deteksi apakah input teks mengandung permintaan untuk mengulang pertanyaan.
    """
    repeat_keywords = [
        "ulang", "ulangi", "repeat", "say again", "once more",
        "bisa diulang", "repeat please", "ulang lagi", "rip"
    ]
    text = text.lower().strip()
    return any(word in text for word in repeat_keywords)
    
    
def is_help(text: str) -> bool:
    """
    Deteksi apakah input user meminta 'help'.
    """
    keywords = ["help", "bantuan", "panduan", "guide", "manual", "cara pakai", "hell"]
    text = text.lower().strip()
    return any(word in text for word in keywords)


def is_status(text: str) -> bool:
    """
    Deteksi apakah input user memilih 'status'.
    """
    keywords = ["status", "informasi", "cek status", "info", "statistik", "stat"]
    text = text.lower().strip()
    return any(word in text for word in keywords)
