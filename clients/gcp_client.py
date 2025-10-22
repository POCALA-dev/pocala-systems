# pip install google-cloud-speech google-cloud-texttospeech google-cloud-translate google-generativeai

import os
import json
from pathlib import Path
import io
import soundfile as sf
import numpy as np
import time
from google.cloud import speech
from google.cloud import texttospeech
from google.cloud import translate_v3 as translate
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from utils.path_helper import get_resource_path

# === KONFIGURASI KREDENSIAL & API ===
CREDENTIALS_DIR = Path(get_resource_path("gcp_credential"))

SERVICE_ACCOUNT_FILE = next(CREDENTIALS_DIR.glob("*.json"), None)
if not SERVICE_ACCOUNT_FILE:
    raise FileNotFoundError(f"Service Account JSON tidak ditemukan di: {CREDENTIALS_DIR}")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(SERVICE_ACCOUNT_FILE)

with open(SERVICE_ACCOUNT_FILE, "r") as f:
    PROJECT_ID = json.load(f).get("project_id")
if not PROJECT_ID:
    raise ValueError("Atribut 'project_id' tidak ditemukan di file Service Account.")

GEMINI_API_KEY_FILE = CREDENTIALS_DIR / "gemini_api_key.txt"
gemini_model = None
if GEMINI_API_KEY_FILE.exists():
    api_key = GEMINI_API_KEY_FILE.read_text().strip()
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel("gemini-flash-lite-latest")

speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()
translate_client = translate.TranslationServiceClient()


def gcp_transcribe_audio(audio_bytes, language_code="id-ID"):
    """
    Mengubah audio menjadi teks menggunakan Google Cloud Speech-to-Text.
    
    Args:
        audio_bytes (bytes): Data audio mentah.
        language_code (str): Kode bahasa (misal 'id-ID', 'en-US', atau 'und' untuk auto-detect).
    
    Returns:
        str: Hasil transkripsi teks.
    """
    if not audio_bytes:
        return ""
    try:
        data, samplerate = sf.read(io.BytesIO(audio_bytes))
        audio = speech.RecognitionAudio(content=audio_bytes)

        config_args = {
            "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
            "sample_rate_hertz": samplerate,
            "enable_automatic_punctuation": True,
        }
        
        if language_code == "und":
            config_args["language_code"] = "id-ID"
            config_args["alternative_language_codes"] = ["en-US"]
            print("[INFO] STT mode: Auto-detect (ID/EN)")
        else:
            config_args["language_code"] = language_code
            print(f"[INFO] STT mode: Specific language ({language_code})")

        config = speech.RecognitionConfig(**config_args)
        
        resp = speech_client.recognize(config=config, audio=audio, timeout=20)

        # Ambil semua hasil transkrip dan gabungkan
        if resp.results:
            transcripts = [r.alternatives[0].transcript for r in resp.results]
            return " ".join(transcripts)
        return ""

    except GoogleAPIError as e:
        print(f"[ERROR STT] {e}")
        return ""
    except Exception as e:
        print(f"[ERROR STT Tak Terduga] {e}")
        return ""
        
        
def gcp_text_to_speech(text, language_code="id-ID", voice_name=None, speaking_rate=1.0):
    """
    Mengubah teks menjadi audio menggunakan Google Cloud Text-to-Speech.
    Hasil audio di-boost dan ternormalisasi agar setara dengan Piper TTS.
    
    Returns:
        bytes: Data audio hasil TTS dalam format WAV PCM16.
    """
    if not text:
        return b""

    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name or f"{language_code}-Wavenet-A"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speaking_rate,
            volume_gain_db=6.0  # boost volume +6 dB
        )

        resp = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice_params, audio_config=audio_config
        )

        # Load audio bytes → float32
        data, samplerate = sf.read(io.BytesIO(resp.audio_content), dtype="float32")

        # Normalisasi peak ke ±1
        if len(data) > 0:
            peak = np.max(np.abs(data))
            if peak > 0:
                data = data / peak

        # Convert kembali ke WAV PCM16
        buf = io.BytesIO()
        sf.write(buf, data, samplerate, format="WAV", subtype="PCM_16")
        return buf.getvalue()

    except GoogleAPIError as e:
        print(f"[ERROR TTS] {e}")
        return b""

        
