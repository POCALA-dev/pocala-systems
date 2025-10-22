# utils/response_menu.py

def is_online(text: str) -> bool:
    """
    Deteksi apakah input user memilih 'online mode'.
    """
    keywords = ["online", "online mode", "mode online", "internet"]
    text = text.lower().strip()
    return any(word in text for word in keywords)


def is_offline(text: str) -> bool:
    """
    Deteksi apakah input user memilih 'offline mode'.
    """
    keywords = ["offline", "offline mode", "mode offline", "luring"]
    text = text.lower().strip()
    return any(word in text for word in keywords)


def is_learning_audio(text: str) -> bool:
    """
    Deteksi apakah input user memilih 'learning audio'.
    """
    keywords = ["learn", "learning audio", "audio belajar", "belajar audio", "music","musik", "lagu", "belajar musik"]
    text = text.lower().strip()
    return any(word in text for word in keywords)
