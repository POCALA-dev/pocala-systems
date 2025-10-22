import socket
import subprocess
import time
import threading
import os
from inout.recorder import record_once
from inout.piper_output import speak_and_display
from inout.whisper_transcriber import transcribe_auto
from inout.display import PocalaDisplay
from utils.response_check import is_yes, is_no, is_repeat, is_help, is_status
from utils.response_menu import is_online, is_offline, is_learning_audio
from utils.path_helper import get_resource_path
from animation.idle_manager import IdleManager
from control.shutdown import shutdown_force

SHUTDOWN_FLAG = "/tmp/pocala_shutdown.flag"

def cek_koneksi_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def safe_transcribe(audio, lcd=None):
    try:
        return (transcribe_auto(audio, lcd=lcd) or "").lower()
    except Exception as e:
        print(f"[TRANSCRIBE ERROR] {e}")
        return ""


def monitor_shutdown_signal(lcd, idle_manager=None):
    """Thread untuk memonitor shutdown flag dari system_button"""
    while True:
        if os.path.exists(SHUTDOWN_FLAG):
            print("[INFO] Shutdown signal received from system_button.")
            os.remove(SHUTDOWN_FLAG)

            # Stop animasi idle dulu biar layar clear
            if idle_manager is not None:
                idle_manager.stop()
            if lcd:
                lcd.clear()

            # lakukan shutdown dengan LCD
            shutdown_force(
                lcd=lcd,
                sound_file="/home/pocala/main/resource/Shutdown_force.wav",
                delay=3
            )
            break
        time.sleep(1)


def main(lcd=None):
    # Inisialisasi idle manager
    idle_manager = IdleManager(
        lcd=lcd,
        on_shutdown=lambda: subprocess.run(["sudo", "shutdown", "-h", "now"]),
        check_interval=5
    )
    idle_manager.start()
    
    # jalankan thread monitor shutdown di background
    threading.Thread(
        target=monitor_shutdown_signal,
        args=(lcd, idle_manager),
        daemon=True
    ).start()

    # Tampilkan gambar
    image_path = get_resource_path("resource", "pocala.jpg")
    lcd.display_image(image_path)
    speak_and_display("Welcome to POCALA Assistant!", lang="en", lcd=None)
    
    while True:
        internet = cek_koneksi_internet()
        if internet:
            speak_and_display("Internet is available.", lang="en", lcd=lcd)
        else:
            speak_and_display("No Internet Connection.", lang="en", lcd=lcd)

        # === Pertanyaan menu utama ===
        speak_and_display(
            "What do you want to use? You can say online, offline, learning audio, help, or status.",
            lang="en", lcd=lcd
        )

        while True:
            audio = record_once(filename="ask_menu.wav", lcd=lcd)
            if audio is None:
                idle_manager.reset()
                speak_and_display("No audio detected. Please try again.", lang="en", lcd=lcd)
                continue

            jawaban = safe_transcribe(audio, lcd=lcd)
            idle_manager.reset()
            print(f"[MENU USER] {jawaban}")

            if is_repeat(jawaban):
                speak_and_display(
                    "Please choose: online, offline, learning audio, help, or status.",
                    lang="en", lcd=lcd
                )
                continue

            if is_help(jawaban):
                idle_manager.stop()
                from help.help import help_mode
                help_mode(lcd=lcd)
                speak_and_display(
                    "Welcome back! You can continue to choose online, offline, learning audio, help, or status",
                    lang="en", lcd=lcd)
                idle_manager.start()
                continue

            if is_status(jawaban):
                idle_manager.stop()
                from status.show_stats import show_status
                show_status(lcd=lcd)
                speak_and_display(
                    "Welcome back! You can continue to choose online, offline, learning audio, help, or status",
                    lang="en", lcd=lcd)
                idle_manager.start()
                continue

            if is_learning_audio(jawaban):
                idle_manager.stop()
                from learning_audio.play_audio import learning_audio_mode
                learning_audio_mode(lcd=lcd)
                idle_manager.start()
                break

            if is_online(jawaban):
                if not internet:
                    speak_and_display(
                        "Internet not available. You can only access offline, learning audio, help, and status.",
                        lang="en", lcd=lcd
                    )
                    continue
                idle_manager.stop()
                speak_and_display("Entering Online Mode...", lang="en", lcd=lcd)
                from online.main_online import online_mode
                online_mode(lcd=lcd)
                idle_manager.start()
                break

            if is_offline(jawaban):
                idle_manager.stop()
                speak_and_display("Entering Offline Mode...", lang="en", lcd=lcd)
                from offline.main_offline import offline_mode
                offline_mode(lcd=lcd)
                idle_manager.start()
                break

            # fallback jika tidak dikenali
            speak_and_display(
                "I didn't understand. Please try again",
                lang="en", lcd=lcd
            )

        # === Tanya kembali ke menu utama ===
        question_text = "Welcome back to main menu. Do you want to start again?"
        speak_and_display(question_text, lang="en", lcd=lcd)

        while True:
            audio = record_once(filename="ask_return_main.wav", lcd=lcd)
            if audio is None:
                idle_manager.reset()
                speak_and_display(
                    "No audio detected. Please try again.",
                    lang="en", lcd=lcd
                )
                continue

            reply = safe_transcribe(audio, lcd=lcd)
            idle_manager.reset()
            print(f"[JAWABAN ULANG] {reply}")

            if is_repeat(reply):
                speak_and_display(question_text, lang="en", lcd=lcd)
                continue

            if is_help(reply):
                idle_manager.stop()
                from help.help import help_mode
                help_mode(lcd=lcd)
                idle_manager.start()
                break

            if is_yes(reply):
                idle_manager.reset()
                break
            elif is_no(reply):
                speak_and_display("Shutting down. Goodbye!", lang="en", lcd=lcd)
                lcd.clear()
                time.sleep(5)
                try:
                    subprocess.run(
                        ["sudo", "shutdown", "-h", "now"],
                        check=True
                    )
                except subprocess.CalledProcessError:
                    speak_and_display(
                        "Shutdown failed. Please do it manually.",
                        lang="en", lcd=lcd
                    )
                return
            else:
                speak_and_display("Please say yes or no.", lang="en", lcd=lcd)


if __name__ == "__main__":
    lcd = PocalaDisplay()
    lcd.clear()
    main(lcd=lcd)
