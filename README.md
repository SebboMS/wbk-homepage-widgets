# WBK Homepage-Widgets

Widgets für die Homepage des Weiterbildungskollegs Münster (wbk.ms). Jede Datei ist ein
eigenständiger HTML-Fragment-Widget (Style + Markup + Script), der per Loader-Snippet
live von GitHub in WordPress eingebunden wird. Änderungen hier landen nach dem Push
automatisch auf der Homepage – kein manuelles Copy-Paste in WordPress mehr nötig.

## Enthaltene Widgets

- `aufnahmeberatung-widget.html` – "Finde deine Beratungssprechstunde"-Assistent
  (Aufnahmeberatung, Sprechstunden, Ferienmodus).

## Einbindung in WordPress

Einmalig im "Benutzerdefiniertes HTML"-Block auf der Homepage folgenden Loader
einfügen (Datei- und Widget-Namen ggf. anpassen):

```html
<div id="wbk-remote-widget">Lädt …</div>
<script>
(function () {
  var target = document.getElementById('wbk-remote-widget');
  var url = 'https://raw.githubusercontent.com/SebboMS/wbk-homepage-widgets/main/aufnahmeberatung-widget.html'
    + '?v=' + Date.now(); // Cache-Busting, damit Änderungen sofort sichtbar sind

  fetch(url)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
    .then(function (html) {
      target.innerHTML = html;
      // <script>-Tags werden von innerHTML nicht ausgeführt -> manuell ersetzen
      target.querySelectorAll('script').forEach(function (old) {
        var s = document.createElement('script');
        if (old.src) { s.src = old.src; } else { s.textContent = old.textContent; }
        old.parentNode.replaceChild(s, old);
      });
    })
    .catch(function () {
      target.innerHTML = '<p style="font-size:14px;color:#666;">Aktuell nicht verfügbar. '
        + 'Infos zur Aufnahmeberatung unter <a href="https://wbk.ms">wbk.ms</a>.</p>';
    });
})();
</script>
```

Danach genügt es, die Widget-Datei hier im Repo zu ändern und zu pushen – die
Homepage lädt bei jedem Seitenaufruf automatisch den aktuellen Stand.

## Update-Workflow

1. Widget-HTML hier im Repo anpassen.
2. Commit + Push auf `main`.
3. Fertig – kein Eingriff in WordPress nötig.

## Ferienmodus: vor den Sommerferien anpassen

Zwischen `holidayFrom` und `holidayUntil` zeigt das Widget statt des Frage-Assistenten den
Screen `wbk-holiday` (Ferien-Hinweise). Der Screen bleibt das Jahr über stehen, seine Inhalte
sind aber jahresspezifisch. **Stand der Angaben: Sommer 2026** — vor den nächsten Sommerferien
diese Stellen durchgehen:

**Im Markup (Screen `wbk-holiday`)**

| Stelle | Was aktualisiert werden muss |
| --- | --- |
| Karte `hc-pause` | Ende der Anmeldephase (zuletzt 15. Juli 2026) und NRW-Ferienzeitraum (zuletzt 20. Juli – 1. September 2026) |
| `wbk-holiday-nachreichen` | Sondersprechstunde zum Nachreichen: Termin, Beratungsperson, Raum. War 2026 ein einmaliger Mittwochstermin — gibt es sie nicht wieder, den ganzen Block löschen |
| `wbk-newtimes-soon` | Semester, für das dann angemeldet wird (zuletzt: Sommersemester 2027, Start Februar 2027) |
| `wbk-newtimes` | Startdatum der neuen Sprechzeiten, die Sprechzeiten selbst (Münster + Rheine) und wieder die Semesterangabe |

**Im Script**

| Variable | Bedeutung |
| --- | --- |
| `holidayFrom` / `holidayUntil` | Zeitfenster des Ferienmodus (zuletzt 16. Juli – 1. September 2026) |
| `newtimesFrom` | Ab wann statt „Termine folgen" die konkreten neuen Sprechzeiten stehen (zuletzt 1. August 2026) |
| `nachreichenHideAfter` | Ab wann die Sondersprechstunde ausgeblendet wird (zuletzt 27. August 2026) |
| Überschrift + Intro | Werden im Ferienmodus per Script überschrieben (`wbk-heading`, `wbk-intro`) |

