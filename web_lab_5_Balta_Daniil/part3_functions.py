# Laborator: funcții, metode și importuri pe web
# Student: Balta Daniil

import requests
import time

BASE_URL = "https://cybercor.org"
TIMEOUT = 10

def fetch(url: str, timeout: int = 10):
    """Returnează obiectul răspuns pentru adresa indicată."""
    return requests.get(url, timeout=timeout)

def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code

def get_title(html: str) -> str:
    """Extrage textul dintre etichetele title din HTML."""
    start = html.find("<title>")
    end = html.find("</title>")
    if start == -1 or end == -1 or end < start:
        return ""
    return html[start + len("<title>"):end].strip()

def page_exists(url: str) -> bool:
    """Returnează True dacă cererea reușește și False dacă apare o eroare de cerere."""
    try:
        return requests.get(url, timeout=TIMEOUT).status_code == 200
    except requests.RequestException:
        return False

def check_paths(base: str, paths: list) -> dict:
    """Returnează codul de stare pentru fiecare cale din listă."""
    results = {}
    for index, path in enumerate(paths):
        if index:
            time.sleep(1)
        url = base.rstrip("/") + "/" + path.lstrip("/")
        try:
            results[path] = requests.get(url, timeout=TIMEOUT).status_code
        except requests.RequestException:
            results[path] = None
    return results

def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea unui antet sau valoarea implicită."""
    response = requests.get(url, timeout=TIMEOUT)
    return response.headers.get(name, default)

def security_headers(url: str) -> dict:
    """Verifică prezența celor cinci antete de securitate cerute."""
    response = requests.get(url, timeout=TIMEOUT)
    names = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
    ]
    return {name: name in response.headers for name in names}

def score_headers(results: dict) -> str:
    """Returnează scorul antetelor prezente, de exemplu 3/5."""
    return f"{sum(bool(value) for value in results.values())}/{len(results)}"

def fetch_robots(base: str):
    """Returnează textul robots.txt sau None dacă nu poate fi citit."""
    try:
        response = requests.get(base.rstrip("/") + "/robots.txt", timeout=TIMEOUT)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return None

def disallowed_paths(robots_text):
    """Extrage valorile liniilor Disallow:; pentru None returnează o listă goală."""
    if robots_text is None:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.strip()
        if line.lower().startswith("disallow:"):
            paths.append(line.split(":", 1)[1].strip())
    return paths

def response_times(*urls: str) -> dict:
    """Returnează durata cererii pentru fiecare URL primit."""
    results = {}
    for index, url in enumerate(urls):
        if index:
            time.sleep(1)
        start = time.perf_counter()
        try:
            requests.get(url, timeout=TIMEOUT)
            results[url] = time.perf_counter() - start
        except requests.RequestException:
            results[url] = None
    return results

def log(message: str, **details) -> None:
    """Afișează un mesaj urmat de detaliile primite ca argumente cu nume."""
    suffix = " | ".join(f"{key}={value}" for key, value in details.items())
    print(f"{message} | {suffix}" if suffix else message)

if __name__ == "__main__":
    print("Ex. 21 - fetch:", fetch(BASE_URL).status_code)
    print("Ex. 22 - statusuri:")
    for path in ["/", "/robots.txt", "/sitemap.xml"]:
        print(path, get_status(BASE_URL.rstrip("/") + path))
        time.sleep(1)
    print("Ex. 23 - timeout implicit:", fetch(BASE_URL).status_code)
    print("Ex. 23 - timeout=3:", fetch(BASE_URL, timeout=3).status_code)
    print("Ex. 24 - titlu:", get_title(fetch(BASE_URL).text))
    print("Ex. 25 - docstring:", get_title.__doc__)
    print("Ex. 26 - adnotările nu verifică automat tipurile la rulare.")
    try:
        print(get_status(123))  # adnotarea nu oprește apelul; requests va raporta eroarea.
    except (requests.RequestException, TypeError, AttributeError) as error:
        print("Apelul cu 123 a eșuat:", error)
    print("Ex. 27 - page_exists:", page_exists("https://this-domain-does-not-exist.invalid"))
    print("Ex. 28 - căi:", check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))
    print("Ex. 29 - Server:", get_header(BASE_URL, name="Server"))
    print("Ex. 30/31 - scor antete:", score_headers(security_headers(BASE_URL)))
    print("Ex. 32 - căi Disallow:", disallowed_paths(fetch_robots(BASE_URL)))
    print("Ex. 33 - durate:", response_times(BASE_URL, BASE_URL + "/robots.txt"))
    log("verificat", url=BASE_URL, status=get_status(BASE_URL))
