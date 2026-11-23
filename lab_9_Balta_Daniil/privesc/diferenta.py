"""diferenta.py - ce SUID a aparut fata de un sistem curat (diferenta de multimi)."""
import os

from arsenal.privesc.enum import citeste_linii, nume, GTFO

START = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start")


def cai(fisier):
    """Intoarce MULTIMEA cailor din fisier."""
    return set(citeste_linii(fisier))


def main():
    baza = cai(os.path.join(START, "baza_suid.txt"))
    acum = cai(os.path.join(START, "suid.txt"))
    print("baza:", len(baza), "acum:", len(acum))

    # B2: ce e in "acum" dar nu in "baza" = SUID nou
    noi = acum - baza
    print(len(noi), "SUID noi fata de sistemul curat")
    for c in sorted(noi):
        print(" ", c)

    # B3: dict comprehension (nume -> risc) + list comprehension cu if
    risc = {nume(c): ("mare" if nume(c) in GTFO else "normal") for c in noi}
    periculoase = [c for c in sorted(noi) if nume(c) in GTFO]
    print("periculoase NOI:", periculoase)
    return risc


if __name__ == "__main__":
    main()
