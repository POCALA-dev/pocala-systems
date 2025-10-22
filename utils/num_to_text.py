import re

# Pemetaan angka ke kata (Indonesia)
angka_map = {
    0: "nol",
    1: "satu",
    2: "dua",
    3: "tiga",
    4: "empat",
    5: "lima",
    6: "enam",
    7: "tujuh",
    8: "delapan",
    9: "sembilan"
}

# Satuan besar Indonesia
satuan_besar = ["", "ribu", "juta", "miliar", "triliun"]

# Simbol matematis Indonesia
simbol_map_id = {
    "+": "tambah",
    "-": "kurang",
    "*": "kali",
    "/": "bagi",
    "=": "sama dengan",
    "%": "persen",
    "&": "dan",
    "#": "nomor",
    "@": "at",  # atau "di"
    "^": "pangkat",
    "<": "kurang dari",
    ">": "lebih dari"
}

# Simbol matematis English
simbol_map_en = {
    "+": "plus",
    "-": "minus",
    "*": "times",
    "/": "divided by",
    "=": "equals",
    "%": "percent",
    "&": "and",
    "#": "number",
    "@": "at",
    "^": "to the power of",
    "<": "less than",
    ">": "greater than"
}


def ubah_angka_ke_kata(angka_str):
    """
    Mengubah string angka menjadi kata-kata dalam Bahasa Indonesia.
    Mendukung angka desimal.
    """
    bagian = angka_str.split(".")
    angka_bulat = bagian[0]
    angka_desimal = bagian[1] if len(bagian) > 1 else ""

    parts = []
    while len(angka_bulat) > 3:
        parts.insert(0, angka_bulat[-3:])
        angka_bulat = angka_bulat[:-3]
    if angka_bulat:
        parts.insert(0, angka_bulat)

    hasil_kata = []
    total_parts = len(parts)

    for i, part in enumerate(parts):
        part = part.zfill(3)
        ratus, puluh, satu = int(part[0]), int(part[1]), int(part[2])
        pos = total_parts - i - 1
        kata = []

        if ratus > 0:
            kata.append(
                "seratus" if ratus == 1 else f"{angka_map[ratus]} ratus"
            )

        if puluh > 0:
            if puluh == 1:
                if satu == 0:
                    kata.append("sepuluh")
                elif satu == 1:
                    kata.append("sebelas")
                else:
                    kata.append(f"{angka_map[satu]} belas")
                satu = 0
            else:
                kata.append(f"{angka_map[puluh]} puluh")

        if satu > 0:
            kata.append(angka_map[satu])

        hasil = " ".join(kata)
        if hasil:
            if part == "001" and pos > 0:
                hasil_kata.append(f"se{satuan_besar[pos]}")
            else:
                hasil_kata.append(f"{hasil} {satuan_besar[pos]}".strip())

    hasil = " ".join(hasil_kata)

    if angka_desimal:
        koma = " ".join(angka_map[int(d)] for d in angka_desimal)
        hasil += f" koma {koma}"

    return hasil.strip()


def angka_ke_kata_id(text):
    """
    Mengonversi angka dan simbol menjadi kata-kata
    dalam Bahasa Indonesia.
    """

    def ganti_angka(match):
        return ubah_angka_ke_kata(match.group(0))

    text = re.sub(r"\d+(\.\d+)?", ganti_angka, text)

    for simbol, kata in simbol_map_id.items():
        if simbol != "-":
            text = text.replace(simbol, f" {kata} ")

    text = re.sub(r"\s-\s", " kurang ", text)
    return re.sub(r"\s+", " ", text).strip()


def simbol_ke_kata_en(text):
    """
    Mengonversi simbol matematika ke kata dalam Bahasa Inggris.
    Angka tidak diubah.
    """
    for simbol, kata in simbol_map_en.items():
        if simbol != "-":
            text = text.replace(simbol, f" {kata} ")

    text = re.sub(r"\s-\s", " minus ", text)
    return re.sub(r"\s+", " ", text).strip()


def convert_text(text, lang="id"):
    """
    Konversi teks berdasarkan bahasa:
    - "id": ubah angka + simbol ke kata (Bahasa Indonesia)
    - "en": ubah simbol ke kata (Bahasa Inggris)
    """
    if lang.lower() == "id":
        return angka_ke_kata_id(text)
    if lang.lower() == "en":
        return simbol_ke_kata_en(text)
    return text
