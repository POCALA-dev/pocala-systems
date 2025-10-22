# control/reset.py
TRIGGER_FILE = "/tmp/pocala_restart_trigger"

def reset_control():
    """Tombol reset membuat trigger file untuk merestart main service."""
    try:
        with open(TRIGGER_FILE, "w") as f:
            f.write("restart\n")
        print("[INFO] Trigger file dibuat. Restart main.py akan dilakukan oleh watcher.")
    except Exception as e:
        print(f"[ERROR] Gagal membuat trigger file: {e}")
