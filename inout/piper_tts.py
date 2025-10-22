import os
import subprocess
import sounddevice as sd
import soundfile as sf
from pathlib import Path
from utils.path_helper import get_resource_path
from utils.num_to_text import convert_text


class PiperTTS:
    def __init__(self, model_dir):
        """
        Inisialisasi objek PiperTTS.
        model_dir: nama folder model di dalam folder models/
        """
        self.model_dir = Path(get_resource_path("piper_models", model_dir))
        self.model_name = self.model_dir.name
        self.onnx = self.model_dir / f"{self.model_name}.onnx"
        self.config = self.model_dir / f"{self.model_name}.onnx.json"

        if not self.onnx.exists() or not self.config.exists():
            raise FileNotFoundError(f"Model atau config tidak ditemukan di {self.model_dir}")

    def speak(self, text, convert_numbers=False, audio_ready_event=None):
        """
        Mengubah teks menjadi audio dan memberi sinyal saat audio siap.
        - text (str): Teks untuk diucapkan.
        - convert_numbers (bool): Ubah angka menjadi kata jika True.
        - audio_ready_event (threading.Event): Objek untuk memberi sinyal.
        """
        if convert_numbers:
            text = convert_text(text, lang="en")

        out = Path(f"piper_output_{os.getpid()}.wav")  # Nama file unik berdasarkan PID

        try:
            try:
                subprocess.run(
                    [
                        "piper",
                        "--model", str(self.onnx),
                        "--config", str(self.config),
                        "--output_file", str(out)
                    ],
                    input=text.encode("utf-8"),
                    check=True,
                    capture_output=True
                )
                #print("INFO: Piper TTS berhasil membuat file audio.")
            except FileNotFoundError:
                print("ERROR: Perintah 'piper' tidak ditemukan. Pastikan Piper terinstal dan ada di PATH.")
                return
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Piper TTS gagal: {e.stderr.decode().strip()}")
                return

            # Pastikan file .wav terbentuk
            if not out.exists():
                print("ERROR: File output audio tidak ditemukan.")
                return

            if audio_ready_event:
                audio_ready_event.set()

            # Mainkan audio
            try:
                data, fs = sf.read(out, dtype='int16')
                sd.play(data, fs)
                sd.wait()
                #print("INFO: Audio berhasil diputar.")
            except sd.PortAudioError as e:
                print(f"ERROR: Gagal memutar audio: {e}")
            except RuntimeError as e:
                print(f"ERROR: Kesalahan saat membaca file audio: {e}")

        finally:
            # Bersihkan file sementara
            if out.exists():
                try:
                    os.remove(out)
                    #print(f"DEBUG: File sementara {out} dihapus.")
                except OSError as e:
                    print(f"WARNING: Gagal menghapus file sementara: {e}")


# === Inisialisasi model suara yang tersedia ===
jenny_tts = PiperTTS("en_GB-jenny_dioco-medium")
nathalie_tts = PiperTTS("nl_BE-nathalie-medium")


def speak_jenny(text, convert_numbers=True, audio_ready_event=None):
    processed_text = convert_text(text, lang="en") if convert_numbers else text
    jenny_tts.speak(processed_text, convert_numbers=False, audio_ready_event=audio_ready_event)


def speak_nathalie(text, convert_numbers=True, audio_ready_event=None):
    processed_text = convert_text(text, lang="id") if convert_numbers else text
    nathalie_tts.speak(processed_text, convert_numbers=False, audio_ready_event=audio_ready_event)
