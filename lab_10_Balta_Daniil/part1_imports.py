# Laborator: funcții, metode și importuri pe web
# Student: Nume Prenume

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# ==========================================================================
# Partea 1: Importuri (exercițiile 1-8)
# ==========================================================================

# --- Exercițiul 1. Primul import -------------------------------------------
import requests
import urllib.request

print("Ex. 1: versiunea requests =", requests.__version__)

# De ce a avut requests nevoie de `pip install`, iar urllib nu?
# urllib face parte din biblioteca standard: vine instalat odată cu Python.
# requests este o bibliotecă externă (terță parte), scrisă de altcineva și
# publicată pe PyPI, așa că trebuie descărcată și instalată separat cu pip.

import time

time.sleep(1)

# --- Exercițiul 2. Două stiluri de import ----------------------------------
# Stilul 1: import modul întreg
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Ex. 2 (import requests):      cod de stare =", response.status_code)

time.sleep(1)

# Stilul 2: import doar numele de care avem nevoie
from requests import get

response = get(BASE_URL, timeout=TIMEOUT)
print("Ex. 2 (from requests import): cod de stare =", response.status_code)

# Avantaj `import requests`: se vede mereu de unde vine funcția
# (requests.get), deci nu există confuzii și nu apar conflicte de nume.
# Avantaj `from requests import get`: codul e mai scurt, nu repetăm prefixul.

time.sleep(1)

# --- Exercițiul 3. Alias-uri -----------------------------------------------
import requests as rq

response = rq.get(BASE_URL, timeout=TIMEOUT)
print("Ex. 3: cod de stare cu alias =", response.status_code)

# Un alias face codul mai ușor de citit când numele e lung și apare des, iar
# aliasul este unul consacrat (import numpy as np, import pandas as pd).
# Îl face mai greu de citit când e inventat sau criptic (rq, r, x): cine
# citește codul trebuie să ghicească ce e în spatele lui.

time.sleep(1)

# --- Exercițiul 4. Doar biblioteca standard --------------------------------
# .read() returnează octeți (bytes); .decode("utf-8") îi face șir de caractere.
try:
    with urllib.request.urlopen(BASE_URL, timeout=TIMEOUT) as answer:
        print("Ex. 4: status =", answer.status)
        body = answer.read().decode("utf-8")
        print("Ex. 4: primele 200 de caractere:")
        print(body[:200])
except OSError as error:  # urllib.error.URLError / HTTPError sunt subclase de OSError
    print("Ex. 4: cererea a eșuat:", error)

time.sleep(1)

# --- Exercițiul 5. Priviți în interiorul unui modul ------------------------
print("Ex. 5: dir(requests) =")
print(dir(requests))

# Trei nume alese din rezultat:
#   requests.get        -> funcție   (type: function)
#   requests.Session    -> clasă     (type: type)
#   requests.exceptions -> modul     (type: module)
for name in ("get", "Session", "exceptions"):
    print(f"   {name}: {type(getattr(requests, name)).__name__}")

# --- Exercițiul 6. Citiți documentația -------------------------------------
help(requests.get)
# În documentație, requests.get(url, params=None, **kwargs) transmite kwargs
# către requests.request(), unde apare parametrul `timeout`: timpul maxim de
# așteptare în secunde. Îl folosim așa:
response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Ex. 6: cerere cu timeout =", TIMEOUT, "->", response.status_code)

time.sleep(1)

# --- Exercițiul 7. Cronometrarea unei cereri -------------------------------
start = time.perf_counter()
response = requests.get(BASE_URL, timeout=TIMEOUT)
measured = time.perf_counter() - start

print(f"Ex. 7: perf_counter       = {measured:.3f} s")
print(f"Ex. 7: response.elapsed   = {response.elapsed.total_seconds():.3f} s")
# perf_counter măsoară tot ce durează apelul (inclusiv citirea corpului
# și crearea obiectului), deci iese de obicei puțin mai mare.
# response.elapsed măsoară doar timpul de la trimiterea cererii până la
# primirea antetelor răspunsului.

# --- Exercițiul 8. Când un import eșuează ----------------------------------
try:
    import bs4
    print("Ex. 8: bs4 este instalat, versiunea", bs4.__version__)
except ImportError:
    print("Instalați modulul cu: pip install beautifulsoup4")

# ==========================================================================
# Verificați-vă: modul, pachet, bibliotecă
# ==========================================================================
# - Modul: un singur fișier .py (ex. webtools.py) pe care îl putem importa.
# - Pachet: un director care conține mai multe module (și un __init__.py);
#   ex. `requests` sau `urllib` (cu submodulele urllib.request, urllib.parse).
# - Bibliotecă: termen general, o colecție de cod reutilizabil care rezolvă
#   o categorie de probleme; poate fi un modul, un pachet sau mai multe pachete.
