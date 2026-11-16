# Laboratorul 6 — fișiere gata de pus în `tehnici-prog-<nume>`

Tot ce ai nevoie pentru Lucrarea A și Lucrarea B, scris urmând exact pașii din
suportul de curs. Toate funcțiile au fost testate și rulează corect (vezi
`raport.md` pentru rezultatele obținute).

## Structură

```
arsenal/forensics/decode.py   Lucrarea A (A1-A7): decoderul universal
teste/test_decode.py          testul cerut la A7 (stil pytest)
forensics.py                  Lucrarea B1-B4: magic bytes, strings, EXIF/GPS, carving
stego.py                      Lucrarea B5-B6: ascunde/dezvăluie mesaj LSB
probe/pregateste_demo.py      generator de fixturi DE TEST, nu scriptul oficial
raport.md                     șablon de raport, completat cu rezultatele mele de test
```

## Important — despre `probe/`

Nu am avut acces la `probe/pregateste.py` (scriptul oficial vine din depozitul
de start al laboratorului, pe care nu l-am primit). Ca să pot scrie și testa
cod care chiar rulează, am scris `probe/pregateste_demo.py`, un generator
echivalent ca idee (aceleași cinci fișiere: mesaj în straturi, XOR, hash,
poză cu EXIF/GPS, poză cu arhivă ascunsă), dar cu valori diferite de ale
voastre din laborator.

**Înainte să predai:**
1. Șterge `probe/pregateste_demo.py` și fixturile mele din `probe/`.
2. Rulează `python probe/pregateste.py` (scriptul oficial) ca să-ți creezi
   propriile fișiere în `probe/`.
3. Rulează din nou `decode.py`, `forensics.py`, `stego.py` pe fixturile tale
   reale și actualizează `raport.md` cu valorile tale (cheia XOR, parola
   spartă, coordonatele GPS, mesajul LSB) — nu cu ale mele.
4. `git add . && git commit -m "Lab 6: decoder universal + forensics si stego" && git push`

## Cum rulezi fiecare piesă

```bash
# Lucrarea A — decodezi un sir direct din linia de comanda:
python arsenal/forensics/decode.py "<sirul tau codat>"

# sau un fisier (ex. xor.bin), cu --fisier:
python arsenal/forensics/decode.py probe/xor.bin --fisier

# testul (daca ai pytest instalat):
pytest teste/test_decode.py -v

# Lucrarea B — forensics pe fisiere (magic bytes, strings, EXIF/GPS, carving):
python forensics.py

# Lucrarea B — steganografie LSB:
python stego.py ascunde probe/foto.jpg "mesajul tau" 
python stego.py dezvaluie stego.png
```

## Ce am verificat local (vezi `raport.md`)

- **A2-A4**: `ghici_strat` recunoaște base64/hex/url după alfabet;
  `desfa_straturi` desface corect un mesaj codat în două straturi suprapuse
  (base64 peste hex peste text).
- **A5**: `sparge_xor` încearcă toate cele 256 de chei; am adăugat un scor de
  plauzibilitate (proporția de litere+spații) ca să aleagă automat cel mai
  bun candidat, fiindcă pe mesaje scurte filtrul simplu (32-126) lasă să
  treacă mai mulți candidați "citibili" dar greșiți.
- **A6**: `sparge_hash` identifică algoritmul după lungime (32/40/64) și
  sparge prin dicționar.
- **B1-B4**: `tip_real` recunoaște JPEG/PNG după semnătură; `scoate_strings`
  scoate textul din binar; `citeste_gps` convertește corect blocul GPS în
  grade zecimale; `extrage_ascuns` găsește și salvează arhiva ZIP lipită la
  coada unui PNG (am verificat că arhiva extrasă chiar se deschide).
- **B5-B6**: mesajul ascuns cu `ascunde()` iese identic la `dezvaluie()`.
