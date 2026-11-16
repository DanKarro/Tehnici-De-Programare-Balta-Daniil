# Laboratorul 6 — Informații invizibile: forensics și steganografie

> **De completat:** câmpurile marcate `[DE COMPLETAT]` trebuie umplute cu
> rezultatele tale reale înainte de predare — restul sunt deja rezultatele
> obținute pe fixturile tale (`probe/pregateste.py` oficial).

## Lucrarea A — Decoderul universal

**Ce ascundea `mesaj.txt` cu straturi:**
Șirul era codat `base64` peste `base64` peste `hex` peste text. Decoderul a
desfăcut straturile în ordine (`base64 -> base64 -> hex -> text`), oprindu-se
la mesajul clar: **`FLAG{straturi_de_encoding}`**.

**Cheia XOR găsită în `xor.bin`:**
Cheia de un octet a fost **128** (`0x80`). Textul clar a ieșit complet
citibil: `"Un singur octet tine tot secretul... gaseste-l! FLAG{xor_un_octet}"`.

**Parola spartă din `hashuri.txt`:**
Hash-ul avea 32 de caractere hex -> `md5`. Prin dicționar (`wordlist.txt`) am
găsit parola **`password`**.

## Lucrarea B — Forensics pe fișiere și mesaj ascuns

**Tipul real al fișierelor (magic bytes):**
- `probe/foto.jpg` -> semnătura JPEG (`ff d8 ff`), deci chiar e un JPEG.
- `probe/ascuns.png` -> semnătura PNG (`89 50 4e 47`).

**Ce am găsit în metadate (inclusiv GPS):**
EXIF conținea `Make = Apple`, `Model = iPhone 13`,
`DateTime = 2026:09:14 10:30:00`. Blocul GPS, convertit în grade zecimale:
**latitudine ≈ 47.0167, longitudine ≈ 28.8575**.

**Ce era în arhiva ascunsă:**
`probe/ascuns.png` avea o arhivă ZIP lipită la coadă, găsită la semnătura
`PK\x03\x04` (octetul 782). Chiar și `strings`, înainte de carving, scotea la
iveală indiciul (`secret.txtFLAG{ascuns_prin_carving}`, fiindcă arhiva nu era
comprimată). Arhiva extrasă conține `secret.txt`, cu textul **`FLAG{ascuns_prin_carving}`**
(vizibil chiar din rezultatul lui `strings`, fiindcă arhiva nu era
comprimată).

**Mesajul LSB ascuns și dezvăluit:** `[DE COMPLETAT]`
(rulează `python3 stego.py ascunde probe/foto.jpg "mesajul tau"` apoi
`python3 stego.py dezvaluie stego.png`)

---

## Pentru vârful sălii (opțional)

`probe/challenge.bin` și `probe/challenge_hint.txt` există în depozitul meu
— bonus-ul e disponibil, dar nu l-am rezolvat încă în acest raport.
Instrumentele de la Lucrarea A (recunoaștere strat, straturi multiple, XOR
brute force, identificare/spargere hash) acoperă exact ce ar trebui să fie
nevoie pentru el.

## Explicații cod

### `arsenal/forensics/decode.py` — decoderul universal (Lucrarea A)

#### `citibil(b)` — criteriul "arată a text"

```python
def citibil(b: bytes) -> bool:
    if not b:
        return False
    return all(32 <= c < 127 for c in b)
```

**Ce face:** primește octeți (`bytes`) și întoarce `True` doar dacă *toți*
octeții sunt în intervalul ASCII imprimabil (32 = spațiu, 126 = `~`). E
funcția de bază pe care se sprijină tot restul: orice decodare se validează
întrebând "rezultatul arată a text?".

**De ce așa:** `32 <= c < 127` este exact intervalul din suportul de curs
pentru "octeți imprimabili". Octeții de control (0-31) și cei peste 126 (unii
non-ASCII) nu sunt text normal, deci îi respingem.

#### `ghici_strat(s)` — recunoști stratul fără să decodezi

```python
def ghici_strat(s: str) -> str:
    if re.search(r"%[0-9A-Fa-f]{2}", s):
        return "url"
    if re.fullmatch(r"[0-9a-fA-F]+", s) and len(s) % 2 == 0:
        return "hex"
    if re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) and len(s) % 4 == 0:
        return "base64"
    return "necunoscut"
```

