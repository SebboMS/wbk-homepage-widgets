#!/usr/bin/env python3
"""Liest Sprechzeiten, Ausfälle und Ferienhinweise aus aufnahmeberatung-widget.html und schreibt sprechzeiten.json.

Das Widget bleibt die einzige Stelle, an der Sebastian die Sprechzeiten pflegt. Diese Datei ist daraus abgeleitet
und wird nie von Hand geändert. Die neue Homepage (Repo SebboMS/wbk-homepage) liest sie und zeigt die Sprechzeiten in
ihrer eigenen Gestaltung, mit denselben Ausfällen und Ferienhinweisen wie das Widget.

Läuft im pre-commit-Hook nach pruefen.py und legt die Datei mit in den Commit. Von Hand:
    python3 daten.py            # schreibt sprechzeiten.json
    python3 daten.py --pruefen  # meldet nur, ob die Datei zum Widget passt (Exit-Code 1, wenn nicht)

Findet das Skript eine erwartete Stelle im Widget nicht (umgebaut, umbenannt), bricht es mit einer Meldung ab,
statt eine halbe Datei zu schreiben. Nur Python-Standardbibliothek.
"""
import html
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WIDGET = HIER / "aufnahmeberatung-widget.html"
ZIEL = HIER / "sprechzeiten.json"
TAGE = {"Mo": "Montag", "Di": "Dienstag", "Mi": "Mittwoch", "Do": "Donnerstag", "Fr": "Freitag", "Sa": "Samstag"}
TAG_RE = "|".join(list(TAGE) + list(TAGE.values()))


class Fehler(Exception):
    pass


