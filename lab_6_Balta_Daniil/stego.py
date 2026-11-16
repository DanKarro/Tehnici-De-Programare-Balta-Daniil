"""
stego.py

Lucrarea B5-B6: steganografie LSB (Least Significant Bit).
  - ascunde(gazda, mesaj)   -> scrie mesajul in ultimul bit al fiecarui canal
  - dezvaluie(stego)        -> citeste biții inapoi si reconstituie mesajul
  - detecteaza(cale)        -> urma statistica (distributia ultimilor biti)

Mesajul se incheie intotdeauna cu un octet 0x00 (santinela), ca
dezvaluirea sa stie unde se opreste.
"""
from collections import Counter

from PIL import Image


# ---------------------------------------------------------------------------
# B5: ascunzi mesajul
# ---------------------------------------------------------------------------
def ascunde(cale_gazda: str, mesaj: bytes, cale_iesire: str = "stego.png") -> str:
    """Scrie mesaj + un octet 0x00 de final in ultimul bit al fiecarui canal RGB."""
    img = Image.open(cale_gazda).convert("RGB")
    px = list(img.getdata())

    mesaj_cu_final = mesaj + b"\x00"
    biti = "".join(f"{b:08b}" for b in mesaj_cu_final)

    if len(biti) > len(px) * 3:
        raise ValueError(
            f"mesajul ({len(mesaj)} octeti) e prea lung pentru aceasta imagine "
            f"({len(px)} pixeli, {len(px) * 3} biti disponibili)"
        )

    px_nou = []
    idx = 0
    for (r, g, b) in px:
        canale = [r, g, b]
        for c in range(3):
            if idx < len(biti):
                canale[c] = (canale[c] & ~1) | int(biti[idx])
                idx += 1
        px_nou.append(tuple(canale))

    img.putdata(px_nou)
    img.save(cale_iesire)  # PNG: fara pierdere, biții raman intacți
    return cale_iesire


# ---------------------------------------------------------------------------
# B6: dezvalui mesajul
# ---------------------------------------------------------------------------
def dezvaluie(cale_stego: str) -> bytes:
    """Citeste ultimul bit al fiecarui canal si reconstituie mesajul pana la 0x00."""
    px = list(Image.open(cale_stego).convert("RGB").getdata())

    biti = []
    for (r, g, b) in px:
        biti.append(r & 1)
        biti.append(g & 1)
        biti.append(b & 1)

    octeti = bytearray()
    for i in range(0, len(biti) - 7, 8):
        octet = 0
        for bit in biti[i:i + 8]:
            octet = (octet << 1) | bit
        if octet == 0:  # santinela de final
            break
        octeti.append(octet)

    return bytes(octeti)


# ---------------------------------------------------------------------------
# Detectie: nu mesajul, ci urma lui
# ---------------------------------------------------------------------------
def detecteaza(cale: str) -> Counter:
    """Distributia ultimului bit pe canalul rosu; ~50/50 e un semnal suspect."""
    px = list(Image.open(cale).convert("RGB").getdata())
    ultimii = [r & 1 for (r, g, b) in px]
    return Counter(ultimii)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4 and sys.argv[1] == "ascunde":
        cale_gazda, mesaj_text = sys.argv[2], sys.argv[3]
        iesire = ascunde(cale_gazda, mesaj_text.encode())
        print("mesaj ascuns in", iesire)
    elif len(sys.argv) >= 3 and sys.argv[1] == "dezvaluie":
        cale_stego = sys.argv[2]
        print(dezvaluie(cale_stego).decode(errors="replace"))
    else:
        print("folosire:")
        print("  python stego.py ascunde gazda.png 'mesaj'")
        print("  python stego.py dezvaluie stego.png")