**Ce face:** se uită doar la *forma* șirului (ce caractere conține, ce
lungime are) și ghicește ce codare ar putea fi, fără să încerce nimic încă.

**De ce ordinea asta:** `url` e cel mai specific (conține `%xx`), deci-l
verific primul. `hex` e mai strict decât `base64` (doar 16 caractere permise,
`0-9a-f`, și lungime pară), deci-l verific al doilea — altfel un șir hex ar
fi clasificat greșit drept base64, pentru că alfabetul base64 include și
cifrele hex. `base64` e cel mai larg alfabet, deci rămâne ultimul.

#### `desfa(s)` — desfaci stratul recunoscut

```python
def desfa(s: str):
    strat = ghici_strat(s)
    try:
        if strat == "base64":
            return strat, base64.b64decode(s, validate=True)
        if strat == "hex":
            return strat, bytes.fromhex(s)
        if strat == "url":
            return strat, unquote(s).encode()
    except Exception:
        pass
    return "necunoscut", s.encode()
```

**Ce face:** pe baza stratului ghicit, alege funcția potrivită din
bibliotecă (`base64.b64decode`, `bytes.fromhex`, `urllib.parse.unquote`) și
întoarce `(strat, octeți_decodați)`.

**De ce `validate=True` la base64:** fără el, `b64decode` acceptă și șiruri
care nu sunt base64 valid și scoate gunoi tăcut. Cu `validate=True`, o
clasificare greșită a lui `ghici_strat` aruncă excepție, prinsă de `except`,
și ne întoarcem cu `"necunoscut"` în loc să afișăm un rezultat fals.

#### `desfa_straturi(s)` — straturi multiple, într-o buclă

```python
def desfa_straturi(s: str, pas_maxim: int = 8):
    istoric = []
    val = s
    strat, b = "necunoscut", s.encode()
    for _ in range(pas_maxim):
        strat, b = desfa(val)
        istoric.append(strat)
        if strat == "necunoscut":
            break
        try:
            val = b.decode()
        except UnicodeDecodeError:
            break
    return strat, b, istoric
```

**Ce face:** repetă `desfa()` cât timp mai recunoaște un strat nou, construind
un `istoric` al straturilor desfăcute (ex: `["base64", "base64", "hex"]`).

**De ce nu ne oprim doar la "citibil":** un rezultat poate fi *citibil* dar
tot o codare (ex: șirul hex `"617363756e73"` e perfect citibil ca text, dar
tot hex e). De-aia criteriul de oprire real e "`ghici_strat` nu mai
recunoaște nimic" (`strat == "necunoscut"`), nu doar `citibil(b)`.
`pas_maxim` există ca plasă de siguranță, să nu intrăm în buclă infinită pe
o intrare neașteptată.

#### `sparge_xor(date)` — forța brută pe cheia XOR

```python
def sparge_xor(date: bytes):
    candidati = []
    for k in range(256):
        clar = bytes(c ^ k for c in date)
        if citibil(clar):
            candidati.append((k, clar))
    candidati.sort(key=lambda kc: _scor_plauzibilitate(kc[1]), reverse=True)
    return candidati
```

**Ce face:** o cheie XOR de un octet are doar 256 de valori posibile, deci le
încercăm pe toate (`for k in range(256)`), facem XOR pe fiecare octet din
mesaj cu aceeași cheie, și păstrăm doar rezultatele complet citibile.

**De ce sortăm după un scor:** pe mesaje scurte, filtrul simplu (`citibil`)
lasă să treacă *mai mulți* candidați care arată "suficient de citibil" din
întâmplare, nu doar cel corect. `_scor_plauzibilitate` calculează ce procent
din octeți sunt litere sau spații — textul normal e aproape numai din astea
— și sortăm descrescător, ca primul candidat să fie, de obicei, cel corect.

#### `identifica_hash(h)` și `sparge_hash(tinta, wordlist)` — amprente

```python
_LUNGIME_ALGORITM = {32: "md5", 40: "sha1", 64: "sha256"}

def identifica_hash(h: str) -> str:
    return _LUNGIME_ALGORITM.get(len(h.strip()), "necunoscut")

def sparge_hash(tinta: str, cale_wordlist: str):
    tinta = tinta.strip()
    algoritm = identifica_hash(tinta)
    if algoritm == "necunoscut":
        return None
    func = getattr(hashlib, algoritm)
    with open(cale_wordlist, encoding="latin1") as f:
        for cuv in f:
            cuv = cuv.strip()
            if not cuv:
                continue
            if func(cuv.encode()).hexdigest() == tinta:
                return cuv
    return None
```

