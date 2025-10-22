import os
import subprocess
import time
from control.volume_control import get_current_volume
from inout.piper_output import speak_and_display


def get_cpu_temp() -> str:
    """Ambil suhu CPU Raspberry Pi"""
    try:
        out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return out.replace("temp=", "").strip()
    except Exception:
        return "Unknown"


def get_ip_address() -> str:
    """Ambil IP address khusus interface wlan0"""
    try:
        out = subprocess.check_output(
            ["hostname", "-I"]
        ).decode().strip().split()
        # hostname -I bisa return banyak IP → pilih IPv4 wlan0
        for ip in out:
            if "." in ip:  # IPv4
                return ip
        return "Not connected"
    except Exception:
        return "Unknown"


def get_wifi_ssid() -> str:
    """Ambil SSID WiFi aktif pakai nmcli"""
    try:
        out = subprocess.check_output(
            ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"]
        ).decode().strip()

        for line in out.splitlines():
            if line.startswith("yes:"):
                return line.split(":", 1)[1]
        return "Not connected"
    except Exception:
        return "Unknown"


def get_bluetooth_devices() -> str:
    """Ambil daftar perangkat bluetooth yang terhubung"""
    try:
        out = subprocess.check_output(["bluetoothctl", "info"]).decode().lower()
        devices = []
        for line in out.splitlines():
            if line.strip().startswith("name:"):
                devices.append(line.split(":", 1)[1].strip())
        return ", ".join(devices) if devices else "No device connected"
    except Exception:
        return "Unknown"


def show_status(lcd=None):
    volume = get_current_volume()
    temp = get_cpu_temp()
    wifi = get_wifi_ssid()
    ip = get_ip_address()
    bt_devices = get_bluetooth_devices()

    # LCD tampil full info
    if lcd:
        lcd_text = (
            f"WiFi: {wifi}    \n"
            f"Volume: {volume}%     \n"
            f"IP: {ip}\n"
            f"BT: {bt_devices}\n"
        )
        lcd.display_text(lcd_text)

    # Audio ringkas
    spoken_text = (
        f"WiFi connected to {wifi} and. "
        f"the volume is {volume} percent. "
    )
    speak_and_display(spoken_text, lang="en", lcd=None)
    
    time.sleep(3)
    if lcd:
        lcd.clear()

