"""
arsenal/forensics/decode.py

Decoder universal de forensics (Lucrarea A, A1-A7).

Ce face:
  - ghici_strat(s)   -> recunoaste stratul (base64 / hex / url) dupa forma sirului
  - desfa(s)         -> desface un singur strat, intoarce (strat, octeti)
  - desfa_straturi(s)-> desface repetat pana iese text citibil (straturi multiple)
  - citibil(b)       -> True daca octetii arata a text ASCII imprimabil
  - sparge_xor(date) -> incearca toate cele 256 chei de un octet (forta bruta)
  - identifica_hash(h) / sparge_hash(h, wordlist) -> identifica algoritmul dupa
    lungime si sparge hash-ul prin dictionar
  - ruleaza(...)     -> punctul central, folosit si de CLI (A7)
"""
import re
import json
import base64
import hashlib
import argparse
from urllib.parse import unquote


# ---------------------------------------------------------------------------
# A1 / A4: text vs octeti, si criteriul "arata a text"
# ---------------------------------------------------------------------------
def citibil(b: bytes) -> bool:
    """True daca toti octetii sunt in intervalul ASCII imprimabil (32..126)."""
    if not b:
        return False
    return all(32 <= c < 127 for c in b)


# ---------------------------------------------------------------------------
# A2: recunosti stratul dupa forma (NU decodezi inca)
# ---------------------------------------------------------------------------
def ghici_strat(s: str) -> str:
    """
    Ghiceste ce codare e un sir, uitandu-se doar la alfabetul folosit.
    Ordinea conteaza: %xx (url) e cel mai specific, apoi hex (strict:
    doar 0-9 a-f, lungime para), apoi base64 (alfabetul cel mai larg).
    """
    if re.search(r"%[0-9A-Fa-f]{2}", s):
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"


# ---------------------------------------------------------------------------
# A3: desfaci stratul recunoscut
# ---------------------------------------------------------------------------
def desfa(s: str):
    """Desface stratul recunoscut de ghici_strat. Intoarce (strat, octeti)."""
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "url":
            return strat, unquote(s).encode()
    except Exception:
        pass
    return "necunoscut", s.encode()


# ---------------------------------------------------------------------------
# A4: straturi multiple, intr-o bucla
# ---------------------------------------------------------------------------
def desfa_straturi(s: str, pas_maxim: int = 8):
    """
    Desface repetat pana nu mai recunoastem niciun strat (sau pana la
    pas_maxim incercari, ca sa nu intram in bucla infinita). Un rezultat
    poate fi, la randul lui, o alta codare (ex: base64 peste hex peste
    text) - de aceea NU ne oprim doar fiindca rezultatul e citibil, ci
    doar cand ghici_strat() nu mai recunoaste nimic de desfacut, sau cand
    octetii nu mai sunt text valid (am ajuns la octeti bruti de fisier).
    Intoarce (ultimul_strat, octeti_finali, istoricul straturilor incercate).
    """
    istoric = []
    val = s
    strat, b = "necunoscut", s.encode()
    for _ in range(pas_maxim):
        strat, b = desfa(val)
        istoric.append(strat)
        if strat == "necunoscut":
            break
        try:
            val = b.decode()
        except UnicodeDecodeError:
            break
    return strat, b, istoric


# ---------------------------------------------------------------------------
# A5: spargi un XOR cu cheie de un octet, prin forta bruta
# ---------------------------------------------------------------------------
def _scor_plauzibilitate(clar: bytes) -> float:
    """
    Cat de mult 'arata a text' un rezultat citibil: ponderam literele si
    spatiile, fiindca textul normal e aproape numai din astea. Pe mesaje
    scurte, filtrul simplu (32..126) lasa sa treaca mai multi candidati;
    scorul asta departajeaza intre ei, fara sa fie nevoie de un dictionar.
    """
    if not clar:
        return 0.0
    litere_si_spatii = sum(1 for c in clar if chr(c).isalpha() or c == 32)
    return litere_si_spatii / len(clar)


def sparge_xor(date: bytes):
    """
    Incearca toate cele 256 de chei de un octet. Intoarce lista
    (cheie, octeti_clar) pentru fiecare rezultat complet citibil,
    sortata descrescator dupa cat de plauzibil arata ca text
    (vezi _scor_plauzibilitate) - primul element e cel mai probabil.
    """
    candidati = []
    for k in range(256):
        clar = bytes(c ^ k for c in date)
        if citibil(clar):
            candidati.append((k, clar))
    candidati.sort(key=lambda kc: _scor_plauzibilitate(kc[1]), reverse=True)
    return candidati


# ---------------------------------------------------------------------------
# A6: identifici si spargi un hash prin dictionar
# ---------------------------------------------------------------------------
_LUNGIME_ALGORITM = {32: "md5", 40: "sha1", 64: "sha256"}


def identifica_hash(h: str) -> str:
    """Ghiceste algoritmul dupa lungimea sirului hex (32/40/64)."""
    return _LUNGIME_ALGORITM.get(len(h.strip()), "necunoscut")


def sparge_hash(tinta: str, cale_wordlist: str):
    """
    Sparge un hash md5/sha1/sha256 prin dictionar: hashuieste fiecare cuvant
    din wordlist si compara cu tinta. Intoarce cuvantul gasit, sau None.
    """
    tinta = tinta.strip()
    algoritm = identifica_hash(tinta)
    if algoritm == "necunoscut":
        return None
    func = getattr(hashlib, algoritm)
    with open(cale_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.strip()
            if not cuv:
                continue
            if func(cuv.encode()).hexdigest() == tinta:
                return cuv
    return None


# ---------------------------------------------------------------------------
# A7: leaga totul, pentru CLI si pentru fisa.json
# ---------------------------------------------------------------------------
def ruleaza(intrare: str, din_fisier: bool = False) -> dict:
    """
    Punctul central al decoderului:
      - daca din_fisier: citeste octetii fisierului; daca nu e text direct,
        incearca sa sparga un XOR de un octet.
      - altfel: trateaza intrarea ca sir si desface straturile de codare.
    Intoarce o fisa (dict) gata de salvat in JSON.
    """
    if din_fisier:
        date = open(intrare, "rb").read()
        if citibil(date):
            return {"strat": "text", "rezultat": date.decode()}
        candidati = sparge_xor(date)
        if candidati:
            cheie, clar = candidati[0]
            return {
                "strat": "xor",
                "cheie": cheie,
                "rezultat": clar.decode(errors="replace"),
            }
        return {"strat": "necunoscut", "rezultat_hex": date.hex()}

    strat, b, istoric = desfa_straturi(intrare)
    try:
        rezultat = b.decode()
    except UnicodeDecodeError:
        rezultat = b.hex()
    return {"strat": strat, "straturi_incercate": istoric, "rezultat": rezultat}


def main():
    p = argparse.ArgumentParser(description="Decoder universal de forensics")
    p.add_argument("intrare", help="sir de caractere, sau o cale de fisier cu --fisier")
    p.add_argument("--fisier", action="store_true", help="trateaza intrarea ca o cale de fisier (octeti)")
    p.add_argument("--iesire", default="arsenal/forensics/fisa.json", help="unde salvezi fisa JSON")
    a = p.parse_args()

    fisa = ruleaza(a.intrare, din_fisier=a.fisier)
    print(fisa)

    with open(a.iesire, "w", encoding="utf-8") as f:
        json.dump(fisa, f, ensure_ascii=False, indent=2)
    print("fisa salvata in", a.iesire)


if __name__ == "__main__":
    main()
