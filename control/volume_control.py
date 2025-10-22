# volume_control.py
import subprocess

# Fungsi untuk mendapatkan volume saat ini
def get_current_volume():
    """Mengambil volume saat ini sebagai persen (int)"""
    try:
        result = subprocess.run(
            ['amixer', 'get', 'Master'],
            capture_output=True, text=True
        )

        for line in result.stdout.splitlines():
            if '%' in line:
                start = line.find('[') + 1
                end = line.find('%')
                volume_str = line[start:end]
                if volume_str.isdigit():
                    return int(volume_str)
        return 50  # fallback default
    except Exception as e:
        print(f"[ERROR] Gagal mendapatkan volume: {e}")
        return 50

# Fungsi untuk mengatur volume ke persentase tertentu
def set_volume(volume_percent):
    """Set volume ke persentase tertentu"""
    volume_percent = max(0, min(100, volume_percent))  # Pastikan volume dalam rentang 0-100
    try:
        subprocess.run(
            ['amixer', 'set', 'Master', f'{volume_percent}%'],
            check=True
        )
        print(f"[INFO] Volume diatur ke {volume_percent}%")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Gagal mengatur volume: {e}")
        return False

# Fungsi untuk meningkatkan volume sebesar 5%
def increase_volume():
    """Menaikkan volume sebesar 5%"""
    current = get_current_volume()
    new_volume = min(100, current + 5)

    print(f"[INFO] Volume sekarang: {current}%, ingin naik ke {new_volume}%")

    if new_volume == current:
        print("[INFO] Volume sudah maksimal.")
    else:
        set_volume(new_volume)

# Fungsi untuk menurunkan volume sebesar 5%
def decrease_volume():
    """Menurunkan volume sebesar 5%"""
    current = get_current_volume()
    new_volume = max(0, current - 5)

    print(f"[INFO] Volume sekarang: {current}%, ingin turun ke {new_volume}%")

    if new_volume == current:
        print("[INFO] Volume sudah minimal.")
    else:
        set_volume(new_volume)

