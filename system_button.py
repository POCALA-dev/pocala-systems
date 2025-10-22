# system_button.py
import time
import threading
from signal import pause
from gpiozero import Button
from control.volume_control import increase_volume, decrease_volume, get_current_volume
from control.reset import reset_control

# Konfigurasi GPIO
BUTTON_VOL_UP_PIN = 17
BUTTON_VOL_DOWN_PIN = 27
BUTTON_RESET_PIN = 24

button_vol_up = Button(BUTTON_VOL_UP_PIN, pull_up=False, bounce_time=0.15)
button_vol_down = Button(BUTTON_VOL_DOWN_PIN, pull_up=False, bounce_time=0.15)
button_reset = Button(BUTTON_RESET_PIN, pull_up=False, bounce_time=0.15)

# Konstanta
LONG_PRESS_TIME = 5  # detik
SHUTDOWN_FLAG = "/tmp/pocala_shutdown.flag"

# Global flag
shutdown_triggered = False

# Handler Volume
def button_vol_up_pressed():
    increase_volume()
    vol = get_current_volume()
    print(f"[INFO] Volume naik -> {vol}%")

def button_vol_down_pressed():
    decrease_volume()
    vol = get_current_volume()
    print(f"[INFO] Volume turun -> {vol}%")

# Handler Reset Short Press
def handle_reset_short_press():
    """Short press tombol reset = restart POCALA"""
    global shutdown_triggered
    if shutdown_triggered:
        # Kalau sudah long press → jangan eksekusi short press
        return
    print("[INFO] Short press detected → restart via reset_control()")
    reset_control()

# Monitor Reset Long Press
def monitor_long_press():
    """Long press tombol reset = request shutdown ke pocala_main"""
    global shutdown_triggered
    while True:
        if button_reset.is_pressed and not shutdown_triggered:
            press_start = time.time()
            while button_reset.is_pressed:
                elapsed = time.time() - press_start
                if elapsed >= LONG_PRESS_TIME:
                    shutdown_triggered = True
                    print("[INFO] Long press detected → request shutdown...")

                    # tulis flag shutdown untuk pocala_main
                    try:
                        with open(SHUTDOWN_FLAG, "w") as f:
                            f.write("shutdown")
                        print(f"[INFO] Shutdown flag ditulis di {SHUTDOWN_FLAG}")
                    except Exception as e:
                        print(f"[ERROR] Gagal menulis shutdown flag: {e}")
                    return  # keluar thread setelah sinyal
                time.sleep(0.1)
        time.sleep(0.1)

# Setup tombol
def setup_button_functions():
    button_vol_up.when_pressed = button_vol_up_pressed
    button_vol_down.when_pressed = button_vol_down_pressed
    button_reset.when_released = handle_reset_short_press

    # Jalankan thread monitoring long press
    threading.Thread(target=monitor_long_press, daemon=True).start()

# Main Loop
def main():
    print("[INFO] Kontrol volume & reset aktif. Menunggu input tombol...")
    setup_button_functions()
    pause()  # tunggu event tombol tanpa beban CPU

if __name__ == "__main__":
    main()

