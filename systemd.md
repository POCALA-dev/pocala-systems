# POCALA System Service Documentation

Dokumentasi untuk menjalankan **System Button Controller**, **Watcher Service**, dan **POCALA Main Service** menggunakan systemd service pada user `pocala`. Semua output script tersimpan ke file log.

---

## **1. Cek lokasi Python3**

```bash
which python3
```

Biasanya hasilnya `/usr/bin/python3`. Catat path ini.

---

## **2. Buat folder log**

```bash
mkdir -p /home/pocala/logs
```

---

## **3. System Button Service**

### **3.1 Buat/ubah service file**

```bash
nano ~/.config/systemd/user/system_button.service
```

Isi:

```ini
[Unit]
Description=POCALA System Button Controller
After=default.target

[Service]
ExecStart=/usr/bin/python3 -u /home/pocala/main/system_button.py
WorkingDirectory=/home/pocala/main
Restart=always
RestartSec=3

StandardOutput=append:/home/pocala/logs/system_button.log
StandardError=append:/home/pocala/logs/system_button.log

[Install]
WantedBy=default.target
```

**Catatan**:

* `-u` → output Python unbuffered, log tampil realtime.
* Gunakan path absolut (`/home/pocala/...`), jangan `~`.

### **3.2 Reload daemon & enable service**

```bash
systemctl --user daemon-reload
systemctl --user enable system_button.service
```

### **3.3 Start manual untuk tes**

```bash
systemctl --user start system_button.service
```

### **3.4 Cek log**

Realtime:

```bash
tail -f /home/pocala/logs/system_button.log
```

Stop dengan Ctrl+C.

Status:

```bash
systemctl --user status system_button.service
```

### **3.5 Rotasi log (opsional)**

```bash
sudo nano /etc/logrotate.d/system_button
```

Isi:

```
/home/pocala/logs/system_button.log {
    size 1M
    rotate 7
    compress
    missingok
    notifempty
    copytruncate
    su pocala pocala
}
```

### **3.6 Autostart setelah boot**

```bash
sudo loginctl enable-linger pocala
```

Service user akan aktif setiap kali Raspberry Pi boot, meski tidak login shell.

---

## **4. Watcher Service (Reset-Safe)**

### **4.1 Buat service file**

```bash
nano ~/.config/systemd/user/pocala_watcher.service
```

Isi:

```ini
[Unit]
Description=POCALA Watcher Service untuk Reset
After=default.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -u /home/pocala/main/utils/watch_restart.py
WorkingDirectory=/home/pocala/main/utils
Restart=always
RestartSec=3

StandardOutput=append:/home/pocala/logs/watcher.log
StandardError=append:/home/pocala/logs/watcher.log

[Install]
WantedBy=default.target
```

### **4.2 Enable & start**

```bash
systemctl --user daemon-reload
systemctl --user enable pocala_watcher.service
systemctl --user start pocala_watcher.service
```

**Catatan**:

* Watcher service memonitor file trigger `/tmp/pocala_restart_trigger`.
* Tombol reset menulis trigger file → Watcher melakukan restart main service.
* Memisahkan restart dari service button → aman, tidak hang.

---

## **5. POCALA Main Service**

### **5.1 Buat service file**

```bash
nano ~/.config/systemd/user/pocala_main.service
```

Isi:

```ini
[Unit]
Description=POCALA Main Service
After=default.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -u /home/pocala/main/pocala_main.py
WorkingDirectory=/home/pocala/main
Restart=on-failure
RestartSec=3

Environment="PATH=/home/pocala/.local/bin:/usr/bin:/bin"
Environment=DISPLAY=:0

StandardOutput=append:/home/pocala/logs/pocala_main.log
StandardError=append:/home/pocala/logs/pocala_main.log

[Install]
WantedBy=default.target
```

### **5.2 Enable & start**

```bash
systemctl --user daemon-reload
systemctl --user enable pocala_main.service
systemctl --user start pocala_main.service
```

**Catatan**:

* `Restart=on-failure` → service restart hanya jika crash, tidak terganggu tombol reset.
* Semua TTS, Whisper, Ollama, dan LCD dijalankan normal.

---

## **6. Lokasi log akhir**

* System Button: `/home/pocala/logs/system_button.log`
* Watcher Service: `/home/pocala/logs/watcher.log`
* Main Service: `/home/pocala/logs/pocala_main.log`

Berikut versi README yang rapi dan mudah dipahami untuk panduan mengelola service POCALA:

---

# Mengelola Service POCALA

Saat melakukan pengembangan atau debugging POCALA, terkadang perlu mematikan sementara service agar tidak terjadi tabrakan. Berikut panduannya.

## 1. Mematikan Service Sementara

Gunakan perintah `systemctl --user stop` untuk menghentikan masing-masing service:

```bash
# Stop Service
systemctl --user stop system_button.service
systemctl --user stop pocala_watcher.service
systemctl --user stop pocala_main.service
```

### Mengecek Status Service

Untuk memastikan service sudah berhenti:

```bash
systemctl --user status system_button.service
systemctl --user status pocala_watcher.service
systemctl --user status pocala_main.service
```

## 2. Menonaktifkan Autostart Sementara

Agar service tidak otomatis berjalan saat reboot atau di-enable, gunakan:

```bash
systemctl --user disable system_button.service
systemctl --user disable pocala_watcher.service
systemctl --user disable pocala_main.service
```

## 3. Mengaktifkan Kembali Service

Setelah selesai ngoding atau debugging, aktifkan dan jalankan kembali service dengan perintah:

```bash
# Enable autostart
systemctl --user enable system_button.service
systemctl --user enable pocala_watcher.service
systemctl --user enable pocala_main.service

# Start service
systemctl --user start system_button.service
systemctl --user start pocala_watcher.service
systemctl --user start pocala_main.service
```
