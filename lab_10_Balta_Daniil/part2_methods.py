# Laborator: funcții, metode și importuri pe web
# Student: Nume Prenume

import time

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# ==========================================================================
# Partea 2: Metode și atribute ale obiectelor web (exercițiile 9-20)
# ==========================================================================

response = requests.get(BASE_URL, timeout=TIMEOUT)

# --- Exercițiul 9. Elementele de bază ale răspunsului ----------------------
print("Ex. 9:")
print("  status_code:", response.status_code)  # atribut (valoare)
print("  ok:         ", response.ok)            # atribut (proprietate, fără paranteze)
print("  url:        ", response.url)           # atribut
print("  encoding:   ", response.encoding)      # atribut

# --- Exercițiul 10. Tratarea erorilor cu o metodă --------------------------
response.raise_for_status()  # pe pagina principală nu face nimic (cod 200)
print("Ex. 10: pagina principală este în regulă")

time.sleep(1)

try:
    missing = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
    missing.raise_for_status()  # metodă: ridică HTTPError dacă codul este 4xx/5xx
    print("Ex. 10: pagina a răspuns fără eroare:", missing.status_code)
except requests.HTTPError as error:
    print("Ex. 10: pagina nu a fost găsită, dar programul continuă.")
    print("        Detalii:", error)

time.sleep(1)

# --- Exercițiul 11. Toate antetele -----------------------------------------
print("Ex. 11: antetele răspunsului")
for name, value in response.headers.items():
    print(f"  {name}: {value}")

# --- Exercițiul 12. Metode de dicționar ------------------------------------
print("Ex. 12:")
print("  Server:      ", response.headers.get("Server", "lipsește"))
print("  Content-Type:", response.headers.get("Content-Type", "lipsește"))
print("  content-type:", response.headers.get("content-type", "lipsește"))
# Observație: și cu litere mici obținem aceeași valoare, pentru că
# response.headers este un CaseInsensitiveDict: numele antetelor nu țin
# cont de majuscule (așa cere standardul HTTP). Un dict obișnuit ar fi
# returnat "lipsește" pentru "content-type".

# --- Exercițiul 13. Înlănțuirea metodelor de șir ---------------------------
count = response.text.lower().count("cyber")
print("Ex. 13: cuvântul 'cyber' apare de", count, "ori")
# Putem înlănțui .lower() și .count() pentru că .lower() returnează un șir
# nou (str), iar orice str are metoda .count(). Fiecare metodă lucrează pe
# rezultatul celei dinainte.

# --- Exercițiul 14. Găsirea titlului ---------------------------------------
html = response.text
start = html.find("<title>")
end = html.find("</title>")
if start == -1 or end == -1:
    print("Ex. 14: pagina nu are tag <title>")
else:
    start += len("<title>")
    print("Ex. 14: titlul paginii =", html[start:end].strip())

# --- Exercițiul 15. Numărarea liniilor -------------------------------------
lines = html.splitlines()
print("Ex. 15: număr de linii =", len(lines))
if lines:
    print("Ex. 15: lungimea celei mai lungi linii =", len(max(lines, key=len)))

# --- Exercițiul 16. Verificarea HTTPS --------------------------------------
if response.url.startswith("https://"):
    print("Ex. 16: Conexiune securizată")
else:
    print("Ex. 16: Conexiune nesecurizată")

# --- Exercițiul 17. Urmărirea redirecționărilor ----------------------------
r = requests.get("http://cybercor.org", timeout=TIMEOUT)
print("Ex. 17: redirecționări pornind de la http://cybercor.org")
for hop in r.history:
    print(f"  {hop.status_code} -> {hop.url}")
print("  URL final:", r.url)

time.sleep(1)

# --- Exercițiul 18. HEAD versus GET ----------------------------------------
head_response = requests.head(BASE_URL, timeout=TIMEOUT)
time.sleep(1)
get_response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Ex. 18: len(content) HEAD =", len(head_response.content))
print("Ex. 18: len(content) GET  =", len(get_response.content))
# HEAD cere serverului doar antetele, fără corp, deci content este gol (0).
# GET returnează și corpul (codul HTML), deci content are mii de octeți.
# HEAD e util când vrem doar să verificăm o pagină fără s-o descărcăm.

time.sleep(1)

# --- Exercițiul 19. Cookie-uri ---------------------------------------------
print("Ex. 19: cookie-uri")
found_cookie = False
for cookie in response.cookies:
    found_cookie = True
    print(f"  {cookie.name} (secure={cookie.secure})")
if not found_cookie:
    print("  Niciun cookie setat")

# --- Exercițiul 20. Sesiuni ------------------------------------------------
session = requests.Session()
# User-Agent doar cu caractere ASCII; înlocuiți cu numele vostru.
session.headers.update({"User-Agent": "WebLab-NumePrenume"})
echo = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)
sent_headers = echo.json()["headers"]
print("Ex. 20: User-Agent primit de server =", sent_headers.get("User-Agent"))

# ==========================================================================
# Verificați-vă: response.text vs response.json()
# ==========================================================================
# response.text este un ATRIBUT (mai exact o proprietate): doar citim o
# valoare, deci nu are paranteze.
# response.json() este o METODĂ: execută o acțiune (parsează corpul ca JSON
# și construiește un dicționar/o listă), deci se apelează cu paranteze.
