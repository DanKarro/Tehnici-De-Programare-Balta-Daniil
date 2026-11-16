import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arsenal.forensics.decode import (
    ghici_strat,
    desfa,
    desfa_straturi,
    citibil,
    sparge_xor,
    identifica_hash,
)


def test_ghici_strat_base64():
    assert ghici_strat("U2FsdXQ=") == "base64"


def test_ghici_strat_hex():
    assert ghici_strat("48656c6c6f") == "hex"


def test_ghici_strat_url():
    assert ghici_strat("%2Fetc%2Fpasswd") == "url"


def test_desfa_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"


def test_desfa_hex():
    strat, b = desfa("48656c6c6f")
    assert strat == "hex"
    assert b == b"Hello"


def test_desfa_url():
    strat, b = desfa("%2Fetc%2Fpasswd")
    assert strat == "url"
    assert b == b"/etc/passwd"


def test_citibil():
    assert citibil(b"text normal")
    assert not citibil(bytes([0, 1, 2, 255]))


def test_desfa_straturi_multiple():
    # "ascuns" -> hex -> base64 (doua straturi suprapuse)
    import base64 as b64

    nivel1 = "ascuns".encode().hex()          # hex peste text
    nivel0 = b64.b64encode(nivel1.encode()).decode()  # base64 peste hex
    strat, b, istoric = desfa_straturi(nivel0)
    assert b == b"ascuns"
    assert istoric[0] == "base64"
    assert istoric[1] == "hex"


def test_sparge_xor():
    cheie = 0x42
    original = b"parola"
    date = bytes(c ^ cheie for c in original)
    candidati = sparge_xor(date)
    gasiti = [k for k, clar in candidati if clar == original]
    assert cheie in gasiti


def test_identifica_hash():
    assert identifica_hash("5f4dcc3b5aa765d61d8327deb882cf99") == "md5"
    assert identifica_hash("a" * 40) == "sha1"
    assert identifica_hash("a" * 64) == "sha256"
    assert identifica_hash("prea scurt") == "necunoscut"
