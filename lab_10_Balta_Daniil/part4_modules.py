# Laborator: funcții, metode și importuri pe web
# Student: Nume Prenume

import hashlib
import json
import re
import socket
import ssl
import time
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import List, Tuple
from urllib.parse import urljoin, urlparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# ==========================================================================
# Partea 4: Alte module din biblioteca standard (exercițiile 35-43)
# ==========================================================================


# --- Exercițiul 35. Descompunerea unui URL ---------------------------------
def show_url_parts(url: str) -> None:
    """Afișează părțile unui URL: scheme, netloc, path, query, fragment."""
    parts = urllib.parse.urlparse(url)
    print("  .scheme  :", parts.scheme)
    print("  .netloc  :", parts.netloc)
    print("  .path    :", parts.path)
    print("  .query   :", parts.query)
    print("  .fragment:", parts.fragment)


# --- Exercițiul 36. Compunerea URL-urilor ----------------------------------
def join_examples(base: str) -> List[str]:
    """Transformă legături relative în URL-uri complete, pornind de la `base`."""
    relative_links = ["/about", "contact.html", "../index.html"]
    return [urljoin(base, link) for link in relative_links]


# --- Exercițiul 37. Extragerea legăturilor ---------------------------------
def extract_links(html: str) -> List[str]:
    """Returnează legăturile href din html, fără duplicate, în ordinea din pagină."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))  # dict păstrează ordinea => fără duplicate


# --- Exercițiul 38. Interne sau externe? -----------------------------------
def split_links(links: List[str], domain: str) -> Tuple[List[str], List[str]]:
    """Returnează (legături_interne, legături_externe) față de `domain`.

    Legăturile care nu sunt http/https (mailto:, javascript: etc.) sunt ignorate.
    """
    internal, external = [], []
    base = "https://" + domain
    for link in links:
        full = urljoin(base, link)  # mai întâi URL complet
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc.lower() == domain.lower():  # apoi comparăm domeniul
            internal.append(full)
        else:
            external.append(full)
    return internal, external


# --- Exercițiul 39. Propriile metode: ImageFinder --------------------------
class ImageFinder(HTMLParser):
    """Parser HTML care colectează atributul src al fiecărui tag <img>."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Apelată automat de parser pentru fiecare tag de deschidere."""
        # HTMLParser transformă numele tag-urilor și ale atributelor în litere
        # mici, deci <IMG SRC="..."> este tratat la fel ca <img src="...">.
        if tag == "img":
            src = dict(attrs).get("src")
            if src:  # ignorăm <img> fără src
                self.images.append(src)


# --- Exercițiul 40. Amprenta paginii ---------------------------------------
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 (hex) a conținutului paginii."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()


# --- Exercițiul 41. Salvarea în JSON ---------------------------------------
def save_headers(url: str, filename: str = "headers.json") -> str:
    """Salvează antetele paginii în fișier JSON, le reîncarcă și returnează Server."""
    response = requests.get(url, timeout=TIMEOUT)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2)
    with open(filename, encoding="utf-8") as file:
        loaded = json.load(file)
    return loaded.get("Server", "lipsește")


# --- Exercițiul 42. Interogare DNS -----------------------------------------
def resolve(hostname: str) -> str:
    """Returnează adresa IP (IPv4) a domeniului `hostname`."""
    return socket.gethostbyname(hostname)


# --- Exercițiul 43. Expirarea certificatului -------------------------------
def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până la expirarea certificatului lui `hostname`."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            cert = secure_sock.getpeercert()
    expires_ts = ssl.cert_time_to_seconds(cert["notAfter"])
    expires = datetime.fromtimestamp(expires_ts, tz=timezone.utc)
    return (expires - datetime.now(timezone.utc)).days


# ==========================================================================
# Rulare (doar când fișierul este pornit direct)
# ==========================================================================
if __name__ == "__main__":
    print("Ex. 35:")
    show_url_parts("https://cybercor.org/path?x=1#top")

    print("Ex. 36:", join_examples(BASE_URL))

    html = requests.get(BASE_URL, timeout=TIMEOUT).text
    links = extract_links(html)
    print("Ex. 37:", len(links), "legături unice")

    internal, external = split_links(links, "cybercor.org")
    print("Ex. 38:", len(internal), "interne,", len(external), "externe")

    # Ex. 39: întâi testul pe HTML cunoscut, apoi pe site-ul real
    test_html = """
<html><body>
  <img src="/logo.png" alt="Logo">
  <IMG SRC="poza.jpg">
  <img alt="imagine fără src">
  <img src="https://cdn.example.com/banner.webp" />
  <a href="/despre">Aceasta nu este o imagine</a>
</body></html>
"""

    finder = ImageFinder()
    finder.feed(test_html)
    print(finder.images)

    assert finder.images == [
        "/logo.png",                            # imagine obișnuită
        "poza.jpg",                             # tag scris cu majuscule
        "https://cdn.example.com/banner.webp",  # tag care se închide singur
    ], "Parserul nu a găsit exact imaginile așteptate"
    print("Testul a trecut!")

    time.sleep(1)
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    finder = ImageFinder()
    finder.feed(response.text)
    print(len(finder.images), "imagini găsite")
    for src in finder.images:
        print(src)
    # Verificare încrucișată cu numărătoarea simplă de "<img"
    print("Verificare: text.lower().count('<img') =", response.text.lower().count("<img"))

    time.sleep(1)
    first = page_fingerprint(BASE_URL)
    time.sleep(1)
    second = page_fingerprint(BASE_URL)
    print("Ex. 40:", first[:16], "...", "identice" if first == second else "DIFERITE")
    # Amprentele ar fi diferite dacă pagina conține conținut dinamic (token
    # CSRF, oră, reclame, contor de vizitatori) sau dacă între cele două cereri
    # s-a schimbat pagina sau a răspuns alt server din spatele unui load balancer.

    time.sleep(1)
    print("Ex. 41: Server (citit din headers.json) =", save_headers(BASE_URL))

    print("Ex. 42: IP cybercor.org =", resolve("cybercor.org"))
    print("Ex. 43: zile până la expirarea certificatului =", cert_days_left("cybercor.org"))

# ==========================================================================
# Verificați-vă: cine apelează handle_starttag()?
# ==========================================================================
# O apelează parserul însuși, din interiorul metodei feed(): pe măsură ce
# parcurge textul HTML și întâlnește un tag de deschidere, apelează metoda
# noastră. Noi o apelăm doar "indirect", prin finder.feed(...). Este un
# mecanism de tip callback: noi scriem reacția, biblioteca decide când se
# execută.
