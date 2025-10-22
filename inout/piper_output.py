import threading
from inout.piper_tts import speak_jenny, speak_nathalie


def speak_and_display(text, lang="id", mode="short", clear_after=False,
                      lcd=None, scroll_speed=0.08):
    """
    Menyuarakan teks dan menampilkannya ke LCD secara sinkron.
    """
    if not text:
        return

    audio_ready_event = threading.Event()
    tts_func = speak_nathalie if lang == "id" else speak_jenny

    tts_thread = threading.Thread(
        target=tts_func,
        args=(text,),
        kwargs={'audio_ready_event': audio_ready_event}
    )
    tts_thread.start()

    if lcd:
        print("[INFO] Menunggu sinyal audio siap dari TTS...")
        audio_ready_event.wait()
        print("[INFO] Sinyal diterima! Menampilkan ke LCD.")

        if mode == "scroll":
            lcd.scroll_text(text, speed=scroll_speed)
        else:
            lcd.display_text(text)

    tts_thread.join()

    if clear_after and lcd:
        lcd.clear()
