import time
import random
from PIL import Image, ImageDraw
from utils.draw_utils import draw_round_rect


class EyeAnimator:
    def __init__(self, lcd,
                 ref_eye_width=80,
                 ref_eye_height=80,
                 ref_space_between_eye=30,
                 ref_corner_radius=20,
                 eye_color=(135, 206, 235)):

        self.lcd = lcd
        self.ref_eye_width = ref_eye_width
        self.ref_eye_height = ref_eye_height
        self.ref_space_between_eye = ref_space_between_eye
        self.ref_corner_radius = ref_corner_radius
        self.eye_color = eye_color

        # posisi default (tengah layar) → anchor: left_eye
        cx, cy = self.lcd.width // 2, self.lcd.height // 2
        self.left_eye_x = cx - (ref_eye_width // 2 + ref_space_between_eye // 2)
        self.left_eye_y = cy

        # mata kanan selalu mengikuti kiri
        self.right_eye_x = self.left_eye_x + ref_eye_width + ref_space_between_eye
        self.right_eye_y = self.left_eye_y

        # dimensi
        self.left_eye_width = self.right_eye_width = ref_eye_width
        self.left_eye_height = self.right_eye_height = ref_eye_height

    # Utility
    def _sync_right_eye(self):
        """Pastikan mata kanan selalu sejajar dengan kiri dengan jarak tetap."""
        self.right_eye_x = self.left_eye_x + self.ref_eye_width + self.ref_space_between_eye
        self.right_eye_y = self.left_eye_y

    def _clamp_position(self):
        """Pastikan mata tidak keluar layar."""
        min_x = self.ref_eye_width // 2
        max_x = self.lcd.width - (self.ref_eye_width // 2 + self.ref_eye_width + self.ref_space_between_eye)
        min_y = self.ref_eye_height // 2
        max_y = self.lcd.height - self.ref_eye_height // 2

        # clamp left eye only
        self.left_eye_x = max(min_x, min(self.left_eye_x, max_x))
        self.left_eye_y = max(min_y, min(self.left_eye_y, max_y))

        # right eye ikut
        self._sync_right_eye()

    def _draw_base_eyes(self, draw: ImageDraw.Draw):
        """Gambar mata kiri & kanan (tanpa pupil)."""
        # kiri
        lx, ly = int(self.left_eye_x - self.left_eye_width / 2), int(self.left_eye_y - self.left_eye_height / 2)
        rx, by = int(self.left_eye_x + self.left_eye_width / 2), int(self.left_eye_y + self.left_eye_height / 2)
        draw_round_rect(draw, lx, ly, rx, by, self.ref_corner_radius, fill=self.eye_color)

        # kanan
        lx2, ly2 = int(self.right_eye_x - self.right_eye_width / 2), int(self.right_eye_y - self.right_eye_height / 2)
        rx2, by2 = int(self.right_eye_x + self.right_eye_width / 2), int(self.right_eye_y + self.right_eye_height / 2)
        draw_round_rect(draw, lx2, ly2, rx2, by2, self.ref_corner_radius, fill=self.eye_color)

    def draw_eyes(self, update=True):
        img = Image.new("RGB", (self.lcd.width, self.lcd.height), self.lcd.bg_color)
        self._draw_base_eyes(ImageDraw.Draw(img))
        if update:
            self.lcd.disp.display(img)

    # Animations
    def blink(self, duration=0.2):
        orig_h = self.left_eye_height
        for h in range(orig_h, 0, -10):
            self.left_eye_height = self.right_eye_height = h
            self.draw_eyes(); time.sleep(0.02)
        time.sleep(duration)
        for h in range(0, orig_h + 1, 10):
            self.left_eye_height = self.right_eye_height = h
            self.draw_eyes(); time.sleep(0.02)
        self.left_eye_height = self.right_eye_height = orig_h
        self.draw_eyes()

    def sleep(self):
        self.left_eye_height = self.right_eye_height = 0
        self.draw_eyes()

    def wakeup(self):
        self.left_eye_height = self.right_eye_height = self.ref_eye_height
        self.draw_eyes()

    def happy_eye(self, frames=10, step=2, frame_delay=0.05, hold=1.0):
        offset = self.ref_eye_height // 2
        for _ in range(frames):
            img = Image.new("RGB", (self.lcd.width, self.lcd.height), self.lcd.bg_color)
            draw = ImageDraw.Draw(img)
            self._draw_base_eyes(draw)

            # segitiga kiri
            left_tri = [
                (self.left_eye_x - self.left_eye_width // 2 - 5, self.left_eye_y + offset),
                (self.left_eye_x + self.left_eye_width // 2 + 10, self.left_eye_y + 5 + offset),
                (self.left_eye_x - self.left_eye_width // 2 - 5, self.left_eye_y + self.left_eye_height + offset),
            ]
            draw.polygon(left_tri, fill=self.lcd.bg_color)

            # segitiga kanan
            right_tri = [
                (self.right_eye_x + self.right_eye_width // 2 + 5, self.right_eye_y + offset),
                (self.right_eye_x - self.right_eye_width // 2 - 10, self.right_eye_y + 5 + offset),
                (self.right_eye_x + self.right_eye_width // 2 + 5, self.right_eye_y + self.right_eye_height + offset),
            ]
            draw.polygon(right_tri, fill=self.lcd.bg_color)

            self.lcd.disp.display(img)
            offset -= step
            time.sleep(frame_delay)

        time.sleep(hold)
        self.draw_eyes()

    def move_big_eye(self, dx=15, dy=0):
        self.left_eye_x += dx
        self.left_eye_y += dy
        self._clamp_position()
        self.draw_eyes()

    def random_saccade(self):
        self.move_big_eye(random.choice([-10, 0, 10]),
                          random.choice([-5, 0, 5]))
                          
    def sleep_then_wakeup(self):
        self.sleep()
        time.sleep(0.5)
        self.wakeup()