**Ce face `identifica_hash`:** numără caracterele hex ale amprentei (32/40/64)
și ghicește algoritmul — exact ideea din curs: lungimea fixă a hash-ului
trădează funcția folosită.

**Ce face `sparge_hash`:** NU inversează hash-ul (nu se poate). În schimb,
hashuiește fiecare cuvânt din `wordlist` cu algoritmul identificat
(`getattr(hashlib, algoritm)` ia dinamic `hashlib.md5`, `hashlib.sha1` sau
`hashlib.sha256`) și compară amprenta rezultată cu ținta. Când coincid, am
"spart" hash-ul — de fapt am ghicit intrarea, nu am decriptat nimic.

**De ce `encoding="latin1"` la citirea wordlist-ului:** fișierele de parole
scurse (ex. rockyou.txt) conțin uneori octeți care nu sunt UTF-8 valid;
`latin1` nu aruncă niciodată eroare la citire (fiecare octet are un
corespondent în latin1), exact ca în exemplul din suportul de curs.

### `forensics.py` — urme în fișiere (Lucrarea B1-B4)

#### `tip_real(cale)` — magic bytes

```python
SEMNATURI = {
    b"\x89PNG": "png",
    b"\xff\xd8\xff": "jpeg",
    b"%PDF": "pdf",
    b"PK\x03\x04": "zip/docx",
    b"\x7fELF": "elf",
}

def tip_real(cale: str) -> str:
    cap = open(cale, "rb").read(8)
    for semnatura, nume in SEMNATURI.items():
        if cap.startswith(semnatura):
            return nume
    return cap.hex()
```

**Ce face:** deschide fișierul în mod binar (`"rb"`), citește primii 8 octeți
și îi compară cu semnăturile cunoscute. Dacă niciuna nu se potrivește,
întoarce octeții ca hex, ca să poți căuta manual ce format e.

**De ce `"rb"` și nu doar `"r"`:** fără `"b"`, Python (sau sistemul de
operare) poate "traduce" anumiți octeți (de exemplu sfârșitul de linie),
stricând fișierul binar înainte să apuci să-l citești corect.

#### `scoate_strings(cale, lungime_minima=4)` — text citibil dintr-un binar

```python
def scoate_strings(cale: str, lungime_minima: int = 4):
    date = open(cale, "rb").read()
    tipar = ("[ -~]{%d,}" % lungime_minima).encode()
    return [m.decode() for m in re.findall(tipar, date)]
```

**Ce face:** citește tot fișierul ca octeți, apoi caută cu o expresie
regulată *pe octeți* (observă `tipar` e `bytes`, nu `str`) toate secvențele
de minim 4 caractere din intervalul imprimabil ASCII (`" "` = 0x20 până la
`"~"` = 0x7e).

**De ce regex pe octeți și nu pe text:** fișierul e binar — nu putem face
`.decode()` pe tot fișierul fără riscul unei erori, fiindcă multe zone nu
sunt text deloc. Căutăm direct în octeți, și abia *fiecare bucată găsită*
(deja garantat ASCII imprimabil) o transformăm în text cu `.decode()`.

#### `citeste_gps(cale)` — coordonate din EXIF

```python
def _grade_zecimale(valoare, emisfera):
    grade, minute, secunde = (float(x) for x in valoare)
    zecimal = grade + minute / 60 + secunde / 3600
    if emisfera in ("S", "W"):
        zecimal = -zecimal
    return zecimal

def citeste_gps(cale: str):
    exif = Image.open(cale).getexif()
    gps = exif.get_ifd(0x8825)  # 34853
    if not gps:
        return None
    lat = _grade_zecimale(gps[2], gps[1])
    lon = _grade_zecimale(gps[4], gps[3])
    return lat, lon
```

**Ce face:** citește blocul GPS din EXIF (tag-ul `34853`, scris aici în hex
ca `0x8825` — e aceeași valoare), care vine ca grade/minute/secunde plus o
emisferă (N/S pentru latitudine, E/V pentru longitudine), și le transformă
în zecimale: `grade + minute/60 + secunde/3600`.

**De ce semnul minus pe S/V:** convenția obișnuită a hărților (și a
`Google Maps`) e ca Sud și Vest să fie coordonate negative; EXIF le ține
mereu pozitive, plus litera emisferei, așa că noi aplicăm semnul.

