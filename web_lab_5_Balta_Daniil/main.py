# Laborator: funcții, metode și importuri pe web
# Student: Balta Daniil

import argparse
from webtools import (
    DEFAULT_HEADERS,
    get_title,
    security_headers,
    fetch,
    site_report,
    save_paths_csv,
)

def main():
    """Citește URL-ul din linia de comandă și generează rapoartele."""
    parser = argparse.ArgumentParser(description="Generează un raport pentru un site web.")
    parser.add_argument("url", help="URL-ul site-ului de verificat")
    args = parser.parse_args()

    # Dacă main.py ar defini propria funcție get_title, aceasta ar avea prioritate
    # în apelurile locale cu acel nume și ar putea ascunde funcția importată.
    print("Antete implicite:", DEFAULT_HEADERS)
    try:
        response = fetch(args.url)
        print("Titlu prin import:", get_title(response.text))
        print("Antete de securitate:", security_headers(args.url))
        save_paths_csv(args.url, "report.csv")
        site_report(args.url, "report.json")
    except Exception as error:
        print("Nu s-a putut genera raportul complet:", error)

if __name__ == "__main__":
    main()
