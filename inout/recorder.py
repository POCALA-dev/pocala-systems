from utils.path_helper import get_resource_path
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from gpiozero import Button
import time

# GLOBAL BUTTON
REC_BUTTON_PIN = 23
button = Button(REC_BUTTON_PIN, pull_up=True)


class AudioRecorder:
    """
    Class untuk merekam audio menggunakan tombol fisik.
    Rekaman dimulai saat tombol ditekan dan berhenti saat dilepas.
    """

    def __init__(self, filename="audio.wav", samplerate=16000, lcd=None):
        # Simpan file di folder audio/ root project
        self.filename = get_resource_path(filename)
        self.samplerate = samplerate
        self.lcd = lcd
        self.audio = []
        # Tidak bikin Button lagi, pakai global `button`

    def run(self):
        """Loop utama untuk merekam audio berkali-kali dengan menekan tombol."""
        try:
            while True:
                if not button.is_pressed:
                    print("INFO: TOMBOL DITEKAN - Mulai merekam...")

                    if self.lcd:
                        self.lcd.clear()
                        self.lcd.display_text("Merekam...")

                    self.audio.clear()

                    with sd.InputStream(samplerate=self.samplerate, channels=1, dtype='int16') as stream:
                        while not button.is_pressed:
                            frame, _ = stream.read(1024)
                            self.audio.append(frame)

                    print("INFO: TOMBOL DILEPAS - Rekaman berhenti.")

                    if not self.audio:
                        print("WARNING: Tidak ada audio yang direkam.")
                        if self.lcd:
                            self.lcd.flash_message("Tidak ada audio.\nCoba rekam ulang.", duration=2)
                        continue

                    if self.lcd:
                        self.lcd.flash_message("Rekaman selesai.", duration=1.5)

                    self.save_audio()
                    print("INFO: Siap untuk rekaman berikutnya...")

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("INFO: Proses dihentikan oleh pengguna.")

    def save_audio(self):
        """Gabungkan dan simpan audio hasil rekaman ke file WAV."""
        audio_np = np.concatenate(self.audio, axis=0)
        max_val = np.max(np.abs(audio_np))
        if max_val > 0:
            audio_np = (audio_np * (32767 / max_val)).astype(np.int16)

        wav.write(self.filename, self.samplerate, audio_np)
        print(f"INFO: Rekaman disimpan sebagai: {self.filename}")


# Fungsi sekali rekam dengan path audio konsisten
def record_once(filename="audio.wav", samplerate=16000, lcd=None):
    audio_path = get_resource_path(filename)

    # Tunggu tombol dilepas dulu (biar gak langsung nyangkut)
    while button.is_pressed:
        time.sleep(0.05)

    print("INFO: TOMBOL DITEKAN - Mulai merekam...")
    if lcd:
        lcd.clear()
        lcd.display_text("Merekam...")

    audio = []
    with sd.InputStream(samplerate=samplerate, channels=1, dtype='int16') as stream:
        while not button.is_pressed:
            frame, _ = stream.read(1024)
            audio.append(frame)

    print("INFO: TOMBOL DILEPAS - Rekaman berhenti.")
    if not audio:
        print("WARNING: Tidak ada audio.")
        if lcd:
            lcd.flash_message("Tidak ada audio.\nCoba rekam ulang.", duration=2)
        return None

    if lcd:
        lcd.flash_message("Rekaman selesai.", duration=1.5)

    audio_np = np.concatenate(audio, axis=0)
    max_val = np.max(np.abs(audio_np))
    if max_val > 0:
        audio_np = (audio_np * (32767 / max_val)).astype(np.int16)

    wav.write(audio_path, samplerate, audio_np)
    print(f"INFO: Rekaman disimpan sebagai: {audio_path}")
    return audio_path
