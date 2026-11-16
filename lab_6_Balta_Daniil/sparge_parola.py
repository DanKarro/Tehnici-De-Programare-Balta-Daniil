"""
sparge_parola.py

Ruleaza din radacina proiectului tau (acolo unde e si arsenal/):
    python3 sparge_parola.py

Citeste hash-ul din probe/hashuri.txt si incearca sa-l sparga
cu probe/wordlist.txt. Daca wordlist-ul are alt nume, schimba
WORDLIST mai jos.
"""
from arsenal.forensics.decode import sparge_hash, identifica_hash

HASHURI = "probe/hashuri.txt"
WORDLIST = "probe/wordlist.txt"  # schimba aici daca se numeste altfel

tinta = open(HASHURI).readline().strip()
print("hash:", tinta)
print("lungime:", len(tinta), "-> algoritm:", identifica_hash(tinta))

parola = sparge_hash(tinta, WORDLIST)
if parola:
    print("parola gasita:", parola)
else:
    print("nu s-a gasit nicio parola in", WORDLIST, "care sa dea acest hash")
