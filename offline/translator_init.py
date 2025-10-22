import re
from transformers import MarianMTModel, MarianTokenizer
from utils.path_helper import get_resource_path
import langid


class Translator:
    """Translator dua arah (ID-EN dan EN-ID) menggunakan model MarianMT lokal."""

    def __init__(self):
        # Muat stopword Indonesia untuk fallback deteksi
        stopword_path = get_resource_path("resource", "stopword-id.txt")
        with open(stopword_path, "r", encoding="utf-8") as f:
            self.stopwords_id = {line.strip().lower() for line in f if line.strip()}

        # Konfigurasi path model lokal
        self.models = {
            "id-en": {
                "model_name": get_resource_path("MT_Model", "id_en"),
                "tokenizer": None,
                "model": None,
            },
            "en-id": {
                "model_name": get_resource_path("MT_Model", "en_id"),
                "tokenizer": None,
                "model": None,
            },
        }
        self.load_all_models()

    def load_model(self, direction):
        """Memuat model dan tokenizer jika belum dimuat."""
        if direction in self.models and self.models[direction]["model"] is None:
            try:
                print(f"[INFO] Loading model for {direction}...")
                model_path = self.models[direction]["model_name"]
                tokenizer = MarianTokenizer.from_pretrained(model_path)
                model = MarianMTModel.from_pretrained(model_path)

                self.models[direction]["tokenizer"] = tokenizer
                self.models[direction]["model"] = model

                print(f"[OK] Model {direction} loaded.")
            except Exception as e:
                print(f"[ERROR] Gagal memuat model {direction}: {e}")

    def load_all_models(self):
        """Meload semua model agar siap digunakan."""
        for direction in self.models:
            self.load_model(direction)

    def detect_direction(self, text):
        """Deteksi arah terjemahan (id→en atau en→id)."""
        lowered = text.lower().strip()

        # Kata kunci eksplisit
        indo_keywords = sorted(["indonesia", "bahasa", "indo"], key=len, reverse=True)
        eng_keywords = sorted(["english", "inggris", "eng"], key=len, reverse=True)

        for keyword in indo_keywords:
            if lowered.startswith(keyword):
                clean_text = lowered.replace(keyword, "", 1).lstrip(" ,:;")
                return "id", "en", clean_text

        for keyword in eng_keywords:
            if lowered.startswith(keyword):
                clean_text = lowered.replace(keyword, "", 1).lstrip(" ,:;")
                return "en", "id", clean_text

        try:
            lang, _ = langid.classify(text)
        except Exception:
            lang = None

        if not lang or lang not in ("id", "en"):
            words = {w.lower() for w in text.split()}
            id_matches = words & self.stopwords_id
            if len(words) > 0 and len(id_matches) / len(words) > 0.2:
                lang = "id"
            else:
                lang = "en"

        target_lang = "en" if lang == "id" else "id"
        return lang, target_lang, text

    def _split_text(self, text):
        """
        Pisahkan teks berdasarkan . , ? ! tapi tetap simpan tanda baca.
        Hasil: list tuple (kalimat, tanda baca).
        """
        parts = re.split(r'([.,?!])', text)
        chunks = []
        for i in range(0, len(parts), 2):
            if i < len(parts):
                chunk = parts[i].strip()
                punct = parts[i+1] if i+1 < len(parts) else ""
                if chunk:
                    chunks.append((chunk, punct))
        return chunks

    def _translate_chunked(self, text, direction):
        """Translate tiap chunk lalu satukan lagi."""
        chunks = self._split_text(text)
        results = []
        tokenizer = self.models[direction]["tokenizer"]
        model = self.models[direction]["model"]

        for chunk, punct in chunks:
            inputs = tokenizer(chunk, return_tensors="pt", padding=True, truncation=False)
            output = model.generate(**inputs, max_length=512)
            translated = tokenizer.decode(output[0], skip_special_tokens=True)
            results.append(translated + punct)

        return " ".join(results).replace(" ,", ",").replace(" .", ".").replace(" ?", "?").replace(" !", "!")

    def translate(self, text, direction=None):
        """Menerjemahkan teks ID-EN atau EN-ID, dengan pemisahan tanda baca."""
        if not text.strip():
            raise ValueError("Teks input kosong.")

        if direction is None:
            source_lang, target_lang, clean_text = self.detect_direction(text)
            direction = f"{source_lang}-{target_lang}"
        else:
            if direction not in self.models:
                raise ValueError(f"Arah terjemahan '{direction}' tidak dikenali.")
            clean_text = text

        self.load_model(direction)

        if self.models[direction]["tokenizer"] is None or self.models[direction]["model"] is None:
            raise RuntimeError(f"Model untuk arah {direction} belum tersedia.")

        return self._translate_chunked(clean_text, direction)
