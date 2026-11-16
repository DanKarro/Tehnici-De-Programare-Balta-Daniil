# Laborator: funcții, metode și importuri pe web
# Student: Balta Daniil

import csv
import hashlib
import json
import re
import socket
import ssl
import time
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests

TIMEOUT = 10
DEFAULT_HEADERS = {"User-Agent": "WebLab-Balta-Daniil"}
SECURITY_HEADER_NAMES = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]

def fetch(url: str, timeout: int = TIMEOUT):
    """Returnează răspunsul HTTP pentru URL-ul dat."""
    return requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)

def get_status(url: str) -> int:
    """Returnează codul de stare HTTP."""
    return fetch(url).status_code

def get_title(html: str) -> str:
    """Extrage titlul HTML dintre etichetele title."""
    start = html.lower().find("<title>")
    end = html.lower().find("</title>")
    if start == -1 or end == -1 or end < start:
        return ""
    return html[start + len("<title>"):end].strip()

def security_headers(url: str) -> dict:
    """Returnează True/False pentru prezența fiecărui antet de securitate."""
    response = fetch(url)
    return {name: name in response.headers for name in SECURITY_HEADER_NAMES}

def score_headers(results: dict) -> str:
    """Returnează numărul antetelor prezente raportat la numărul verificat."""
    return f"{sum(bool(value) for value in results.values())}/{len(results)}"

def check_paths(base: str, paths: list) -> dict:
    """Verifică doar căile specificate și returnează codurile lor de stare."""
    results = {}
    for index, path in enumerate(paths):
        if index:
            time.sleep(1)
        url = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
        try:
            results[path] = fetch(url).status_code
        except requests.RequestException:
            results[path] = None
    return results

def fetch_robots(base: str):
    """Returnează textul robots.txt sau None dacă nu este disponibil."""
    try:
        response = fetch(urljoin(base.rstrip("/") + "/", "robots.txt"))
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return None

def disallowed_paths(robots_text):
    """Extrage valorile Disallow din robots.txt; None produce o listă goală."""
    if robots_text is None:
        return []
    result = []
    for line in robots_text.splitlines():
        line = line.strip()
        if line.lower().startswith("disallow:"):
            result.append(line.split(":", 1)[1].strip())
    return result

def extract_links(html: str) -> list:
    """Extrage legăturile href fără duplicate, păstrând ordinea."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))

def split_links(links: list, domain: str) -> tuple:
    """Împarte legăturile în interne și externe după domeniu."""
    internal, external = [], []
    normalized_domain = domain.lower().removeprefix("www.")
    base = "https://" + domain
    for link in links:
        absolute = urljoin(base + "/", link)
        host = urlparse(absolute).netloc.lower().removeprefix("www.")
        (internal if host == normalized_domain else external).append(link)
    return internal, external

class ImageFinder(HTMLParser):
    """Colectează atributul src al fiecărui tag img."""
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Colectează src când tag-ul este img."""
        if tag.lower() == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)

def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 a conținutului descărcat."""
    response = fetch(url)
    return hashlib.sha256(response.content).hexdigest()

def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 a domeniului."""
    return socket.gethostbyname(hostname)

def cert_days_left(hostname: str) -> int:
    """Returnează numărul de zile până la expirarea certificatului TLS."""
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            certificate = secure_sock.getpeercert()
    expiry = ssl.cert_time_to_seconds(certificate["notAfter"])
    return int((expiry - time.time()) // 86400)

def site_report(url: str, json_filename: str = "report.json") -> dict:
    """Colectează informațiile cerute și salvează raportul în JSON."""
    response = fetch(url)
    html = response.text
    parsed = urlparse(response.url)
    hostname = parsed.hostname or urlparse(url).hostname
    links = extract_links(html)
    internal_links, external_links = split_links(links, hostname or "")
    security = security_headers(response.url)

    # Exercițiul cere lanțul de redirecționări pornind de la HTTP.
    http_url = urljoin(url, "/")
    if http_url.startswith("https://"):
        http_url = "http://" + http_url[len("https://"):]
    redirect_response = requests.get(
        http_url, timeout=TIMEOUT, headers=DEFAULT_HEADERS, allow_redirects=True
    )
    redirects = [
        {"status": item.status_code, "url": item.url}
        for item in redirect_response.history
    ]
    redirects.append({"status": redirect_response.status_code, "url": redirect_response.url})

    robots_text = fetch_robots(url)
    report = {
        "requested_url": url,
        "status_code": response.status_code,
        "final_url": response.url,
        "title": get_title(html),
        "ip_address": resolve(hostname) if hostname else None,
        "redirect_chain": redirects,
        "security_headers": security,
        "security_score": score_headers(security),
        "certificate_days_left": cert_days_left(hostname) if hostname else None,
        "internal_links_count": len(internal_links),
        "external_links_count": len(external_links),
        "disallowed_paths": disallowed_paths(robots_text),
        "checked_at": datetime.now().isoformat(),
    }

    print(f"=== Raport site: {url} ===")
    print("Cod de stare:     ", report["status_code"])
    print("URL final:        ", report["final_url"])
    print("Titlu:            ", report["title"] or "Titlu negăsit")
    print("Adresă IP:        ", report["ip_address"])
    print("Redirecționări:   ", " -> ".join(
        f'{item["status"]} {item["url"]}' for item in redirects
    ))
    print("Scor securitate:  ", report["security_score"])
    print("Certificat:       ", report["certificate_days_left"], "zile rămase")
    print("Legături:         ", report["internal_links_count"], "interne,",
          report["external_links_count"], "externe")
    print("Căi interzise:    ", ", ".join(report["disallowed_paths"]) or "niciuna indicată")

    with open(json_filename, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print("Salvat în", json_filename)
    return report

def save_paths_csv(base: str, filename: str = "report.csv") -> dict:
    """Salvează codurile pentru căile specificate în report.csv."""
    paths = ["/", "/robots.txt", "/sitemap.xml"]
    results = check_paths(base, paths)
    checked_at = datetime.now().isoformat()
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["path", "status", "checked_at"])
        for path, status in results.items():
            writer.writerow([path, status, checked_at])
    return results

if __name__ == "__main__":
    print("Autotest:", get_status("https://cybercor.org"))