def text(s):
    s = re.sub(r"<br\s*/?>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def block(roh, element_id):
    """HTML des Elements mit dieser id bis zum nächsten Element auf derselben Ebene (für die Endscreens genügt
    der Abschnitt bis zum nächsten Kommentar-Screen)."""
    m = re.search(rf'<div id="{element_id}"[^>]*>', roh)
    if not m:
        raise Fehler(f"Element #{element_id} nicht gefunden")
    ende = re.search(r"\n  <!-- (?:Screen|Endscreen)", roh[m.end():])
    return roh[m.start(): m.end() + ende.start() if ende else len(roh)]


def zeile(abschnitt, schluessel):
    m = re.search(rf'<span class="key">{schluessel}</span><span class="val"[^>]*>(.*?)</span></div>', abschnitt, re.S)
    if not m:
        raise Fehler(f"Zeile „{schluessel}“ nicht gefunden")
    return m.group(1)


def zeit(s):
    m = re.search(rf"({TAG_RE}), (\d{{1,2}}\.\d{{2}}) – (\d{{1,2}}\.\d{{2}}) Uhr", text(s))
    if not m:
        raise Fehler(f"Sprechzeit nicht lesbar: {text(s)!r}")
    return TAGE.get(m.group(1), m.group(1)), m.group(2), m.group(3)


def datum(js):
    """new Date(2026, 10, 19, 14, 30) -> '2026-11-19T14:30' (Monate im Widget 0-basiert)."""
    m = re.fullmatch(r"new Date\((\d{4}),\s*(\d{1,2}),\s*(\d{1,2})(?:,\s*(\d{1,2}))?(?:,\s*(\d{1,2}))?\)", js.strip())
    if not m:
        raise Fehler(f"Datum nicht lesbar: {js!r}")
    j, mo, t, h, mi = m.groups()
    return f"{int(j):04d}-{int(mo) + 1:02d}-{int(t):02d}T{int(h or 0):02d}:{int(mi or 0):02d}"


def js_liste(roh, name):
    m = re.search(rf"var {name} = \[(.*?)\n  \];", roh, re.S)
    if not m:
        raise Fehler(f"Liste „{name}“ im Script nicht gefunden")
    inhalt = re.sub(r"/\*.*?\*/", "", m.group(1), flags=re.S)
    inhalt = re.sub(r"//[^\n]*", "", inhalt)
    return [e for e in re.findall(r"\{(.*?)\}\s*(?:,|$)", inhalt, re.S) if e.strip()]


def js_feld(eintrag, feld):
    m = re.search(rf"{feld}:\s*(new Date\([^)]*\)|'[^']*'|\[[^\]]*\])", eintrag)
    return m.group(1) if m else None


def js_ids(wert):
    return re.findall(r"'([^']+)'", wert or "")


def lesen():
    roh = WIDGET.read_text(encoding="utf-8")

    # Regelmäßige Sprechzeiten Münster: Endscreen „Allgemein Münster“, Zeile „Zeiten“
    ms = block(roh, "wbk-alg-ms")
    zeiten_html = zeile(ms, "Zeiten")
    muenster, zeilen_id, nach_name = [], {}, {}
    for teil in re.split(r"<br\s*/?>", zeiten_html):
        if not text(teil):
            continue
        tag, von, bis = zeit(teil)
        name = re.search(r'<span class="muted">\(([^)]*)\)</span>', teil)
        if not name:
            raise Fehler(f"Name fehlt in der Zeile {text(teil)!r}")
        eintrag = {"tag": tag, "von": von, "bis": bis, "name": html.unescape(name.group(1)), "art": "allgemein"}
        nach_name[eintrag["name"]] = eintrag
        muenster.append(eintrag)
    # Markierbare Zeilen (<span id="wbk-alg-ms-xx-line">…(Name)…): Kennung dem Namen danach zuordnen. Das <br> steht
    # teils innerhalb der Klammer-Spans, deshalb nicht über die Teile oben.
    for m in re.finditer(r'id="wbk-alg-ms-([a-z]+)-line">', zeiten_html):
        n = re.search(r'<span class="muted">\(([^)]*)\)</span>', zeiten_html[m.end():])
        name = html.unescape(n.group(1)) if n else None
        if name in nach_name:
            nach_name[name]["kennung"] = m.group(1)
            zeilen_id[f"wbk-alg-ms-{m.group(1)}-line"] = nach_name[name]
    # Sprechstunde für Geflüchtete: Endscreen „Geflüchtete“
    flu = block(roh, "wbk-flu")
    tag, von, bis = zeit(zeile(flu, "Zeit"))
    muenster.append({"tag": tag, "von": von, "bis": bis, "name": text(zeile(flu, "Berater\\*in")),
                     "art": "gefluechtete", "zusatz": "Sprechstunde für Geflüchtete"})
    reihenfolge = list(TAGE.values())
    muenster.sort(key=lambda e: (reihenfolge.index(e["tag"]), e["von"]))

    # Rheine: Endscreen „Allgemein Rheine“
    rh = block(roh, "wbk-alg-rh")
    tag, von, bis = zeit(zeile(rh, "Zeit"))
    buchung = re.search(r'href="(https://[^"]*termin[^"]*)"', rh)
    rheine = {"tag": tag, "von": von, "bis": bis, "name": text(zeile(rh, "Berater\\*in")),
              "zusatz": "nur Fachhochschulreife & Abitur", "termin": "erforderlich",
              "buchung": buchung.group(1) if buchung else None}

    # Semester aus dem Hinweis auf die neuen Sprechzeiten
    sem = re.search(r"im <strong>([A-Za-zäöü]+ \d{4})</strong> beginnende <strong>((?:Sommer|Winter)semester \d{4}(?:/\d{2})?)</strong>",
                    html.unescape(block(roh, "wbk-holiday")))
    semester = {"name": sem.group(2), "start": sem.group(1)} if sem else None

    # Ausfälle und Änderungen
    ausfaelle = []
    for e in js_liste(roh, "ausfaelle"):
        notiz = None
        for nid in js_ids(js_feld(e, "noticeIds")):
            n = re.search(rf'<div id="{nid}"[^>]*>.*?<span class="nw-text">(.*?)</span>', roh, re.S)
            if n:
                notiz = text(n.group(1))
                break
        betroffen = []
        for lid in js_ids(js_feld(e, "lineIds")):
            if lid in zeilen_id and zeilen_id[lid]["name"] not in betroffen:
                betroffen.append(zeilen_id[lid]["name"])
        art = {"line-cancelled": "faellt-aus", "line-hidden": "entfaellt", "line-changed": "geaendert"}
        klasse = (js_feld(e, "lineClass") or "'line-cancelled'").strip("'")
        von, bis = js_feld(e, "showFrom"), js_feld(e, "hideAfter")
        if not (von and bis):
            raise Fehler("Ausfall ohne showFrom/hideAfter")
        ausfaelle.append({"von": datum(von), "bis": datum(bis), "art": art.get(klasse, "faellt-aus"),
                          "betrifft": betroffen, "hinweis": notiz})

    # Ferienhinweise
    ferien = []
    for e in js_liste(roh, "ferienBanner"):
        fid = js_ids(js_feld(e, "id"))
        von, bis = js_feld(e, "von"), js_feld(e, "bis")
        if not (fid and von and bis):
            raise Fehler("Ferien-Eintrag unvollständig")
        b = re.search(rf'<div id="{fid[0]}"[^>]*>.*?<span class="db-text">(.*?)</span>', roh, re.S)
        if not b:
            raise Fehler(f"Ferien-Banner #{fid[0]} nicht gefunden")
        ferien.append({"von": datum(von), "bis": datum(bis), "hinweis": text(b.group(1))})

    # Sommerpause (Ferienmodus des Widgets)
    hv = re.search(r"var holidayFrom\s*=\s*(new Date\([^)]*\))", roh)
    hb = re.search(r"var holidayUntil\s*=\s*(new Date\([^)]*\))", roh)
    pause = re.search(r'<div class="holiday-card hc-pause">.*?<p[^>]*>(.*?)</p>', roh, re.S)
    sommerpause = ({"von": datum(hv.group(1)), "bis": datum(hb.group(1)), "hinweis": text(pause.group(1))}
                   if hv and hb and pause else None)

    return {
        "hinweis": "Abgeleitet aus aufnahmeberatung-widget.html durch daten.py. Nicht von Hand ändern.",
        "zeitzone": "Europe/Berlin",
        "semester": semester,
        "muenster": {"ort": "Raum E.15 (Erdgeschoss, neben dem Sekretariat), Uppenkampstiege 21, Münster",
                     "termin": "ohne", "zeiten": muenster},
        "rheine": rheine,
        "ausfaelle": ausfaelle,
        "ferien": ferien,
        "sommerpause": sommerpause,
    }


def main():
    try:
        daten = lesen()
    except Fehler as e:
        sys.exit(f"daten.py: {e}. Das Widget wurde umgebaut; daten.py anpassen (README, Abschnitt „Datendatei“).")
    neu = json.dumps(daten, ensure_ascii=False, indent=1) + "\n"
    alt = ZIEL.read_text(encoding="utf-8") if ZIEL.exists() else ""
    if "--pruefen" in sys.argv:
        if alt != neu:
            sys.exit("sprechzeiten.json passt nicht zum Widget: python3 daten.py ausführen.")
        print("sprechzeiten.json passt zum Widget.")
        return
    if alt != neu:
        ZIEL.write_text(neu, encoding="utf-8")
        print("sprechzeiten.json aktualisiert.")
    else:
        print("sprechzeiten.json unverändert.")


if __name__ == "__main__":
    main()
