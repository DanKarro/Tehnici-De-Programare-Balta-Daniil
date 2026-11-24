"""Lab 10 - Lucrarea B: detector de brute force cu prag reglabil si raport JSON."""
import argparse
import json
from collections import Counter

from .parse_auth import citeste_esecuri, pe_ip


def suspecti(counts, prag=10):
    """Intoarce [(ip, n), ...] cu n >= prag, sortat descrescator dupa n."""
    if prag < 1:
        raise ValueError(f"prag invalid: {prag} (cel putin 1)")
    return [(ip, n) for ip, n in Counter(counts).most_common() if n >= prag]


def main():
    p = argparse.ArgumentParser(description="Detector de brute force din auth.log")
    p.add_argument("log")
    p.add_argument("--prag", type=int, default=10)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    esecuri = citeste_esecuri(a.log)
    counts = pe_ip(esecuri)
    try:
        sus = suspecti(counts, a.prag)
    except ValueError as e:
        p.error(str(e))

    if a.json:
        raport = {
            "esecuri": len(esecuri),
            "pe_ip": dict(counts.most_common()),
            "suspecti": [{"ip": ip, "n": n} for ip, n in sus],
        }
        print(json.dumps(raport, indent=2))
    else:
        print("Esecuri de autentificare:", len(esecuri))
        for ip, n in counts.most_common():
            print(f"  {ip}: {n}")
        print(f"Suspecti (prag {a.prag}):")
        for ip, n in sus:
            print(f"  {ip} ({n} incercari) BRUTE FORCE")


if __name__ == "__main__":
    main()
