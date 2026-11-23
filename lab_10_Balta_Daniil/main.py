# Laborator: funcții, metode și importuri pe web
# Student: Nume Prenume
#
# main.py - programul care importă modulul meu webtools (Partea 5).
# Rulare:  python main.py https://cybercor.org

import argparse

# Ex. 44: import de modul întreg; funcțiile se apelează cu prefixul webtools.
import webtools

# Ex. 45: import al unor nume anume, folosite fără prefix.
# Ex. 47: importăm și constanta DEFAULT_HEADERS.
#
# Ce s-ar întâmpla dacă main.py ar avea și o funcție proprie get_title?
# Numele get_title din main.py ar fi legat de funcția care apare ULTIMA în
# fișier: dacă `def get_title` vine după `from webtools import get_title`,
# funcția mea o înlocuiește pe cea din webtools (o "umbrește"); dacă importul
# vine după definiție, importul o înlocuiește pe a mea. Fără erori, doar un
# comportament surprinzător. De aceea folosim `import webtools` când riscăm
# conflicte de nume, sau un alias: `from webtools import get_title as wt_title`.
from webtools import DEFAULT_HEADERS, get_title, security_headers


def parse_args() -> argparse.Namespace:
    """Citește adresa site-ului din linia de comandă (ex. 48)."""
    parser = argparse.ArgumentParser(description="Raport despre un site web.")
    parser.add_argument("url", help="adresa site-ului, ex. https://cybercor.org")
    return parser.parse_args()


def main() -> None:
    """Rulează demonstrațiile din Partea 5 pentru adresa primită în linia de comandă."""
    args = parse_args()
    url = args.url  # ex. 48: URL-ul vine din linia de comandă, nu din BASE_URL

    # Ex. 44: apel prin prefixul modulului
    page = webtools.fetch(url)
    print("Titlu (webtools.get_title):", webtools.get_title(page.text))

    # Ex. 45: apel direct, fără prefix
    print("Titlu (get_title):         ", get_title(page.text))
    print("Antete de securitate:      ", security_headers(url, page))

    # Ex. 47: constanta importată
    print("DEFAULT_HEADERS:           ", DEFAULT_HEADERS)
    print()

    # Ex. 49: raport CSV cu rezultatul funcției check_paths()
    results = webtools.check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
    webtools.save_csv_report(results, "report.csv")
    print("Salvat în report.csv:", results)
    print()

    # Ex. 50: proiectul final
    webtools.site_report(url, "report.json")


if __name__ == "__main__":
    main()
