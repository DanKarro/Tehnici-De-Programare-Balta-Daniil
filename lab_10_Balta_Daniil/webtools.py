# Laborator: funcții, metode și importuri pe web
# Student: Nume Prenume
#
# webtools.py - modulul meu cu funcții reutilizabile (Partea 5).
# Conține funcțiile din Partea 3 și Partea 4, plus site_report() (ex. 50).

import csv
import json
import re
import socket
import ssl
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# Ex. 47: constantă de modul, folosită în fetch().
# Atenție: valoarea trebuie să conțină doar caractere ASCII.
DEFAULT_HEADERS = {"User-Agent": "WebLab-NumePrenume"}

SECURITY_HEADER_NAMES = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


# --------------------------------------------------------------------------
# Cereri de bază (ex. 21-23, 27, 29)
# --------------------------------------------------------------------------

def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarcă url cu GET (cu timeout și User-Agent) și returnează răspunsul."""
    return requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


def page_exists(url: str) -> bool:
    """Returnează True dacă pagina răspunde cu cod < 400, altfel False (fără erori)."""
    try:
        return fetch(url).ok
    except requests.RequestException:
        return False


def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului `name` de la url sau `default` dacă lipsește."""
    return fetch(url).headers.get(name, default)


def check_paths(base: str, paths: List[str]) -> Dict[str, Optional[int]]:
    """Returnează {cale: cod_de_stare} pentru fiecare cale (None dacă cererea eșuează).

    Face o pauză de 1 secundă între cereri.
    """
    results = {}
    for i, path in enumerate(paths):
        if i > 0:
            time.sleep(1)
        try:
            results[path] = get_status(urljoin(base, path))
        except requests.RequestException:
            results[path] = None
    return results


# --------------------------------------------------------------------------
# HTML: titlu, legături (ex. 24, 37, 38)
# --------------------------------------------------------------------------

def get_title(html: str) -> str:
    """Returnează textul dintre <title> și </title> (șir gol dacă lipsește)."""
    lower = html.lower()
    start = lower.find("<title>")
    if start == -1:
        return ""
    start += len("<title>")
    end = lower.find("</title>", start)
    if end == -1:
        return ""
    return html[start:end].strip()


def extract_links(html: str) -> List[str]:
    """Returnează legăturile href din html, fără duplicate, în ordinea din pagină."""
    links = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    return list(dict.fromkeys(links))  # dict păstrează ordinea => fără duplicate


def _normalize_host(netloc: str) -> str:
    """Pune domeniul cu litere mici și fără prefixul www. (funcție ajutătoare)."""
    netloc = netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def split_links(links: List[str], domain: str) -> Tuple[List[str], List[str]]:
    """Împarte legăturile în (interne, externe) față de `domain`.

    Legăturile care nu sunt http/https (mailto:, tel:, javascript:) sunt ignorate.
    """
    internal, external = [], []
    base = "https://" + domain
    for link in links:
        full = urljoin(base, link)
        parsed = urlparse(full)
        if parsed.scheme not in ("http", "https"):
            continue
        if _normalize_host(parsed.netloc) == _normalize_host(domain):
            internal.append(full)
        else:
            external.append(full)
    return internal, external


# --------------------------------------------------------------------------
# Antete de securitate (ex. 30, 31)
# --------------------------------------------------------------------------

def security_headers(url: str, response: Optional[requests.Response] = None) -> Dict[str, bool]:
    """Returnează {antet: True/False} pentru cele 5 antete de securitate.

    Dacă primește deja un `response`, nu mai trimite o cerere nouă.
    """
    if response is None:
        response = fetch(url)
    return {name: name in response.headers for name in SECURITY_HEADER_NAMES}


def score_headers(results: Dict[str, bool]) -> str:
    """Primește dicționarul din security_headers() și returnează un scor, ex. '3/5'."""
    return f"{sum(results.values())}/{len(results)}"


# --------------------------------------------------------------------------
# robots.txt (ex. 32)
# --------------------------------------------------------------------------

