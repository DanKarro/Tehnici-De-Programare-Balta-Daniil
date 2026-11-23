# Laborator: funcții, metode și importuri pe web
# Student: Nume Prenume

import time
from typing import Dict, List, Optional

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# ==========================================================================
# Partea 3: Scrierea propriilor funcții (exercițiile 21-34)
# ==========================================================================


# --- Exercițiile 21 + 23. fetch(url, timeout=10) ---------------------------
# Ex. 21: prima versiune era fetch(url). Ex. 23: am adăugat parametrul
# implicit `timeout`, deci apelurile vechi fetch(url) merg în continuare.
def fetch(url: str, timeout: int = TIMEOUT) -> requests.Response:
    """Descarcă url cu GET și returnează obiectul răspuns."""
    return requests.get(url, timeout=timeout)


response = fetch(BASE_URL)
print("Ex. 21: cod de stare =", response.status_code)
time.sleep(1)

response = fetch(BASE_URL)  # cu valoarea implicită (10 s)
print("Ex. 23: timeout implicit  ->", response.status_code)
time.sleep(1)
response = fetch(BASE_URL, timeout=3)  # timeout explicit
print("Ex. 23: timeout=3         ->", response.status_code)
time.sleep(1)


# --- Exercițiile 22 + 26. get_status(url) ----------------------------------
# Ex. 22: returnează doar codul de stare. Ex. 26: cu adnotări de tip.
def get_status(url: str) -> int:
    """Returnează codul de stare HTTP pentru adresa url."""
    return fetch(url).status_code


for path in ["/", "/robots.txt", "/sitemap.xml"]:
    print(f"Ex. 22: {path} -> {get_status(BASE_URL + path)}")
    time.sleep(1)


# --- Exercițiile 24 + 25. get_title(html) ----------------------------------
# Ex. 24: nicio operație de rețea; primește HTML, returnează titlul.
# Ex. 25: docstring, vizibil cu help(get_title).
def get_title(html: str) -> str:
    """Returnează textul dintre <title> și </title> sau un șir gol dacă lipsește.

    Parametri:
        html: codul HTML al paginii, ca șir de caractere.
    """
    start = html.find("<title>")
    end = html.find("</title>")
    if start == -1 or end == -1:
        return ""
    return html[start + len("<title>"):end].strip()


print("Ex. 24: titlu =", get_title(fetch(BASE_URL).text))
print("Ex. 24: get_title pe text scris de mine =", get_title("<title> Test </title>"))
help(get_title)  # Ex. 25
time.sleep(1)

# --- Exercițiul 26. Adnotările de tip nu opresc nimic ----------------------
# Adnotările (url: str, -> int) sunt doar documentație pentru oameni și
# pentru unelte (mypy, editorul). Python NU le verifică la rulare.
try:
    get_status(123)  # nu e un str, dar Python nu ne oprește la apel
except requests.RequestException as error:
    # Eroarea vine din requests (MissingSchema), nu din adnotare.
    print("Ex. 26: get_status(123) a eșuat în requests:", type(error).__name__)


# --- Exercițiul 27. Fără opriri neașteptate --------------------------------
def page_exists(url: str) -> bool:
    """Returnează True dacă pagina răspunde cu cod < 400, altfel False (fără excepții)."""
    try:
        return fetch(url).ok
    except requests.RequestException:
        return False


print("Ex. 27: page_exists(BASE_URL) =", page_exists(BASE_URL))
time.sleep(1)
print("Ex. 27: page_exists(domeniu inexistent) =",
      page_exists("https://this-domain-does-not-exist.invalid"))
time.sleep(1)


# --- Exercițiul 28. Returnarea unui dicționar ------------------------------
def check_paths(base: str, paths: List[str]) -> Dict[str, Optional[int]]:
    """Returnează un dicționar {cale: cod_de_stare} (None dacă cererea eșuează)."""
    results = {}
    for i, path in enumerate(paths):
        if i > 0:
            time.sleep(1)  # pauză între cereri
        try:
            results[path] = get_status(base + path)
        except requests.RequestException:
            results[path] = None
    return results


