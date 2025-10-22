class ChatContext:
    """
    Kelas untuk mengelola konteks percakapan antara pengguna dan asisten,
    termasuk system prompt, batas jumlah pesan, dan riwayat percakapan.
    """

    def __init__(self, system_prompt: str = None, max_messages: int = 6):
        """
        Inisialisasi konteks percakapan.

        Parameters:
            system_prompt (str, optional): Prompt sistem di awal konteks.
            max_messages (int): Jumlah maksimum pesan (user + assistant) yang disimpan.
                                Nilai minimum adalah 1.
        """
        if max_messages < 1:
            raise ValueError("max_messages harus minimal 1.")

        self.max_messages = max_messages
        self.messages = []

        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def add_message(self, role: str, message: str):
        """
        Tambahkan pesan ke konteks.

        Parameters:
            role (str): Peran pengirim pesan, harus 'user', 'assistant', atau 'system'.
            message (str): Konten pesan.
        """
        if role not in ("user", "assistant", "system"):
            raise ValueError("Role harus 'user', 'assistant', atau 'system'.")
        self.messages.append({"role": role, "content": message})
        self._trim()

    def add_user_message(self, message: str):
        """Tambahkan pesan dari pengguna ke konteks."""
        self.add_message("user", message)

    def add_assistant_message(self, message: str):
        """Tambahkan pesan dari asisten ke konteks."""
        self.add_message("assistant", message)

    def _trim(self):
        """Pangkas pesan agar jumlahnya tidak melebihi `max_messages` (system prompt tidak dihitung)."""
        system_messages = [m for m in self.messages if m["role"] == "system"]
        non_system_messages = [m for m in self.messages if m["role"] != "system"]

        if len(non_system_messages) > self.max_messages:
            non_system_messages = non_system_messages[-self.max_messages:]

        self.messages = system_messages + non_system_messages

    def get_context(self) -> list:
        """
        Ambil semua pesan dalam konteks.

        Returns:
            list: Salinan semua pesan (termasuk system prompt jika ada).
        """
        return list(self.messages)

    def clear(self, keep_system: bool = True, new_system_prompt: str = None):
        """
        Hapus riwayat percakapan.

        Parameters:
            keep_system (bool): Jika True, system prompt lama dipertahankan.
            new_system_prompt (str): Jika diberikan, mengganti system prompt lama.
        """
        if new_system_prompt:
            system_prompt_msg = [{"role": "system", "content": new_system_prompt}]
        elif keep_system:
            system_prompt_msg = [m for m in self.messages if m["role"] == "system"]
        else:
            system_prompt_msg = []

        self.messages = system_prompt_msg

    def last_user_message(self) -> str:
        """
        Ambil pesan terakhir dari pengguna.

        Returns:
            str: Konten pesan terakhir pengguna, atau None jika tidak ada.
        """
        for msg in reversed(self.messages):
            if msg["role"] == "user":
                return msg["content"]
        return None

    def last_assistant_message(self) -> str:
        """
        Ambil pesan terakhir dari asisten.

        Returns:
            str: Konten pesan terakhir asisten, atau None jika tidak ada.
        """
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return None

    def add_history(self, history: list):
        """
        Tambahkan ringkasan riwayat pertanyaan ke dalam konteks sebagai catatan sistem.

        Parameters:
            history (list): Daftar dict dengan kunci 'number' dan 'question'.
        """
        if not history:
            return

        summary = "\n".join(
            f"{item['number']}. {item['question']}" for item in history
        )
        self.add_message(
            "system",
            f"Previous questions (avoid repeating):\n{summary}"
        )