def fetch_robots(base: str) -> Optional[str]:
    """Returnează textul din /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = fetch(urljoin(base, "/robots.txt"))
    except requests.RequestException:
        return None
    return response.text if response.ok else None


def disallowed_paths(robots_text: Optional[str]) -> List[str]:
    """Returnează lista valorilor `Disallow:` din robots.txt (listă goală pentru None)."""
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip()  # eliminăm comentariile
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value and value not in paths:  # "Disallow:" gol = nimic interzis
                paths.append(value)
    return paths


# --------------------------------------------------------------------------
# Rețea: DNS, certificat, redirecționări (ex. 17, 42, 43)
# --------------------------------------------------------------------------

def resolve(hostname: str) -> str:
    """Returnează adresa IP (IPv4) pentru `hostname`."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str) -> int:
    """Returnează câte zile mai sunt până când expiră certificatul TLS al lui hostname."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            cert = secure_sock.getpeercert()
    expires_ts = ssl.cert_time_to_seconds(cert["notAfter"])
    expires = datetime.fromtimestamp(expires_ts, tz=timezone.utc)
    return (expires - datetime.now(timezone.utc)).days


def redirect_chain(url: str) -> List[str]:
    """Returnează lanțul de redirecționări ca șiruri de forma '301 -> adresa'."""
    response = fetch(url)
    urls_after = [r.url for r in response.history[1:]] + [response.url]
    return [f"{hop.status_code} -> {nxt}" for hop, nxt in zip(response.history, urls_after)]


# --------------------------------------------------------------------------
# Rapoarte (ex. 49, 50)
# --------------------------------------------------------------------------

def save_csv_report(results: Dict[str, Optional[int]], filename: str = "report.csv") -> None:
    """Salvează rezultatul din check_paths() în CSV: path, status, checked_at."""
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["path", "status", "checked_at"])
        for path, status in results.items():
            writer.writerow([path, status, datetime.now().isoformat()])


def _try(func, *args):
    """Apelează func(*args); returnează None dacă apare o eroare de rețea (ajutător)."""
    try:
        return func(*args)
    except (requests.RequestException, OSError, ssl.SSLError, ValueError, KeyError):
        return None


def _days_text(days: Optional[int]) -> str:
    """Scrie numărul de zile în română: '1 zi', '5 zile', '74 de zile' (ajutător)."""
    if days is None:
        return "indisponibil"
    if days == 1:
        return "1 zi rămasă"
    de = " de" if days % 100 == 0 or days % 100 >= 20 else ""
    return f"{days}{de} zile rămase"


def site_report(url: str, filename: str = "report.json") -> dict:
    """Colectează informații despre site, le afișează și le salvează în report.json.

    Trimite doar cereri GET, cu pauză de 1 secundă între ele.
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    # 1. Pagina principală: stare, URL final, titlu, antete, legături
    response = fetch(url)  # dacă eșuează aici, nu are sens raportul
    html = response.text
    title = get_title(html)
    security = security_headers(url, response)  # refolosim răspunsul, fără cerere nouă
    internal, external = split_links(extract_links(html), parsed.netloc)

    # 2. DNS și certificat (nu sunt cereri HTTP)
    ip = _try(resolve, hostname)
    days_left = _try(cert_days_left, hostname)

    # 3. Redirecționările pornind de la http://
    time.sleep(1)
    http_url = urlunparse(parsed._replace(scheme="http", path=parsed.path or "/"))
    chain = _try(redirect_chain, http_url)

    # 4. robots.txt
    time.sleep(1)
    disallowed = disallowed_paths(fetch_robots(url))

    report = {
        "url": url,
        "status_code": response.status_code,
        "final_url": response.url,
        "title": title,
        "ip": ip,
        "redirects": chain,
        "security_score": score_headers(security),
        "security_headers": security,
        "cert_days_left": days_left,
        "internal_links": len(internal),
        "external_links": len(external),
        "disallowed_paths": disallowed,
        "checked_at": datetime.now().isoformat(),
    }

    redirects_text = ", ".join(chain) if chain else "fără redirecționări"
    cert_text = _days_text(days_left)
    print(f"=== Raport site: {url} ===")
    print(f"Cod de stare:      {report['status_code']}")
    print(f"Titlu:             {title or 'lipsește'}")
    print(f"Adresă IP:         {ip or 'indisponibilă'}")
    print(f"Redirecționări:    {redirects_text}")
    print(f"Scor securitate:   {report['security_score']}")
    print(f"Certificat:        {cert_text}")
    print(f"Legături:          {len(internal)} interne, {len(external)} externe")
    print(f"Căi interzise:     {', '.join(disallowed) if disallowed else 'niciuna'}")

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print(f"Salvat în {filename}")
    return report


# Ex. 46: blocul __main__
# Codul de mai jos rulează doar când fișierul este pornit direct
# (python webtools.py), pentru că atunci __name__ == "__main__".
# Când main.py face `import webtools`, __name__ este "webtools", deci
# autotestul NU rulează. Așa putem importa modulul fără efecte secundare.
if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))