print("Ex. 28:", check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))
time.sleep(1)


# --- Exercițiul 29. Argumente cu nume --------------------------------------
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului `name` sau `default` dacă acesta lipsește."""
    return fetch(url).headers.get(name, default)


print("Ex. 29: Server =", get_header(BASE_URL, name="Server"))
time.sleep(1)


# --- Exercițiul 30. Antete de securitate -----------------------------------
SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def security_headers(url: str) -> Dict[str, bool]:
    """Returnează {antet: True/False} după cum cele 5 antete de securitate sunt prezente."""
    headers = fetch(url).headers
    return {name: name in headers for name in SECURITY_HEADERS}


results = security_headers(BASE_URL)
for header, present in results.items():
    print(f"Ex. 30: {header:28} {present}")


# --- Exercițiul 31. Funcții care apelează funcții --------------------------
def score_headers(results: Dict[str, bool]) -> str:
    """Primește dicționarul din security_headers() și returnează un scor, ex. '3/5'."""
    return f"{sum(results.values())}/{len(results)}"


print("Ex. 31: scor =", score_headers(results))
# Apelul combinat cere o nouă cerere la server, deci facem pauză înainte:
time.sleep(1)
print("Ex. 31: scor (apel combinat) =", score_headers(security_headers(BASE_URL)))
time.sleep(1)


# --- Exercițiul 32. Două funcții, o sarcină --------------------------------
def fetch_robots(base: str) -> Optional[str]:
    """Returnează textul din /robots.txt sau None dacă fișierul lipsește."""
    try:
        response = fetch(base + "/robots.txt")
    except requests.RequestException:
        return None
    return response.text if response.ok else None


def disallowed_paths(robots_text: Optional[str]) -> List[str]:
    """Returnează lista valorilor `Disallow:` din robots.txt (listă goală dacă primește None)."""
    if not robots_text:
        return []
    paths = []
    for line in robots_text.splitlines():
        line = line.split("#", 1)[0].strip()  # ignorăm comentariile
        if line.lower().startswith("disallow:"):
            value = line.split(":", 1)[1].strip()
            if value:  # "Disallow:" fără valoare nu interzice nimic
                paths.append(value)
    return paths


print("Ex. 32: cu None ->", disallowed_paths(None))
print("Ex. 32: text de test ->", disallowed_paths("User-agent: *\nDisallow: /admin\nDisallow: /private  # secret\nDisallow:"))
print("Ex. 32: site real ->", disallowed_paths(fetch_robots(BASE_URL)))
time.sleep(1)


# --- Exercițiul 33. Oricâte argumente --------------------------------------
def response_times(*urls: str) -> Dict[str, Optional[float]]:
    """Returnează {url: secunde} pentru oricâte adrese primește (None dacă eșuează)."""
    times = {}
    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(1)
        start = time.perf_counter()
        try:
            fetch(url)
            times[url] = round(time.perf_counter() - start, 3)
        except requests.RequestException:
            times[url] = None
    return times


print("Ex. 33:", response_times(BASE_URL, BASE_URL + "/robots.txt"))


# --- Exercițiul 34. Argumente cu nume colectate ----------------------------
def log(message: str, **details) -> None:
    """Afișează mesajul urmat de fiecare detaliu, sub forma `mesaj | cheie=valoare`."""
    parts = [message] + [f"{key}={value}" for key, value in details.items()]
    print(" | ".join(parts))


log("verificat", url=BASE_URL, status=200)

# ==========================================================================
# Verificați-vă: print() vs return
# ==========================================================================
# print() doar AFIȘEAZĂ valoarea pe ecran; codul care a apelat funcția nu o
# poate folosi mai departe (funcția returnează None).
# return trimite valoarea ÎNAPOI către cel care a apelat funcția, care o poate
# salva într-o variabilă, o poate transmite altei funcții (ex. score_headers(
# security_headers(url))) sau o poate testa. De aceea funcțiile utile
# returnează valori, iar afișarea se face la final, separat.
