# Laborator: funcții, metode și importuri pe web
# Student: Balta Daniil

import requests
import urllib.request
import time

BASE_URL = "https://cybercor.org"
TIMEOUT = 10

# Exercițiul 1
print("Ex. 1 - requests:", requests.__version__)
# requests este o bibliotecă externă instalată cu pip; urllib.request face parte din biblioteca standard Python.
print("urllib.request a fost importat.")

# Exercițiul 2
try:
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    print("Ex. 2 - requests.get:", response.status_code)
    # Avantaj: requests.get este explicit și ușor de recunoscut.
    from requests import get
    response2 = get(BASE_URL, timeout=TIMEOUT)
    print("Ex. 2 - from requests import get:", response2.status_code)
    # Avantaj: apelul get(...) este mai scurt; importul requests păstrează mai clar originea funcției.
except requests.RequestException as error:
    print("Cererea nu a reușit:", error)

# Exercițiul 3
import requests as rq
try:
    response = rq.get(BASE_URL, timeout=TIMEOUT)
    print("Ex. 3 - alias rq:", response.status_code)
    # Un alias scurt ajută la multe apeluri; unul neobișnuit poate face codul mai greu de înțeles.
except rq.RequestException as error:
    print("Cererea nu a reușit:", error)

# Exercițiul 4
try:
    with urllib.request.urlopen(BASE_URL, timeout=TIMEOUT) as response:
        body = response.read().decode("utf-8", errors="replace")
        print("Ex. 4 - status:", response.status)
        print("Primele 200 caractere:", body[:200])
except Exception as error:
    print("Cererea urllib nu a reușit:", error)

# Exercițiul 5
print("Ex. 5 - câteva nume din dir(requests):")
print(dir(requests))
# Exemple: get este funcție; Session este clasă; exceptions este modul/pachet de excepții.

# Exercițiul 6
help(requests.get)
try:
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    print("Ex. 6 - status folosind timeout:", response.status_code)
except requests.RequestException as error:
    print("Cererea nu a reușit:", error)

# Exercițiul 7
try:
    start = time.perf_counter()
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    elapsed = time.perf_counter() - start
    print("Ex. 7 - perf_counter:", round(elapsed, 4), "secunde")
    print("response.elapsed:", response.elapsed.total_seconds(), "secunde")
except requests.RequestException as error:
    print("Cererea nu a reușit:", error)

# Exercițiul 8
try:
    import bs4
    print("Ex. 8 - bs4 este instalat.")
except ImportError:
    print("Instalați modulul cu: pip install beautifulsoup4")
