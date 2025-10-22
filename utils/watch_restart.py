# watch_restart.py
import os
import time
import subprocess

TRIGGER_FILE = "/tmp/pocala_restart_trigger"

while True:
    if os.path.exists(TRIGGER_FILE):
        print("[INFO] Trigger file terdeteksi. Merestart pocala_main.service...")
        try:
            subprocess.run([
                "systemctl", "--user", "restart", "pocala_main.service"
            ], check=True)
        except Exception as e:
            print(f"[ERROR] Gagal restart service: {e}")
        finally:
            os.remove(TRIGGER_FILE)
    time.sleep(1)
