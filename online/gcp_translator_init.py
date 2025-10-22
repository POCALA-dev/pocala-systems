# Versi online dari translator menggunakan Google Cloud Translation API.

import langid
from utils.path_helper import get_resource_path
from clients.gcp_client import gcp_translate_text

# --- Load stopword Indonesia ---
STOPWORDS_ID = set()
stopword_path = get_resource_path('resource', 'stopword-id.txt')
with open(stopword_path, 'r', encoding='utf-8') as f:
    STOPWORDS_ID = {line.strip().lower() for line in f if line.strip()}


class GcpTranslator:
    """
    Wrapper untuk Google Cloud Translation API dengan deteksi arah otomatis.
    """

    def __init__(self):
        """Inisialisasi GcpTranslator (tidak memerlukan konfigurasi tambahan)."""
        print("[INFO] GcpTranslator (Online) siap digunakan.")

    def detect_direction(self, text):
        """
        Menentukan arah terjemahan (source & target lang) dan membersihkan teks input.
        Memperkuat deteksi bahasa dengan stopword Indonesia.

        Args:
            text (str): Teks input pengguna.

        Returns:
            tuple: (source_lang, target_lang, clean_text)
                - source_lang (str | None): 'id', 'en', atau None (auto)
                - target_lang (str): 'id' atau 'en'
                - clean_text (str): Teks input yang sudah dibersihkan dari kata kunci
        """
        lowered = text.lower().strip()

        # Deteksi dari kata kunci
        indo_keywords = sorted(["indonesia", "bahasa", "indo"], key=len, reverse=True)
        eng_keywords = sorted(["english", "inggris", "eng"], key=len, reverse=True)

        for keyword in indo_keywords:
            if lowered.startswith(keyword):
                clean_text = lowered.replace(keyword, "", 1).lstrip(" :;")
                return "id", "en", clean_text

        for keyword in eng_keywords:
            if lowered.startswith(keyword):
                clean_text = lowered.replace(keyword, "", 1).lstrip(" :;")
                return "en", "id", clean_text

        # Deteksi otomatis menggunakan langid
        try:
            lang, _ = langid.classify(text)
        except Exception:
            lang = None

        # Perkuat deteksi dengan stopword
        if not lang or lang not in ("id", "en"):
            words = {w.lower() for w in text.split()}
            id_matches = words & STOPWORDS_ID
            lang = "id" if len(id_matches) / max(len(words), 1) > 0.2 else "en"

        target_lang = "en" if lang == "id" else "id"
        return lang, target_lang, text

    def translate(self, text):
        """
        Menerjemahkan teks menggunakan Google Cloud Translation API.

        Args:
            text (str): Teks yang akan diterjemahkan.

        Returns:
            tuple: (translated_text, target_lang)
                - translated_text (str): Hasil terjemahan
                - target_lang (str): 'id' atau 'en'

        Raises:
            Exception: Jika GCP gagal atau terjemahan kosong.
        """
        if not text:
            return "", "id"

        source_lang, target_lang, clean_text = self.detect_direction(text)

        # Validasi bahasa target
        if target_lang not in ("id", "en"):
            target_lang = "en"

        if source_lang == target_lang:
            return clean_text, target_lang

        print(f"[*] Menerjemahkan dari '{source_lang or 'auto'}' ke '{target_lang}'...")

        # Memanggil GCP tanpa fallback offline
        translated_text = gcp_translate_text(
            text=clean_text,
            target_language=target_lang,
            source_language=source_lang
        )

        if not translated_text.strip():
            raise ValueError("Terjemahan kosong dari GCP")

        return translated_text, target_lang
