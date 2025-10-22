# POCALA (Pocket A Language)

POCALA adalah asisten percakapan portabel berbasis Raspberry Pi yang didesain untuk membantu pengguna dalam menerjemahkan, memahami kosakata, dan melakukan percakapan sederhana menggunakan sistem suara dan layar LCD. POCALA sepenuhnya berjalan secara *offline* dan ramah terhadap pengguna tunanetra.

---

## Fitur Utama

### 1. **Translator Mode**

* Menerjemahkan kalimat dua arah antara Bahasa Indonesia dan Bahasa Inggris.
* Deteksi otomatis arah terjemahan berdasarkan bahasa input atau kata kunci.
* Output ditampilkan di layar dan disuarakan dengan TTS (Text to Speech).

### 2. **Vocabulary Mode**

* Mengenali satu kata, menerjemahkannya, menampilkan fonetik, serta definisi dan contoh penggunaannya.
* Menggunakan model penerjemah MarianMT dan definisi dari model LLM lokal (Ollama/Gemma).
* Menampilkan hasil di LCD dengan dukungan scrolling dan menyuarakan hasilnya.

### 3. **Assistant Mode**

* Terdapat fungsi fungsi khusus untuk tugas tugas tertentu seperti grammar, asking, question dan speaking menggunakan LLM lokal

### 4. **LCD Output**

* Dukungan tampilan teks pendek dan panjang (scrolling).
* Warna latar dan font yang ramah visual.

### 5. **Text-to-Speech (TTS)**

* Menggunakan Piper TTS dengan model lokal bahasa Indonesia dan Inggris.
* Angka diubah menjadi kata untuk kejelasan suara indonesia

### 6. **Voice Input**

* Rekaman suara melalui tombol GPIO (pin 23).
* Pemrosesan audio dengan `whisper.cpp` untuk transkripsi offline.

## Setup & Instalasi

### Perangkat Keras

* Raspberry Pi 5 atau setara
* Tombol fisik terhubung ke GPIO pin 23
* Layar LCD ST7789 240x240
* Speaker audio dan mikrofon

### Dependensi

```bash
pip install sounddevice scipy gpiozero numpy transformers torch soundfile
dan dependensi lainnya
```

Model yang digunakan
```bash
Whisper.cpp, MarianMT (OpusMT Model id-en dan en-id), Piper-TTS (Jenny Dioco dan Jennifer), ollama (Gemma3:1b)
```

---

## Penggunaan

Jalankan program utama:

```bash
python main.py
```

Setelah dijalankan:

* Pilih mode dengan suara: "Translator", "Vocabulary", atau "Assistant"
* Ikuti instruksi suara dan tampilan
* Tekan tombol untuk berbicara

---

## Catatan Tambahan

* Seluruh sistem berjalan **offline**, cocok untuk daerah tanpa akses internet.
* Desain modular: setiap mode dapat dikembangkan secara terpisah.
* Kompatibel dengan pengguna tunanetra dengan integrasi suara dan LCD.

---

## Kredit

Proyek ini dikembangkan sebagai bagian dari eksplorasi *AI asisten edukatif* dan *penerjemah suara lokal* oleh Muhammad Ricky Rizaldi dan tim pengembang.

---

## Lisensi

POCALA menggunakan berbagai pustaka open-source. Lihat masing-masing folder model dan repositori pustaka terkait untuk detail lisensi.
