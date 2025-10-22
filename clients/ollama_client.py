import requests
import time

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434", model="gemma3:1b"):
        """
        Inisialisasi klien Ollama.
        
        Parameters:
        - base_url: URL dasar API Ollama.
        - model: Nama model default yang akan digunakan.
        """
        self.base_url = base_url
        self.model = model

    def generate(self, prompt, stream=False):
        """
        Mengirim prompt satu arah ke endpoint /api/generate.

        Parameters:
        - prompt: Teks perintah.
        - stream: Jika True, hasil dikembalikan dalam bentuk stream (tidak digunakan di sini).

        Returns:
        - Respons teks (string) dari model.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": stream
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal generate dari Ollama: {e}")
            return ""

    def chat(self, prompt_or_context, context=None, stream=False, max_retries=3, timeout=60):
        """
        Mengirim percakapan ke endpoint /api/chat dengan retry dan logging waktu respons.

        Bisa dipanggil dalam dua mode:
        1. prompt_or_context = string prompt, context = ChatContext → akan ditambahkan ke riwayat.
        2. prompt_or_context = list of dicts (pesan manual) → tanpa manipulasi konteks.

        Parameters:
        - max_retries: jumlah percobaan ulang jika timeout
        - timeout: batas waktu per request (detik)

        Returns:
        - Hasil balasan dari asisten dalam bentuk teks.
        """
        if isinstance(prompt_or_context, str) and context is not None:
            # Mode 1: prompt string + objek ChatContext
            context.add_user_message(prompt_or_context)
            messages = context.get_context()
        elif isinstance(prompt_or_context, list):
            # Mode 2: langsung kirim list pesan tanpa objek context
            messages = prompt_or_context
        else:
            raise ValueError(
                "chat() membutuhkan prompt string + context, atau list of messages."
            )

        attempt = 1
        while attempt <= max_retries:
            try:
                print(f"[INFO] Mengirim ke Ollama (percobaan {attempt}/{max_retries})...")
                start_time = time.time()

                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": stream
                    },
                    timeout=timeout
                )
                response.raise_for_status()

                elapsed = time.time() - start_time
                print(f"[INFO] Respons diterima dalam {elapsed:.2f} detik.")

                data = response.json()
                return data.get("message", {}).get("content", "")

            except requests.exceptions.ReadTimeout:
                print(f"[WARNING] Timeout setelah {timeout} detik. Mencoba ulang...")
            except requests.exceptions.ConnectionError:
                print("[ERROR] Ollama Offline: Server tidak dapat dihubungi.")
                return ""
            except Exception as e:
                print(f"[ERROR] Gagal chat ke Ollama: {e}")
                return ""

            attempt += 1
            time.sleep(1)  # jeda sebelum retry

        return "[Gagal] Tidak ada respons setelah beberapa percobaan."

    def list_models(self):
        """
        Mengambil daftar model yang tersedia di server Ollama.

        Returns:
        - List nama model (string) atau [] jika gagal.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return [
                model["name"]
                for model in response.json().get("models", [])
            ]
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Tidak bisa ambil daftar model: {e}")
            return []

    def is_server_ready(self):
        """
        Mengecek apakah server Ollama berjalan dan siap dipakai.

        Returns:
        - True jika server merespon dengan 200 OK.
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