**Monate sind 0-basiert** — `new Date(2027, 6, 15)` ist der 15. Juli 2027.

Ändern sich dabei die Sprechzeiten, stehen sie an **drei** Stellen: in `wbk-newtimes`, im Endscreen
`wbk-alg-ms` (Zeile „Zeiten") und im Endscreen `wbk-beg-ms` (Schritt 1). Alle drei anpassen.

Zum Schuljahresstart ist außerdem meist ein Banner sinnvoll, dass in der ersten Schulwoche noch
keine Beratung stattfindet — Vorlage dafür im Abschnitt oben.

## Info-Banner oben (Gerüst)

Für Hinweise, die über dem gesamten Widget stehen (z. B. „Beratung startet erst ab …"), gibt es
das CSS-Gerüst `.deadline-banner`. Es ist bewusst ohne Beispiel im Markup, damit keine
abgelaufenen Termine in der Datei liegen bleiben. Zum Einsetzen direkt nach dem `<p id="wbk-intro">`:

```html
<div id="wbk-startinfo" class="deadline-banner">
  <span class="db-icon">&#128197;</span>
  <span class="db-text">Text mit <strong>hervorgehobenem Termin</strong>.</span>
</div>
```

Dazu im Script ein Zeitfenster ergänzen (`if (now >= von && now < bis) { …style.display = 'flex'; }`)
und beides nach Ablauf wieder entfernen.

## Datumsgesteuerte Ausfall- und Änderungs-Hinweise

Kurzfristige Abweichungen bei den Sprechzeiten (Ausfall, Vertretung, verkürzte Sprechstunde)
werden **nicht** in die Sprechzeiten-Zeilen eingerechnet, sondern als eigene Hinweis-Box über
der Beratungskarte eingeblendet — automatisch nur in einem festgelegten Zeitfenster. So kann
der Hinweis mit Vorlauf eingebaut werden und verschwindet danach ohne weiteres Zutun.

So wird ein Hinweis ergänzt:

1. In **jedes** betroffene Endscreen (z. B. `wbk-alg-ms` *und* `wbk-beg-ms` — dort stehen die
   Münsteraner Sprechzeiten doppelt) eine Box `<div id="…" class="notice-warn">` direkt vor
   `<div class="card">` einsetzen.
2. Die betroffene Sprechzeit-Zeile in ein `<span id="…">` klammern, damit sie markiert werden kann.
3. Im Script unten einen Eintrag im Array `ausfaelle` ergänzen:
   - `noticeIds` – ids der Hinweis-Boxen
   - `lineIds` – (optional) ids der markierten Zeilen
   - `lineClass` – `line-cancelled` (durchgestrichen, fällt aus) oder `line-changed`
     (gelb hinterlegt, findet geändert statt)
   - `textSwaps` – (optional) `[{ id, text }]`: ersetzt im Zeitfenster den Text einzelner
     Elemente. Damit steht in der Sprechzeit-Zeile direkt die geänderte Uhrzeit. Dafür ist die
     Endzeit in ein eigenes `<span>` gefasst (`wbk-alg-ms-ns-end`, `wbk-beg-ms-ns-end`) —
     bei anderen Zeilen ebenso vorgehen.
   - `showFrom` / `hideAfter` – Zeitfenster `[showFrom .. hideAfter)`; **Monate sind 0-basiert**
     (`new Date(2026, 8, 18)` = 18. September 2026)

Abgelaufene Einträge samt ihrer Hinweis-Boxen wieder löschen, damit die Datei nicht zuwächst.
Beim Löschen auch die `id`-Spans um die Zeilen (`…-line`, `…-end`) wieder auflösen, und zwar
**per Klartext-Ersetzung, nicht per Regex**.

### Automatische Prüfung vor jedem Commit (`pruefen.py`)

Anlass: Am 06.10.2026 hat eine Regex-Ersetzung beim Auflösen dieser Spans die Sprechzeit von
Nicole Schneider zerstört (`\1` direkt vor einer Ziffer, `\114.30`, wurde als Oktal-Escape
gelesen). Im Widget stand zwei Tage „.30 Uhr" mit einem unsichtbaren Steuerzeichen (U+008C)
statt „Do, 13.00 – 14.30 Uhr"; Sebastian hat es am 08.10.2026 auf der Homepage entdeckt.

Seitdem läuft `pruefen.py` als **pre-commit-Hook** (`.githooks/pre-commit`) und blockiert den
Commit, wenn

1. Steuerzeichen in der Datei stehen,
2. eine Sprechzeit-Zeile „… Uhr (Name)" nicht die Form „Tag, HH.MM – HH.MM Uhr" hat,
3. vor „Uhr" keine vollständige Uhrzeit steht,
4. dieselbe Person an verschiedenen Stellen verschiedene Sprechzeiten hat.

Ändert sich eine reguläre Sprechzeit, also **alle** Stellen ändern, sonst schlägt Punkt 4 an.

Der Hook ist **nur aktiv, wenn `core.hooksPath` gesetzt ist** (gilt je Klon, wird nicht mit
übertragen). Nach einem neuen Klon einmal ausführen:

```bash
git config core.hooksPath .githooks
```

Von Hand prüfen: `python3 pruefen.py`. Getestet gegen den kaputten Stand `ab88f49` (schlägt an)
und gegen `d77ed61` und den heutigen Stand (OK).

Bei `textSwaps` (geänderte Uhrzeit in der Zeile) und bei `line-cancelled` `showFrom` so legen,
dass **kein regulärer Termin derselben Berater\*in** mehr ins Fenster fällt — sonst wird dieser
Termin mit falscher Zeit angezeigt oder durchgestrichen.

`showFrom` darf auch eine Uhrzeit tragen (`new Date(2026, 8, 10, 14, 30)`). Sinnvoll ist als
Startpunkt das Ende der **vorangehenden** Sprechstunde derselben Berater\*in: Wer vorher auf die
Seite schaut, plant ohnehin für den früheren Termin, und der Hinweis stünde nur unnötig im Weg.

**Aktueller Eintrag (Stand 06.10.2026):** Die Sprechstunde für Geflüchtete (Cylia Büsching)
fällt am Mittwoch, **7. Oktober 2026** aus. Hinweis-Box dreisprachig (Deutsch, Englisch,
Arabisch) im Endscreen `wbk-flu`, die Zeile „Zeit" wird durchgestrichen. Läuft vom 6. bis
einschließlich 7. Oktober und kann danach entfernt werden. Der abgelaufene Eintrag zum
17.09.2026 (Nicole Schneider) ist samt Boxen gelöscht.

Getestet wird mit `preview.html` (lokal, nicht im Repo): dort lässt sich ein beliebiges Datum
simulieren, ohne die Systemuhr zu stellen.

## E-Mail-Vorlage an Katja Klein (Beratung mit Begleitperson)

Die beiden Links „E-Mail an Katja Klein schreiben" (Ferienkarte + Begleitperson-Schritt)
bekommen ihren `mailto:`-Link **per Script** (`var kkBody` im Script-Block, gesucht über
die Klasse `.wbk-kk-mail`) — nicht im HTML-Attribut. Grund: Betreff und Fließtext werden
so mit `encodeURIComponent` kodiert, damit Umlaute und Zeilenumbrüche im Mailprogramm
sauber ankommen. Das `href` im Markup ist nur der Fallback ohne Vorlage.

Abgefragte Felder (Stand 02.09.2026):

1. Name (Bewerber\*in)
2. Name der Begleitperson
3. Letzter Schulabschluss — mit Beispielen, weil Bewerber\*innen die aktuellen
   Bezeichnungen oft nicht kennen
4. Angestrebter Schulabschluss am WBK — Wunschziel, damit die Beratung vorbereitet ist
5. Gewünschte Sprechstunde (Berater\*in / Wochentag)

Beim Ändern: Text in `kkBody` anpassen, `\n` für Zeilenumbrüche, Umlaute als
`\uXXXX`-Escapes schreiben (Rest der Datei macht es genauso). Vorlage nicht zu lang
werden lassen — manche Mailprogramme kürzen sehr lange `mailto:`-Links.
