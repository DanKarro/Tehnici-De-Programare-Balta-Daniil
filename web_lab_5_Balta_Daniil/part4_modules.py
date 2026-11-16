# Laborator: funcții, metode și importuri pe web
# Student: Balta Daniil

import re
import hashlib
import json
import socket
import ssl
import time
from datetime import datetime
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser
import requests

BASE_URL = "https://cybercor.org"
TIMEOUT = 10

# Exercițiul 35
def show_url_parts(url: str) -> None:
    """Afișează componentele unui URL."""
    parsed = urlparse(url)
    print("scheme:", parsed.scheme)
    print("netloc:", parsed.netloc)
    print("path:", parsed.path)
    print("query:", parsed.query)
    print("fragment:", parsed.fragment)

# Exercițiul 36
def show_joined_urls(base: str) -> None:
    """Afișează URL-urile complete pentru căile relative cerute."""
    for path in ["/about", "contact.html", "../index.html"]:
        print(path, "->", urljoin(base.rstrip("/") + "/", path))

# Exercițiul 37
def extract_links(html: str) -> list:
    """Extrage legăturile href fără duplicate, păstrând ordinea."""
    links = re.findall(r'href="([^"]+)"', html)
    return list(dict.fromkeys(links))

# Exercițiul 38
def split_links(links: list, domain: str) -> tuple:
    """Împarte linkurile în interne și externe folosind domeniul indicat."""
    internal, external = [], []
    base = "https://" + domain
    for link in links:
        absolute = urljoin(base + "/", link)
        netloc = urlparse(absolute).netloc
        if netloc == domain or netloc == domain.removeprefix("www."):
            internal.append(link)
        else:
            external.append(link)
    return internal, external

# Exercițiul 39
class ImageFinder(HTMLParser):
    """Parser care colectează atributul src al tag-urilor img."""
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Adaugă src dacă tag-ul este img și atributul există."""
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)

# Exercițiul 40
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 a corpului răspunsului."""
    response = requests.get(url, timeout=TIMEOUT)
    return hashlib.sha256(response.content).hexdigest()

# Exercițiul 41
def save_headers(url: str, filename: str = "headers.json") -> None:
    """Salvează antetele în JSON, le recitește și afișează un antet."""
    response = requests.get(url, timeout=TIMEOUT)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2)
    with open(filename, "r", encoding="utf-8") as file:
        headers = json.load(file)
    print("Content-Type:", headers.get("Content-Type", "lipsește"))

# Exercițiul 42
def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 asociată numelui de gazdă."""
    return socket.gethostbyname(hostname)

# Exercițiul 43
def cert_days_left(hostname: str) -> int:
    """Conectează la portul 443 și returnează zilele rămase până la expirarea certificatului."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            cert = secure_sock.getpeercert()
    expiry_seconds = ssl.cert_time_to_seconds(cert["notAfter"])
    remaining = expiry_seconds - time.time()
    return int(remaining // 86400)

if __name__ == "__main__":
    show_url_parts("https://cybercor.org/path?x=1#top")
    show_joined_urls(BASE_URL)
    try:
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        links = extract_links(response.text)
        print("Ex. 37 - linkuri:", links)
        internal, external = split_links(links, "cybercor.org")
        print("Ex. 38 - interne:", internal)
        print("Ex. 38 - externe:", external)

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
        print("Ex. 39 - imagini test:", finder.images)
        assert finder.images == [
            "/logo.png", "poza.jpg", "https://cdn.example.com/banner.webp"
        ], "Parserul nu a găsit exact imaginile așteptate"
        print("Testul parserului a trecut!")
        time.sleep(1)
        finder_real = ImageFinder()
        finder_real.feed(response.text)
        print("Imagini pe site:", len(finder_real.images))
        print("Număr apariții <img:", response.text.lower().count("<img"))
        print("Ex. 40 - amprente:", page_fingerprint(BASE_URL), page_fingerprint(BASE_URL))
        save_headers(BASE_URL)
        print("Ex. 42 - IP:", resolve("cybercor.org"))
        print("Ex. 43 - zile certificat:", cert_days_left("cybercor.org"))
    except (requests.RequestException, OSError, ssl.SSLError, KeyError, ValueError) as error:
        print("Unele exerciții nu au putut fi finalizate:", error)
