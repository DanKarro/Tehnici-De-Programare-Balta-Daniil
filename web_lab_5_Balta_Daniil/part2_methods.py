# Laborator: funcții, metode și importuri pe web
# Student: Balta Daniil

import requests
import time

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10

try:
    # Exercițiul 9
    response = requests.get(BASE_URL, timeout=TIMEOUT)
    print("Ex. 9 - status_code:", response.status_code)  # atribut
    print("ok:", response.ok)                            # atribut
    print("url:", response.url)                          # atribut
    print("encoding:", response.encoding)                # atribut

    # Exercițiul 10
    response.raise_for_status()  # metodă
    try:
        missing = requests.get(BASE_URL + "/this-page-does-not-exist", timeout=TIMEOUT)
        missing.raise_for_status()
    except requests.HTTPError:
        print("Ex. 10 - Pagina solicitată nu a fost găsită sau serverul a refuzat cererea.")

    # Exercițiul 11
    print("Ex. 11 - antete:")
    for name, value in response.headers.items():
        print(f"{name}: {value}")

    # Exercițiul 12
    print("Ex. 12 - Server:", response.headers.get("Server", "lipsește"))
    print("Content-Type:", response.headers.get("Content-Type", "lipsește"))
    print("content-type:", response.headers.get("content-type", "lipsește"))
    # Antetele HTTP nu țin cont de majuscule/minuscule în requests.

    # Exercițiul 13
    print("Ex. 13 - apariții cyber:", response.text.lower().count("cyber"))
    # lower() produce un șir nou; count() se aplică acelui șir rezultat.

    # Exercițiul 14
    html = response.text
    start = html.find("<title>")
    end = html.find("</title>")
    if start != -1 and end != -1 and end >= start:
        title = html[start + len("<title>"):end].strip()
    else:
        title = "Titlu negăsit"
    print("Ex. 14 - titlu:", title)

    # Exercițiul 15
    lines = html.splitlines()
    print("Ex. 15 - număr linii:", len(lines))
    print("Lungimea celei mai lungi linii:", len(max(lines, key=len)) if lines else 0)

    # Exercițiul 16
    if response.url.startswith("https://"):
        print("Ex. 16 - Conexiune securizată")
    else:
        print("Ex. 16 - Conexiune nesecurizată")

    # Exercițiul 17
    time.sleep(1)
    redirect_response = requests.get("http://cybercor.org", timeout=TIMEOUT)
    print("Ex. 17 - redirecționări:")
    for item in redirect_response.history:
        print(item.status_code, item.url)
    print("URL final:", redirect_response.url)

    # Exercițiul 18
    time.sleep(1)
    head_response = requests.head(BASE_URL, timeout=TIMEOUT)
    get_response = requests.get(BASE_URL, timeout=TIMEOUT)
    print("Ex. 18 - HEAD bytes:", len(head_response.content))
    print("GET bytes:", len(get_response.content))
    # HEAD transmite antetele fără corpul paginii; GET descarcă și corpul.

    # Exercițiul 19
    if response.cookies:
        for cookie in response.cookies:
            print("Ex. 19 - cookie:", cookie.name, "secure:", cookie.secure)
    else:
        print("Ex. 19 - Niciun cookie setat")

    # Exercițiul 20 - antet personalizat este verificat pe httpbin.org
    session = requests.Session()
    session.headers.update({"User-Agent": "WebLab-Balta-Daniil"})
    echo_response = session.get(ECHO_URL + "/headers", timeout=TIMEOUT)
    echo_response.raise_for_status()
    echo_headers = echo_response.json().get("headers", {})
    print("Ex. 20 - User-Agent trimis:", echo_headers.get("User-Agent", "nu a fost găsit"))
except requests.RequestException as error:
    print("Eroare de rețea:", error)
