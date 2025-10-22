import re

# --- Regex precompiled untuk hapus emoji & ekspresi ---
EMOJI_PATTERN = re.compile(
    "[" "\U0001F600-\U0001F64F"  # Emotikon wajah
    "\U0001F300-\U0001F5FF"      # Simbol & pictogram
    "\U0001F680-\U0001F6FF"      # Transport & simbol
    "\U0001F1E0-\U0001F1FF"      # Bendera
    "\U00002702-\U000027B0"      # Simbol tambahan
    "\U000024C2-\U0001F251"      # Simbol tambahan lainnya
    "]+",
    flags=re.UNICODE
)

EKSPRESI_PATTERN = re.compile(r"\([^)]*\)")  # Hapus isi dalam tanda kurung


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
