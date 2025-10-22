import os

def get_resource_path(*relative_path_parts):
    """
    Mengembalikan path absolut ke resource berdasarkan root project.
    
    Usage:
        font_path = get_resource_path('fonts', 'InterDisplay-Regular.ttf')
        model_path = get_resource_path('models', 'translator_model.pt')
        audio_path = get_resource_path('audio', 'beep.wav')
    """
    # Ambil folder root project
    # Asumsi script utama dijalankan dari root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    # Gabungkan root dengan path relatif resource
    return os.path.join(root_dir, *relative_path_parts)

"""
Cara memanggil:
from utils.path_helper import get_resource_path
font_path = get_resource_path('folder', 'nama file')
"""