def gcp_translate_text(text, target_language="en", source_language=None):
    """
    Menerjemahkan teks menggunakan Google Cloud Translate.
    
    Args:
        text (str): Teks yang akan diterjemahkan.
        target_language (str): Kode bahasa tujuan.
        source_language (str, optional): Kode bahasa sumber.
    
    Returns:
        str: Hasil terjemahan.
    """
    if not text:
        return ""
    try:
        parent = f"projects/{PROJECT_ID}/locations/global"
        resp = translate_client.translate_text(
            parent=parent,
            contents=[text],
            target_language_code=target_language,
            source_language_code=source_language,
            mime_type="text/plain",
            timeout=10,
        )
        return resp.translations[0].translated_text if resp.translations else ""
    except GoogleAPIError as e:
        print(f"[ERROR Translate] {e}")
        return text

def gcp_gemini_generate(prompt, temperature=0.9, max_retries=3, retry_delay=1, timeout=30):
    """
    Menghasilkan teks dari prompt tunggal menggunakan Gemini.
    Dengan retry dan timeout manual.
    """
    if not gemini_model:
        raise RuntimeError("Model Gemini belum dikonfigurasi.")
    if not prompt:
        return ""

    attempt = 1
    while attempt <= max_retries:
        try:
            print(f"[INFO] Mengirim prompt ke Gemini (percobaan {attempt}/{max_retries})...")
            start_time = time.time()

            config = genai.types.GenerationConfig(temperature=temperature)
            resp = gemini_model.generate_content(prompt, generation_config=config)

            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Request melebihi batas {timeout} detik.")

            print(f"[INFO] Respons diterima dalam {elapsed:.2f} detik.")
            return resp.text or ""

        except Exception as e:
            print(f"[WARNING] Gagal generate dari Gemini: {e}")
            if attempt < max_retries:
                print(f"[INFO] Mencoba ulang dalam {retry_delay} detik...")
                time.sleep(retry_delay)
            attempt += 1

    return "[Gagal] Tidak ada respons setelah beberapa percobaan."


def gcp_gemini_generate_chat(prompt_or_context, context=None, temperature=0.9, max_retries=3, retry_delay=1, timeout=30):
    """
    Menghasilkan respon chat berbasis riwayat percakapan menggunakan Gemini.
    Dengan retry dan timeout manual.

    Bisa dipanggil dalam dua mode:
    1. prompt_or_context = string prompt, context = GcpChatContext → otomatis simpan ke riwayat.
    2. prompt_or_context = list of dicts (pesan manual) → langsung kirim ke Gemini.
    """
    if not gemini_model:
        raise RuntimeError("Model Gemini belum dikonfigurasi.")

    # Mode 1
    if isinstance(prompt_or_context, str) and context is not None:
        context.add_user_message(prompt_or_context)
        messages = context.get_context()
    # Mode 2
    elif isinstance(prompt_or_context, list):
        messages = prompt_or_context
    else:
        raise ValueError(
            "gcp_gemini_generate_chat() membutuhkan prompt string + context, atau list of messages."
        )

    if not messages:
        return ""

    attempt = 1
    while attempt <= max_retries:
        try:
            print(f"[INFO] Mengirim ke Gemini (percobaan {attempt}/{max_retries})...")
            start_time = time.time()

            config = genai.types.GenerationConfig(temperature=temperature)
            resp = gemini_model.generate_content(
                contents=messages,
                generation_config=config
            )

            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Request melebihi batas {timeout} detik.")

            print(f"[INFO] Respons diterima dalam {elapsed:.2f} detik.")
            output_text = resp.text or ""

            if context:
                context.mark_system_prompt_sent()
                context.add_assistant_message(output_text)

            return output_text

        except Exception as e:
            print(f"[WARNING] Gagal chat ke Gemini: {e}")
            if context and isinstance(prompt_or_context, str):
                if hasattr(context, "last_user_message") and context.last_user_message() == prompt_or_context:
                    if hasattr(context, "messages"):
                        context.messages.pop()
            if attempt < max_retries:
                print(f"[INFO] Mencoba ulang dalam {retry_delay} detik...")
                time.sleep(retry_delay)
            attempt += 1

    return "[Gagal] Tidak ada respons setelah beberapa percobaan."
