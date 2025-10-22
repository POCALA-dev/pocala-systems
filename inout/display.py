import time
import textwrap
from pathlib import Path
from utils.path_helper import get_resource_path

import ST7789
from PIL import Image, ImageDraw, ImageFont


class PocalaDisplay:
    """
    Wrapper untuk ST7789 Display:
    - Teks statis
    - Scroll teks
    - Pesan singkat
    """

    def __init__(
        self,
        font_path = get_resource_path('fonts', 'InterDisplay-Regular.ttf'),
        font_size=22,
        bg_color=(0, 0, 0),
        fg_color=(193, 255, 114)
    ):
        """Inisialisasi display dan font."""
        try:
            self.disp = ST7789.ST7789(
                port=0,
                cs=0,
                rst=5,
                dc=6,
                backlight=None,
                spi_speed_hz=80 * 1_000_000
            )
            self.disp._spi.mode = 3
            self.disp.reset()
            self.disp._init()
        except Exception as e:
            print(f"[ERROR] Gagal inisialisasi ST7789: {e}")
            raise

        self.width = self.disp.width
        self.height = self.disp.height

        try:
            if not Path(font_path).exists():
                raise FileNotFoundError(f"Font tidak ditemukan: {font_path}")
            self.font_main = ImageFont.truetype(font_path, font_size)
        except Exception as e:
            print(f"[WARNING] Font gagal dimuat, pakai default: {e}")
            self.font_main = ImageFont.load_default()

        self.bg_color = bg_color
        self.fg_color = fg_color

    def _create_canvas(self):
        """Buat kanvas kosong untuk menggambar teks."""
        image = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(image)
        return image, draw

    def clear(self):
        """Bersihkan layar."""
        image = Image.new("RGB", (self.width, self.height), self.bg_color)
        self.disp.display(image)

    def display_text(self, text, color=None):
        """Tampilkan teks statis."""
        color = color or self.fg_color
        image, draw = self._create_canvas()
        wrapped = textwrap.wrap(text, width=18)

        y = 10
        for line in wrapped:
            draw.text((10, y), line, font=self.font_main, fill=color)
            bbox = self.font_main.getbbox(line)
            y += (bbox[3] - bbox[1]) + 4

        self.disp.display(image)

    def scroll_text(self, text, speed=0.08):
        """Tampilkan teks panjang dengan scroll vertikal."""
        wrapped = textwrap.wrap(text, width=16)
        line_height = (self.font_main.getbbox("A")[3] -
                       self.font_main.getbbox("A")[1] + 4)
        total_height = len(wrapped) * line_height

        if total_height <= self.height:
            self.display_text(text)
            return

        image_height = total_height + 20
        image = Image.new("RGB", (self.width, image_height), self.bg_color)
        draw = ImageDraw.Draw(image)

        y = 0
        for line in wrapped:
            draw.text((5, y), line, font=self.font_main, fill=self.fg_color)
            y += line_height

        for top in range(0, y - self.height + 10, 2):
            frame = image.crop((0, top, self.width, top + self.height))
            self.disp.display(frame)
            time.sleep(speed)

    def flash_message(self, text, duration=1.5, color=None):
        """Tampilkan pesan singkat lalu hilang."""
        self.display_text(text, color=color)
        time.sleep(duration)
        self.clear()

    def display_image(self, image_path):
        """
        Tampilkan gambar di layar
        """
        try:
            image = Image.open(image_path)
            image = image.resize((self.width, self.height), resample=Image.LANCZOS)
            self.disp.display(image)
        except Exception as e:
            print(f"[ERROR] Gagal menampilkan gambar '{image_path}': {e}")
            
    def show_demo(self):
        """Demo sederhana."""
        self.display_text("Translator siap digunakan")
        time.sleep(2)
        paragraph = (
            "Edukasi adalah proses untuk mengembangkan pengetahuan, keterampilan, "
            "dan nilai-nilai dalam diri individu, yang membantu mereka "
            "tumbuh dan berkembang dalam masyarakat."
        )
        self.scroll_text(paragraph)
