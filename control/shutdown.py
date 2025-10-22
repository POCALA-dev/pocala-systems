# control/shutdown.py
import subprocess
import time

def shutdown_force(lcd=None, sound_file=None, delay=3):
    """
    Matikan sistem dengan membersihkan LCD dulu dan optional suara.
    
    Args:
        lcd (PocalaDisplay, optional): objek LCD untuk clear sebelum shutdown.
        sound_file (str, optional): path file audio wav untuk dimainkan sebelum shutdown.
        delay (int): waktu tunggu (detik) sebelum eksekusi shutdown.
    """
    try:
        if lcd is not None:
            lcd.display_text("Shutting down...")

        if sound_file:
            subprocess.Popen(["aplay", sound_file])
            
        time.sleep(delay)

        if lcd is not None:
            lcd.clear()
        
        time.sleep(1)
        subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)

    except subprocess.CalledProcessError:
        if lcd:
            lcd.clear()
            lcd.display_text("Shutdown failed")
        print("[ERROR] Shutdown gagal. Lakukan manual.")
