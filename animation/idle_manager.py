# animation/idle_manager.py
import time
import threading
from animation.idle_anim import IdleAnimation

class IdleManager:
    def __init__(self, lcd, on_shutdown=None, check_interval=10):
        """
        Manager untuk idle animation.
        Args:
            lcd: instance PocalaDisplay
            on_shutdown: fungsi opsional untuk shutdown
            check_interval: interval pengecekan (detik)
        """
        self.lcd = lcd
        self.on_shutdown = on_shutdown
        self.check_interval = check_interval
        self._running = False
        self._thread = None
        self.idle_ticks = 0
        self.idle_anim = IdleAnimation(lcd, on_shutdown=self.on_shutdown, check_interval=self.check_interval)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        self.idle_ticks = 0
        if self.lcd:       
            self.lcd.clear()
            
    def reset(self):
        self.idle_ticks = 0
        if self.lcd:       
            self.lcd.clear()
            
    def _run(self):
        while self._running:
            time.sleep(self.check_interval)
            self.idle_ticks += 1
            self.idle_anim.run_animation(self.idle_ticks)
