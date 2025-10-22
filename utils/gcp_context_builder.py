# Mengelola riwayat percakapan untuk Gemini API dengan system prompt yang opsional.

class GcpChatContext:
    """
    Mengelola riwayat percakapan dalam format yang sesuai untuk Gemini API.
    Mirip dengan ChatContext di Ollama, tapi menyesuaikan struktur Gemini.
    """

    def __init__(self, system_prompt=None, max_messages=8):
        if system_prompt and not isinstance(system_prompt, str):
            raise TypeError("Jika diberikan, system_prompt harus berupa string.")

        self.system_prompt = system_prompt
        self.max_messages = max_messages
        self.messages = []
        self._system_prompt_sent = False

    def add_message(self, role, message):
        """
        Tambahkan pesan ke riwayat.
        role: "user", "model", atau "system" (system akan dikirim sebagai user prompt awal).
        """
        if role not in ("user", "model", "system"):
            raise ValueError("Role harus 'user', 'model', atau 'system'.")

        if role == "system":
            # Gemini tidak punya role system, jadi kita treat sebagai user pertama
            self.system_prompt = message
            self._system_prompt_sent = False
        else:
            self.messages.append({"role": role, "parts": [{"text": message}]})
            self._trim()

    def add_user_message(self, message):
        self.add_message("user", message)

    def add_assistant_message(self, message):
        self.add_message("model", message)

    def _trim(self):
        """Pangkas riwayat agar tidak melebihi max_messages (system prompt tidak dihitung)."""
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self):
        """
        Ambil riwayat percakapan untuk dikirim ke Gemini API.
        Jika system_prompt ada & belum dikirim, tambahkan di awal.
        """
        if self.system_prompt and not self._system_prompt_sent:
            context_with_system = [{
                "role": "user",
                "parts": [{"text": self.system_prompt}]
            }]
            context_with_system.extend(self.messages)
            return context_with_system
        return list(self.messages)

    def mark_system_prompt_sent(self):
        if self.system_prompt:
            self._system_prompt_sent = True

    def clear(self, keep_system=True, new_system_prompt=None):
        """
        Hapus riwayat percakapan.
        keep_system: kalau True, pertahankan system prompt lama.
        new_system_prompt: kalau diisi, ganti system prompt lama.
        """
        if new_system_prompt:
            self.system_prompt = new_system_prompt
            self._system_prompt_sent = False
        elif keep_system:
            self._system_prompt_sent = False
        else:
            self.system_prompt = None
            self._system_prompt_sent = False
        self.messages = []

    def last_user_message(self):
        """Ambil pesan terakhir dari user."""
        for msg in reversed(self.messages):
            if msg["role"] == "user":
                return msg["parts"][0]["text"]
        return None

    def last_assistant_message(self):
        """Ambil pesan terakhir dari asisten (model)."""
        for msg in reversed(self.messages):
            if msg["role"] == "model":
                return msg["parts"][0]["text"]
        return None

    def add_history(self, history):
        """
        Tambahkan ringkasan soal lama sebagai system note (format Gemini: role=user).
        history: list of dict (number, question).
        """
        if not history:
            return
        summary = "\n".join(
            [f"{item['number']}. {item['question']}" for item in history]
        )
        self.add_message("user", f"Previous questions (avoid repeating):\n{summary}")
