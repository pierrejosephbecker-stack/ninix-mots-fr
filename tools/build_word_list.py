#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""Fabrique la liste de mots de la Course aux mots (« fr-gl7.7-1 ») à partir du lexique Grammalecte 7.7.

Usage :
    python3 tools/build_word_list.py                      # télécharge le lexique (12 Mo) dans un dossier temporaire
    python3 tools/build_word_list.py --source lexique.zip # ou part d'une copie locale du zip (ou du .txt qu'il contient)
    python3 tools/build_word_list.py --check              # vérifie que Ninix/Resources/Games/mots-fr.txt est à jour

Python 3.9 ou plus, sans dépendance. Règles : docs/jeux/course-aux-mots.md, § 5.3 et § 5.4.
1. Lignes du lexique : on écarte les étiquettes `npr`, `prn`, `patr` (noms propres, prénoms, patronymes) et les notes
   `sig`, `symb`, `unit`, `cc`, `abty` (sigles, symboles, unités…). On garde `abr`, sinon ZOO disparaît.
2. On écarte toute forme qui commence par une majuscule ou qui contient autre chose qu'une lettre (chiffre, espace,
   apostrophe, trait d'union, point) : les mots composés sont exclus.
3. Œ devient OE, Æ devient AE ; décomposition NFD et suppression des marques U+0300 à U+036F ; il ne doit alors rester
   que des lettres ASCII, mises en majuscules.
4. On garde les mots de 3 à 9 lettres (`^[A-Z]{3,9}$`), sans doublon.
5. On retire la liste noire `tools/word_list_blacklist.txt` (un mot par ligne, `#` pour les commentaires).
Le fichier écrit est en UTF-8 sans BOM, un mot par ligne, `\n` après chaque mot, trié par octets.
"""

import argparse
import hashlib
import io
import os
import re
import sys
import unicodedata
import urllib.request
import zipfile

SOURCE_URL = "https://www.grammalecte.net/dic/lexique-grammalecte-fr-v7.7.zip"
SOURCE_ZIP_SHA256 = "bdccf2065e252010253171000a38de84581407896b6bc60aca7d4d69dab7e4d2"
SOURCE_TXT_NAME = "lexique-grammalecte-fr-v7.7.txt"
SOURCE_TXT_SHA256 = "dc1fa3740e6353bccdcb435ea8f1c8a65287726026abd53dd232d5d494548eff"

LEXICON_VERSION = "fr-gl7.7-1"
BAD_TAGS = {"npr", "prn", "patr"}
BAD_NOTES = {"sig", "symb", "unit", "cc", "abty"}
WORD = re.compile(r"[A-Z]{3,9}")
ASCII_LETTERS = re.compile(r"[A-Za-z]+")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACKLIST = os.path.join(ROOT, "tools", "word_list_blacklist.txt")
OUTPUT = os.path.join(ROOT, "Ninix", "Resources", "Games", "mots-fr.txt")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_source(path):
    """Texte du lexique, après contrôle des empreintes. `path` : zip ou .txt local, ou None pour télécharger."""
    if path is None:
        print(f"Téléchargement de {SOURCE_URL}…", file=sys.stderr)
        with urllib.request.urlopen(SOURCE_URL, timeout=120) as response:
            raw = response.read()
    else:
        with open(path, "rb") as f:
            raw = f.read()
    if zipfile.is_zipfile(io.BytesIO(raw)):
        if sha256(raw) != SOURCE_ZIP_SHA256:
            # Le zip peut être refait à l'identique du contenu : seule l'empreinte du texte fait foi.
            print(f"Attention : empreinte du zip inattendue ({sha256(raw)}).", file=sys.stderr)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            raw = archive.read(SOURCE_TXT_NAME)
    if sha256(raw) != SOURCE_TXT_SHA256:
        sys.exit(f"Lexique inattendu : SHA-256 {sha256(raw)}, attendu {SOURCE_TXT_SHA256}.")
    return raw.decode("utf-8")


def normalize(form):
    """Forme du lexique → mot en majuscules ASCII, ou None si elle ne s'écrit pas qu'avec des lettres A à Z."""
    form = form.replace("œ", "oe").replace("Œ", "OE").replace("æ", "ae").replace("Æ", "AE")
    form = unicodedata.normalize("NFD", form)
    form = "".join(c for c in form if not 0x300 <= ord(c) <= 0x36F)
    if not ASCII_LETTERS.fullmatch(form):
        return None
    return form.upper()


def candidate_words(text):
    words = set()
    for line in text.splitlines():
        fields = line.split("\t")
        # Lignes de données : id numérique, puis fid, Flexion, Lemme, Étiquettes, Métagraphe, Metaphone2, Notes…
        if len(fields) < 8 or not fields[0].isdigit():
            continue
        form, tags, notes = fields[2], set(fields[4].split()), set(fields[7].split())
        if tags & BAD_TAGS or notes & BAD_NOTES:
            continue
        if not form or form[0].isupper():
            continue
        word = normalize(form)
        if word is not None and WORD.fullmatch(word):
            words.add(word)
    return words


def read_blacklist():
    words = []
    with open(BLACKLIST, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            entry = line.split("#", 1)[0].strip()
            if not entry:
                continue
            if not WORD.fullmatch(entry):
                sys.exit(f"{BLACKLIST}:{number} : « {entry} » n'est pas un mot de 3 à 9 lettres A à Z.")
            words.append(entry)
    return words


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", help="zip ou .txt du lexique Grammalecte 7.7 déjà téléchargé")
    parser.add_argument("--check", action="store_true", help="vérifie le fichier existant au lieu de l'écrire")
    args = parser.parse_args()

    candidates = candidate_words(read_source(args.source))
    blacklist = read_blacklist()
    unknown = sorted(set(blacklist) - candidates)
    if unknown:
        print(f"Liste noire : {len(unknown)} mot(s) absent(s) de la liste, sans effet : {' '.join(unknown)}", file=sys.stderr)
    words = sorted(candidates - set(blacklist), key=lambda w: w.encode("ascii"))
    data = "".join(word + "\n" for word in words).encode("ascii")

    if args.check:
        with open(OUTPUT, "rb") as f:
            current = f.read()
        if current != data:
            sys.exit(f"{OUTPUT} n'est pas à jour : relancer sans --check.")
    else:
        os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
        with open(OUTPUT, "wb") as f:
            f.write(data)

    print(f"{LEXICON_VERSION} : {len(candidates)} candidats, {len(set(blacklist) & candidates)} retirés par la liste noire")
    print(f"{len(words)} mots, {len(data)} octets")
    print(f"SHA-256 {sha256(data)}")


if __name__ == "__main__":
    main()
