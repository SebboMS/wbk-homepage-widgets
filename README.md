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
Homepage lädt bei jedem Seitenaufruf den Stand, den GitHub gerade ausliefert.

**Verzögerung bis zu ~5 Minuten:** `raw.githubusercontent.com` speichert die Datei je
CDN-Server zwischen (`cache-control: max-age=300`). Das `?v=`-Cache-Busting im Loader hilft
dagegen nicht. Nach einem Push liefern einzelne Server noch einige Minuten die alte Fassung,
auch nach Neuladen und auf anderen Geräten (beobachtet 08.10.2026: Push 08:46, im Browser
bis 08:50 alt, ab 08:50:33 neu). Erst nach 5 Minuten auf der Homepage nachsehen.

## Update-Workflow

1. Widget-HTML hier im Repo anpassen.
2. Commit + Push auf `main`.
3. Nach ~5 Minuten auf https://wbk.ms/was-zeichnet-uns-aus/ prüfen (dort ist das Widget
   eingebunden) – kein Eingriff in WordPress nötig.

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

**Ferienhinweise** (keine Sprechstunden in den Ferien) laufen über dieses Banner, nicht über
`ausfaelle`: Es steht über allen Screens und gilt damit für Münster, Rheine und die Sprechstunde
für Geflüchtete zugleich. Je Ferien ein eigenes Banner (`id`) plus ein Eintrag im Script-Array
`ferienBanner` (`id`, `von`, `bis`). Fenster: **ab dem Ende der letzten Sprechstunde vor den
Ferien** (Sebastian, 15.10.2026: vorher steht der Hinweis Bewerber\*innen im Weg, die noch kommen
wollen) bis zum Beginn des ersten Tages mit Sprechstunde danach. Im Text die Werktage der Ferien
nennen und den ersten Tag mit regulären Sprechzeiten. Ferientermine aus
`unterrichtsplanung/semester-*.md` (Abschnitt „Rahmentermine“) im WBK-Ordner.

**Aktuelle Einträge (Stand 15.10.2026):**

| Banner | Ferien | Text | Fenster | Geprüft mit `preview.html` |
| --- | --- | --- | --- | --- |
| `wbk-herbstferien` | Sa 17.10.–Sa 31.10.2026 | „19. bis 30. Oktober 2026“, ab Mo 2. November | Fr 16.10.2026, 13.30 Uhr (Ende Freitags-Sprechstunde) bis einschl. 01.11.2026 | 16.10. 13.29 aus, 13.30 an, 01.11. 23.00 an, 02.11. aus |
| `wbk-weihnachtsferien` | Mi 23.12.2026–Mi 06.01.2027 | „23. Dezember 2026 bis 6. Januar 2027“, ab Do 7. Januar | Di 22.12.2026, 18.30 Uhr (Ende Dienstags-Sprechstunde) bis einschl. 06.01.2027 | 22.12. 18.29 aus, 18.30 an, 24.12. an, 06.01. 23.00 an, 07.01. aus |

Nach Ablauf Banner und Array-Eintrag per Klartext-Ersetzung entfernen.

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
   - `lineClass` – `line-cancelled` (durchgestrichen, fällt aus), `line-hidden` (ganz
     ausgeblendet, entfällt ohne Hinweis; dann keine Hinweis-Box nötig) oder `line-changed`
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

**Aktueller Eintrag (Stand 15.10.2026):** Die Freitags-Sprechstunde von Sebastian Aufdemkamp
findet vom **20. November bis 18. Dezember 2026** nicht statt (Elternzeit). Sie wird in der Zeit
**ganz ausgeblendet, ohne Hinweis-Box** (Sebastian, 15.10.2026: „Die findet dann einfach nicht
statt.“). Die Freitagszeilen (`wbk-alg-ms-ak-line`, `wbk-beg-ms-ak-line`) bekommen `line-hidden`,
in der Berater-Zeile (`wbk-alg-ms-berater`) ersetzt ein `textSwap` den Text durch „Nicole
Schneider oder Philipp Terwey“. Der Zeilenumbruch `<br>` steht dafür **innerhalb** der Spans,
sonst bliebe eine Leerzeile. Fenster ab Fr 13.11.2026, 13.30 Uhr (Ende der letzten regulären
Sprechstunde davor) bis einschließlich 18.12.2026; danach Eintrag und Spans per
Klartext-Ersetzung entfernen. Geprüft mit `preview.html` an 13.11. 12.00 (sichtbar), 13.11. 13.30,
20.11., 18.12. (ausgeblendet), 19.12. (sichtbar). **Offen:** Annabelle bietet in der Zeit eine
Sprechstunde an, Termin noch nicht festgelegt (Sebastian, 14.10.2026); dann als eigene Zeile
ergänzen. Die früheren Hinweis-Boxen `wbk-*-ms-ak-elternzeit` sind gelöscht.
Der abgelaufene Eintrag zum 07.10.2026 (Cylia Büsching) ist samt Box und Span gelöscht.

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
