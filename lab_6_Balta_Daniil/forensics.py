"""
forensics.py

Lucrarea B1-B4: ce spune un fisier despre el.
  - tip_real(cale)        -> recunoaste formatul real dupa magic bytes
  - scoate_strings(cale)  -> text citibil dintr-un binar (regex pe octeti)
  - citeste_exif(cale)    -> metadatele EXIF ale unei poze
  - citeste_gps(cale)     -> latitudine/longitudine, in grade zecimale
  - extrage_ascuns(cale)  -> file carving: scoate un fisier lipit la coada
"""
import re

from PIL import Image
from PIL.ExifTags import TAGS

# ---------------------------------------------------------------------------
# B1: magic bytes
# ---------------------------------------------------------------------------
SEMNATURI = {
    b"\x89PNG": "png",
    b"\xff\xd8\xff": "jpeg",
    b"%PDF": "pdf",
    b"PK\x03\x04": "zip/docx",
    b"\x7fELF": "elf",
}


def tip_real(cale: str) -> str:
    """Citeste primii octeti si recunoaste formatul real, indiferent de extensie."""
    cap = open(cale, "rb").read(8)
    for semnatura, nume in SEMNATURI.items():
        if cap.startswith(semnatura):
            return nume
    return cap.hex()


# ---------------------------------------------------------------------------
# B2: strings
# ---------------------------------------------------------------------------
def scoate_strings(cale: str, lungime_minima: int = 4):
    """Scoate secventele de caractere imprimabile (4+) dintr-un fisier binar."""
    date = open(cale, "rb").read()
    tipar = ("[ -~]{%d,}" % lungime_minima).encode()
    return [m.decode() for m in re.findall(tipar, date)]


# ---------------------------------------------------------------------------
# B3: EXIF si GPS
# ---------------------------------------------------------------------------
def citeste_exif(cale: str) -> dict:
    """Intoarce metadatele EXIF, cu id-urile traduse in nume citibile."""
    exif_brut = Image.open(cale).getexif()
    return {TAGS.get(id_, id_): val for id_, val in exif_brut.items()}


def _grade_zecimale(valoare, emisfera):
    grade, minute, secunde = (float(x) for x in valoare)
    zecimal = grade + minute / 60 + secunde / 3600
    if emisfera in ("S", "W"):
        zecimal = -zecimal
    return zecimal


def citeste_gps(cale: str):
    """Extrage blocul GPS (tag 34853) si intoarce (latitudine, longitudine)."""
    exif = Image.open(cale).getexif()
    gps = exif.get_ifd(0x8825)  # 34853
    if not gps:
        return None
    lat = _grade_zecimale(gps[2], gps[1])
    lon = _grade_zecimale(gps[4], gps[3])
    return lat, lon


# ---------------------------------------------------------------------------
# B4: file carving
# ---------------------------------------------------------------------------
def extrage_ascuns(cale: str, semnatura: bytes = b"PK\x03\x04", iesire: str = "gasit.zip"):
    """Cauta semnatura unui al doilea fisier lipit la coada si il salveaza separat."""
    date = open(cale, "rb").read()
    i = date.find(semnatura)
    if i == -1:
        return None
    with open(iesire, "wb") as f:
        f.write(date[i:])
    return iesire, i


if __name__ == "__main__":
    print("--- B1: magic bytes ---")
    print("probe/foto.jpg  ->", tip_real("probe/foto.jpg"))
    print("probe/ascuns.png ->", tip_real("probe/ascuns.png"))

    print("\n--- B2: strings ---")
    for s in scoate_strings("probe/ascuns.png"):
        print(" ", s)

    print("\n--- B3: EXIF si GPS ---")
    for nume, val in citeste_exif("probe/foto.jpg").items():
        print(" ", nume, "=", val)
    print("  GPS:", citeste_gps("probe/foto.jpg"))

    print("\n--- B4: file carving ---")
    rezultat = extrage_ascuns("probe/ascuns.png", iesire="probe/gasit.zip")
    if rezultat:
        cale_iesire, pozitie = rezultat
        print("  arhiva extrasa de la octetul", pozitie, "->", cale_iesire)
    else:
        print("  nimic ascuns gasit")