#### `extrage_ascuns(cale)` — file carving

```python
def extrage_ascuns(cale: str, semnatura: bytes = b"PK\x03\x04", iesire: str = "gasit.zip"):
    date = open(cale, "rb").read()
    i = date.find(semnatura)
    if i == -1:
        return None
    with open(iesire, "wb") as f:
        f.write(date[i:])
    return iesire, i
```

**Ce face:** caută în octeții fișierului semnătura unui al doilea fișier
(implicit semnătura ZIP, `PK\x03\x04`) cu `bytes.find()`, și dacă o găsește,
salvează tot ce urmează de acolo (`date[i:]`) ca fișier nou.

**De ce merge:** vizualizatoarele de imagini se opresc la sfârșitul normal
al pozei (dat de structura internă a formatului PNG/JPEG) și ignoră complet
orice octeți lipiți după. Octeții rămân acolo, fizic, în fișier — `find()` îi
găsește oricând știi ce semnătură cauți.

### `stego.py` — steganografie LSB (Lucrarea B5-B6)

#### `ascunde(cale_gazda, mesaj, cale_iesire)`

```python
mesaj_cu_final = mesaj + b"\x00"
biti = "".join(f"{b:08b}" for b in mesaj_cu_final)
...
for (r, g, b) in px:
    canale = [r, g, b]
    for c in range(3):
        if idx < len(biti):
            canale[c] = (canale[c] & ~1) | int(biti[idx])
            idx += 1
    px_nou.append(tuple(canale))
```

**Ce face:** transformă mesajul în biți (`f"{b:08b}"` scrie fiecare octet pe
8 cifre binare), apoi parcurge fiecare pixel și fiecare canal de culoare
(R, G, B), scriind câte un bit de mesaj în ultimul bit al canalului:
`canale[c] & ~1` șterge ultimul bit (îl pune pe 0), iar `| int(biti[idx])`
scrie acolo bitul nostru.

**De ce adaug un octet `0x00` la final:** e "santinela" — semnul că mesajul
s-a terminat. Fără el, la dezvăluire nu am ști unde să ne oprim din citit
biți (am continua până la ultimul pixel din poză, umplând restul cu gunoi).

**De ce salvăm ca `.png`, nu `.jpg`:** JPEG recomprimă imaginea la salvare
(e cu pierderi), ceea ce schimbă exact biții pe care tocmai i-am ascuns.
PNG e fără pierdere, deci biții rămân neatinși.

#### `dezvaluie(cale_stego)`

```python
biti = []
for (r, g, b) in px:
    biti.append(r & 1)
    biti.append(g & 1)
    biti.append(b & 1)

octeti = bytearray()
for i in range(0, len(biti) - 7, 8):
    octet = 0
    for bit in biti[i:i + 8]:
        octet = (octet << 1) | bit
    if octet == 0:
        break
    octeti.append(octet)
```

**Ce face:** e exact inversul lui `ascunde()`. Citește ultimul bit al
fiecărui canal (`r & 1`), le strânge pe toate într-o listă lungă de biți,
apoi le regrupează câte 8 (`biti[i:i+8]`) ca să reconstituie fiecare octet
original: `(octet << 1) | bit` mută octetul construit până acum cu o poziție
la stânga și adaugă bitul curent, bit cu bit.

**De ce ne oprim la primul `octet == 0`:** e exact santinela pusă de
`ascunde()` — semnalul că mesajul util s-a terminat și restul pixelilor nu
mai conțin nimic relevant.

#### `detecteaza(cale)` — nu mesajul, ci urma lui

```python
def detecteaza(cale: str) -> Counter:
    px = list(Image.open(cale).convert("RGB").getdata())
    ultimii = [r & 1 for (r, g, b) in px]
    return Counter(ultimii)
```

**Ce face:** numără de câte ori apare `0`, respectiv `1`, ca ultim bit al
canalului roșu, pe toți pixelii. Într-o poză naturală, fără mesaj ascuns,
distribuția nu e perfect echilibrată; un mesaj ascuns prin LSB tinde să
apropie distribuția de 50/50, pentru că biții unui mesaj text (sau al
oricărui conținut comprimat) sunt aproape aleatori. E un semnal statistic de
suspiciune, nu o dovadă — dar e exact principiul din spatele uneltelor reale
de detecție (zsteg, stegsolve).
