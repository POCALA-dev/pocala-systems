from PIL import ImageDraw

def draw_round_rect(draw: ImageDraw.Draw, x0, y0, x1, y1, radius, fill):
    """
    Utility untuk menggambar rounded rectangle.
    """
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
