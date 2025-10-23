import re

# Stop words untuk pembersihan
stop_words_id = {
    'apa', 'arti', 'dari', 'dalam', 'itu', 'adalah', 'maksud', 'artinya', 'bahasa', 'inggris', 'inggrisnya', 
    'terjemahan', 'terjemahkan', 'kata', 'beri', 'saya', 'ke', 'di', 'pada', 'untuk', 'dengan', 
    'atau', 'dan', 'yang', 'ini', 'tersebut', 'bisa', 'jadi', 'seperti', 'saya ingin tau tentang', 'saya ingin tahu tentang'
}
stop_words_en = {
    'what', 'is', 'the', 'of', 'in', 'to', 'a', 'an', 'does', 'mean', 'meaning', 'define', 
    'definition', 'translate', 'how', 'do', 'you', 'say', 'indonesian', 'tell', 'me', 'for', 
    'with', 'on', 'at', 'by', 'or', 'and', 'this', 'that', 'like', 'i want to know about'
}

def extract_vocab_word(text, lang="id"):
    """
    Mengekstrak kata kosa kata dari kalimat seperti 'apa arti laba-laba' atau 'what is the meaning of spider'.
    Robust untuk frasa multi-kata tanpa daftar valid.
    """
    if not text or len(text.strip()) == 0:
        return "No valid word found"
    
    text = text.lower().strip()
    # Ganti tanda hubung dengan spasi untuk menangani 'kupu-kupu' -> 'kupu kupu'
    text = text.replace("-", " ")
    # Hapus karakter non-alphanumerik kecuali spasi
    text = re.sub(r"[^\w\s]", "", text)
    
    # Pilih stop words berdasarkan bahasa
    stop_words = stop_words_id if lang == "id" else stop_words_en
    
    # Pola regex berdasarkan bahasa (diperluas untuk variasi)
    if lang == "id":
        patterns = [
            r"(?:apa arti dari|arti dari|apa arti|artinya|apa maksud dari|maksud dari|apa maksud|apa itu) (.+)",
            r"(?:apa bahasa inggris dari|bahasa inggris dari|apa bahasa inggris|apa terjemahan dari|terjemahkan) (.+)",
        ]
    else:
        patterns = [
            r"(?:what is the meaning of|what does|define|definition of|tell me the meaning of|what is) (.+)",
            r"(?:translate|how do you say|how to say|what is the indonesian of|i want to translate) (.+?) (?:to indonesian|in indonesian|$)",
        ]
    
    # Coba cocokkan pola
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            extracted = match.group(1).strip()
            # Bersihkan stop words
            words = extracted.split()
            valid_words = [word for word in words if word not in stop_words]
            # Ambil hingga 4 kata pertama yang valid untuk frasa multi-kata
            return " ".join(valid_words[:4]) if valid_words else extracted.split()[-1]
    
    # Fallback: bersihkan stop words dari seluruh text
    words = text.split()
    valid_words = [word for word in words if word not in stop_words]
    
    if not valid_words:
        return ""
    
    # Jika <=4 kata setelah bersih, ambil semua; jika lebih, ambil 4 kata terakhir
    if len(valid_words) <= 4:
        return " ".join(valid_words)
    else:
        return " ".join(valid_words[-4:])

# Stop words sederhana untuk membersihkan topik
stop_words = {'i', 'want', 'to', 'a', 'an', 'the', 'about', 'in', 'for', 'with', 'on', 'at', 'by', 'of', 'can', 'we', 'do', 
              'lets', 'try', 'let', 'us', 'learn', 'please', 'give', 'show', 'teach', 'me', 'explain', 'saya', 'ingin', 
              'mau', 'belajar', 'beri', 'aku', 'tentang', 'bahas', 'is', 'and', 'its', 'usage', 'like', 'talk'}

