# animation/idle_anim.py
import time
import random
from animation.eye_anims import EyeAnimator
from inout.piper_output import speak_and_display

class IdleAnimation:
    def __init__(self, lcd, on_shutdown=None, check_interval=10):
        """
        Idle animation & voice reminders for POCALA.
        Args:
            lcd: Instance PocalaDisplay
            on_shutdown: optional shutdown callback
            check_interval: interval pengecekan (detik), default 10
        """
        self.lcd = lcd
        self.eye = EyeAnimator(lcd)
        self.on_shutdown = on_shutdown
        self.check_interval = check_interval

        # idle messages for minutes 1–5
        self.idle_messages = {
            1: "It has been one minute. Are you still there?",
            2: "Two minutes of silence. I'm still waiting.",
            3: "Three minutes have passed... maybe you're busy?",
            4: "Four minutes have passed. Did you forget me?",
            5: "Five minutes waiting... I'm getting sleepy.",
        }

    def run_animation(self, elapsed_ticks: int):
        """
        Run idle animations every tick (e.g. 10s), and voice every full minute.
        Args:
            elapsed_ticks: number of ticks idle (1 tick = check_interval seconds)
        """
        # Konversi tick → menit
        elapsed_minutes = (elapsed_ticks * self.check_interval) // 60

        # Animasi hanya jalan setelah idle >= 1 menit
        if elapsed_minutes >= 1:
            anims = [
                self.eye.blink,
                self.eye.random_saccade,
                self.eye.happy_eye,
                self.eye.sleep_then_wakeup
            ]
            weights = [4, 2, 2, 2]
            random.choices(anims, weights=weights, k=1)[0]()   # jalankan animasi tiap tick

        # Voice hanya kalau pas ganti menit (1–5 menit)
        if 1 <= elapsed_minutes <= 5 and elapsed_ticks % (60 // self.check_interval) == 0:
            message = self.idle_messages.get(elapsed_minutes)
            if message:
                speak_and_display(message, lang="en", lcd=None)
            return

        # Shutdown di menit ke-6
        if elapsed_minutes >= 6 and elapsed_ticks % (60 // self.check_interval) == 0:
            self.shutdown_animation()
            return

    def shutdown_animation(self):
        """Final animation before shutdown."""
        self.eye.happy_eye()
        speak_and_display(
            "It seems I'm not being used. Goodbye.",
            lang="en",
            lcd=None
        )
        self.eye.sleep()
        self.lcd.clear()
        time.sleep(3)
        if self.on_shutdown:
            self.on_shutdown()
