# utils/cleaned_text.py
import re
import unicodedata

# --- Regex precompiled untuk hapus emoji & ekspresi ---
EMOJI_PATTERN = re.compile(
    "[" 
    "\U0001F600-\U0001F64F"  # Emotikon wajah
    "\U0001F300-\U0001F5FF"  # Simbol & pictogram
    "\U0001F680-\U0001F6FF"  # Transport & simbol
    "\U0001F1E0-\U0001F1FF"  # Bendera
    "\U00002702-\U000027B0"  # Simbol tambahan
    "\U000024C2-\U0001F251"  # Simbol tambahan lainnya
    "]+",
    flags=re.UNICODE,
)

EKSPRESI_PATTERN = re.compile(r"\([^)]*\)")  # Hapus isi dalam tanda kurung

# Karakter kutip umum yang sering bikin TTS mengeja simbol
QUOTE_CHARS = "\"'`“”‘’«»‹›„‟‚‛"


def hapus_emoji_dan_ekspresi(text: str) -> str:
    """
    Hapus emoji dan ekspresi dalam tanda kurung dari teks.
    
    Args:
        text (str): Teks input.
    
    Returns:
        str: Teks yang sudah dibersihkan.
    """
    text = EMOJI_PATTERN.sub("", text)
    text = EKSPRESI_PATTERN.sub("", text)
    return text.strip()


def clean_for_tts(text: str) -> str:
    """
    Bersihkan teks agar aman untuk TTS:
    - Normalisasi unicode (NFKC)
    - Hapus markdown/backtick/quote
    - Ganti '/' → 'atau'
    - Hapus emoji & ekspresi
    - Ganti URL dengan kata 'tautan'
    - Rapikan spasi
    
    Args:
        text (str): Teks asli dari model/LLM.
    Returns:
        str: Teks bersih siap dibacakan.
    """
    if not text:
        return ""

    # Normalisasi unicode (ubah fullwidth, tanda mirip, dsb.)
    t = unicodedata.normalize("NFKC", text)

    # Hapus blok code fence ```...``` dan inline `code`
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    t = re.sub(r"`([^`]*)`", r"\1", t)

    # Hilangkan bullet dan simbol markup umum
    t = t.replace("*", "").replace("•", "").replace("–", "-")

    # Ganti slash dengan kata "atau"
    t = t.replace("/", " atau ")

    # Hilangkan semua jenis tanda kutip (lurus/keriting/backtick)
    t = re.sub(f"[{re.escape(QUOTE_CHARS)}]+", "", t)

    # Ganti URL agar tidak dieja karakter per karakter
    t = re.sub(r"https?://\S+", " tautan ", t)

    # Hapus emoji dan ekspresi dalam tanda kurung
    t = hapus_emoji_dan_ekspresi(t)

    # Rapikan spasi
    t = re.sub(r"\s+", " ", t).strip()
    return t
