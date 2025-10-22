import io
import time
import socket
import sounddevice as sd
import soundfile as sf

from clients.gcp_client import gcp_text_to_speech
from utils.num_to_text import convert_text
from inout.piper_tts import speak_jenny, speak_nathalie  # fallback offline


class GcpTTS:
    def __init__(self, lang_code, voice_name, default_speed=1.0, max_retries=3, retry_delay=1):
        """
        Wrapper Google Cloud Text-to-Speech dengan retry mechanism, print log,
        dukungan audio_ready_event, dan fallback Piper.
        """
        self.lang_code = lang_code
        self.voice_name = voice_name
        self.default_speed = default_speed
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _internet_available(self, host="8.8.8.8", port=53, timeout=7):
        """Cek apakah ada koneksi internet sebelum request."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            return True
        except (OSError, socket.timeout):
            return False

    def speak(self, text, speed=None, convert_numbers=False, audio_ready_event=None):
        """
        Ucapkan teks menggunakan Google Cloud TTS.
        Jika gagal, fallback otomatis ke PiperTTS.
        """
        if not text:
            return

        if not self._internet_available():
            print("WARNING: Tidak ada koneksi internet. Menggunakan fallback offline TTS (Piper).")
            self._fallback_offline(text)
            return

        final_text = convert_text(text, lang=self.lang_code[:2]) if convert_numbers else text
        final_speed = speed if speed is not None else self.default_speed

        audio_content = None
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"INFO: Mengambil audio GCP (percobaan {attempt}/{self.max_retries})...")
                audio_content = gcp_text_to_speech(
                    text=final_text,
                    language_code=self.lang_code,
                    voice_name=self.voice_name,
                    speaking_rate=final_speed,
                )
                if audio_content:
                    break
                print("WARNING: Tidak ada audio yang diterima dari GCP.")
            except Exception as e:
                print(f"ERROR: Gagal memanggil GCP TTS: {e}")

            if attempt < self.max_retries:
                print(f"INFO: Menunggu {self.retry_delay} detik sebelum mencoba lagi...")
                time.sleep(self.retry_delay)

        if not audio_content:
            print("WARNING: GCP TTS gagal. Menggunakan fallback offline TTS (Piper).")
            self._fallback_offline(final_text)
            return

        if audio_ready_event:
            audio_ready_event.set()

        # Playback audio
        try:
            buffer = io.BytesIO(audio_content)
            data, fs = sf.read(buffer, dtype='int16')
            #print(f"INFO: Memutar audio ({fs} Hz)...")
            sd.play(data, fs)
            sd.wait()
        except Exception as e:
            print(f"ERROR: Gagal memutar audio GCP: {e}")
            try:
                with open("tts_fallback.wav", "wb") as f:
                    f.write(audio_content)
                #print("INFO: Audio disimpan ke tts_fallback.wav sebagai fallback.")
            except Exception as save_err:
                print(f"CRITICAL: Gagal menyimpan file fallback: {save_err}")
            # fallback offline juga bisa dijalankan di sini
            self._fallback_offline(final_text)

    def _fallback_offline(self, text):
        """Gunakan PiperTTS sebagai cadangan TTS offline."""
        if self.lang_code.startswith("en"):
            speak_jenny(text)
        else:
            speak_nathalie(text)


# === Instance TTS ===
# Higher Models
#gcp_en_tts = GcpTTS(lang_code="en-US", voice_name="en-US-Chirp3-HD-Despina")
#gcp_id_tts = GcpTTS(lang_code="id-ID", voice_name="id-ID-Chirp3-HD-Despina")

# Standard Models
gcp_en_tts = GcpTTS(lang_code="en-US", voice_name="en-US-Standard-F")
gcp_id_tts = GcpTTS(lang_code="id-ID", voice_name="id-ID-Standard-A")


# === Shortcut ===
def speak_en(text, speed=None, audio_ready_event=None):
    gcp_en_tts.speak(text, speed=speed, convert_numbers=True, audio_ready_event=audio_ready_event)


def speak_id(text, speed=None, audio_ready_event=None):
    gcp_id_tts.speak(text, speed=speed, convert_numbers=True, audio_ready_event=audio_ready_event)
    
