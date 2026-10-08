#!/usr/bin/env python3
"""Prueft aufnahmeberatung-widget.html vor jedem Commit (laeuft als pre-commit-Hook).

Anlass: Am 06.10.2026 hat eine Regex-Ersetzung die Sprechzeit von Nicole Schneider zu
".30 Uhr" plus unsichtbarem Steuerzeichen zerstoert; das stand zwei Tage live.

Pruefungen:
  1. keine Steuerzeichen (U+0000-U+001F ausser Tab/Zeilenumbruch, U+007F-U+009F)
  2. jede Sprechzeit-Zeile "… Uhr (Name)" hat die Form "<Tag>, HH.MM – HH.MM Uhr"
  3. jede Uhrzeit vor "Uhr" ist vollstaendig (HH.MM), kein Rest wie ".30 Uhr"
  4. dieselbe Person hat an allen Stellen dieselbe Sprechzeit

Aufruf: python3 pruefen.py   (Exit-Code 1 bei Fehlern)
"""
import html
import re
import sys
from pathlib import Path

DATEI = Path(__file__).with_name("aufnahmeberatung-widget.html")
TAGE = {"Mo": "Montag", "Di": "Dienstag", "Mi": "Mittwoch", "Do": "Donnerstag",
        "Fr": "Freitag", "Sa": "Samstag"}
TAG = "|".join(list(TAGE) + list(TAGE.values()))


def zeilennr(roh, pos):
    return roh.count("\n", 0, pos) + 1


def main():
    roh = DATEI.read_text(encoding="utf-8")
    fehler = []

    for m in re.finditer(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", roh):
        fehler.append(f"Zeile {zeilennr(roh, m.start())}: Steuerzeichen U+{ord(m.group()):04X}")

    # Nur den sichtbaren Text pruefen: Skripte/Styles/Kommentare raus, Tags durch Leerzeichen
    # ersetzen (<br> trennt Zeilen), Entities aufloesen.
    text = re.sub(r"<(script|style)\b.*?</\1>|<!--.*?-->", " ", roh, flags=re.S)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))

    for m in re.finditer(r"(\S*)\s+Uhr\b", text):
        if not re.fullmatch(r"\d{1,2}[.:]\d{2}", m.group(1)):
            fehler.append(f"unvollstaendige Uhrzeit: {text[max(0, m.start() - 30):m.end()]!r}")

    zeiten = {}
    for m in re.finditer(r"([^\n]*?)\s*Uhr\s*\(([^)–,]+?)\s*(?:[–,][^)]*)?\)", text):
        vorne, name = m.group(1).strip(), m.group(2).strip()
        z = re.search(rf"({TAG}),\s*(\d{{1,2}}\.\d{{2}})\s*–\s*(\d{{1,2}}\.\d{{2}})$", vorne)
        if not z:
            fehler.append(f"Sprechzeit von {name} unvollstaendig: {vorne[-40:]!r} Uhr")
            continue
        tag = TAGE.get(z.group(1), z.group(1))
        zeiten.setdefault(name, set()).add(f"{tag}, {z.group(2)} – {z.group(3)}")

    for name, varianten in zeiten.items():
        if len(varianten) > 1:
            fehler.append(f"{name}: abweichende Sprechzeiten {sorted(varianten)}")

    if fehler:
        print("pruefen.py: aufnahmeberatung-widget.html hat Fehler:")
        for f in fehler:
            print("  -", f)
        return 1
    print("pruefen.py: OK –", "; ".join(f"{n}: {', '.join(sorted(v))}" for n, v in zeiten.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