# Daftar topik grammar bahasa Inggris yang komprehensif (diurutkan longest first)
valid_topics = [
    "present perfect continuous tense", "past perfect continuous tense", "future perfect continuous tense",
    "simple present tense", "present continuous tense", "present perfect tense",
    "simple past tense", "past continuous tense", "past perfect tense",
    "simple future tense", "future continuous tense", "future perfect tense",
    "direct and indirect speech", "active and passive voice", "subject-verb agreement",
    "singular and plural nouns", "count and non-count nouns",
    "parts of speech", "reported speech", "direct speech", "indirect speech",
    "phrasal verbs", "conditional sentences", "adjective clauses", "relative clauses",
    "irregular verbs", "auxiliary verbs", "possessive nouns",
    "dangling modifiers", "embedded questions", "parallel structure",
    "conjunctive adverbs", "confusing words", "conversational language",
    "commonly misused words", "english clause syntax",
    "present tenses", "past tenses", "future tenses", "verb tenses",
    "comparatives", "superlatives", "subjunctive", "perfectives",
    "conditionals", "modals", "imperative", "if clauses", "wish",
    "passive voice", "active voice", "verb forms", "main verbs",
    "articles", "determiners", "nouns", "pronouns", "verbs", "adverbs",
    "adjectives", "prepositions", "conjunctions", "interjections",
    "relative pronouns", "reflexive pronouns", "indefinite pronouns",
    "proper nouns", "common nouns", "singular nouns",
    "action verbs", "be verbs", "antonyms", "case", "capitalization",
    "clause", "colon", "comma", "comma splice", "complement", "compound",
    "gender", "time-telling", "will", "would", "shall", "should",
    "ing form", "infinitive", "punctuation", "adjective forms", "nationalities"
]
# Urutkan berdasarkan panjang descending untuk match terpanjang dulu
valid_topics.sort(key=len, reverse=True)

# Precompile pola topik
def _normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^\w\s\-]", "", s)
    s = s.replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Precompile pola topik terhadap bentuk yang sudah dinormalisasi (tanpa minus)
TOPIC_PATTERNS = []
for t in valid_topics:
    t_norm = _normalize(t)  # contoh: "non-count" -> "non count"
    pat = re.compile(r'\b' + re.escape(t_norm).replace(r'\ ', r'\s+') + r'\b')
    TOPIC_PATTERNS.append((t, pat))  # simpan kanonik 't' + pola untuk teks yang sudah dinormalisasi

LEVEL_ALIASES = {
    "basic": "basic", "beginner": "basic", "elementary": "basic", "dasar": "basic", "pemula": "basic",
    "intermediate": "intermediate", "menengah": "intermediate", "mid": "intermediate",
    "advanced": "advanced", "advance": "advanced", "lanjutan": "advanced", "expert": "advanced"
}
LEVEL_RE = re.compile(r"\b(" + "|".join(map(re.escape, LEVEL_ALIASES.keys())) + r")\b")

def extract_topic_and_level(text):
    if not text or len(text.strip()) == 0:
        return {"topic": "No topic found", "level": "unspecified"}

    text = _normalize(text)

    # 1) Deteksi level (default: unspecified = tidak ditentukan)
    level = "unspecified"
    m = LEVEL_RE.search(text)
    if m:
        level = LEVEL_ALIASES[m.group(1)]
        text = LEVEL_RE.sub(" ", text)
        text = re.sub(r"\s+", " ", text).strip()

    # 2) Deteksi topik (pakai teks yang sudah dinormalisasi)
    for topic_canonical, rx in TOPIC_PATTERNS:
        if rx.search(text):
            return {"topic": topic_canonical, "level": level}

    # 3) Pola frasa
    patterns = [
        r"(?:i want to learn|i need to learn|teach me about|explain about|tell me about) (.+)",
        r"(?:can we learn|can you teach|could you explain) (.+)",
        r"(?:lets learn|lets try|let us learn) (.+)",
        r"(?:please give me|please show me) (.+)",
        r"(?:saya ingin belajar|saya mau belajar|beri saya|ajari saya) (.+)",
        r"(?:tentang|bahas) (.+)",
        r"(?:learn|study|discuss|talk about) (.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            topic_phrase = match.group(1).strip()
            topic_words = [w for w in topic_phrase.split() if w not in stop_words]
            cleaned_topic = " ".join(topic_words)

            # cek lagi ke daftar kanonik
            for topic_canonical, rx in TOPIC_PATTERNS:
                if rx.search(cleaned_topic):
                    return {"topic": topic_canonical, "level": level}

            return {"topic": cleaned_topic if cleaned_topic else text, "level": level}

    # 4) Fallback (pakai `text`)
    words = text.split()
    cleaned_words = [w for w in words if w not in stop_words]
    if not cleaned_words:
        topic_fb = " ".join(words[-2:]) if len(words) >= 2 else text
    elif len(cleaned_words) <= 5:
        topic_fb = " ".join(cleaned_words)
    else:
        topic_fb = " ".join(cleaned_words[-5:])

    return {"topic": topic_fb, "level": level}
