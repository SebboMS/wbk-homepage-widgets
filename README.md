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

`showFrom` darf auch eine Uhrzeit tragen (`new Date(2026, 8, 10, 14, 30)`). Sinnvoll ist als
Startpunkt das Ende der **vorangehenden** Sprechstunde derselben Berater\*in: Wer vorher auf die
Seite schaut, plant ohnehin für den früheren Termin, und der Hinweis stünde nur unnötig im Weg.

**Aktueller Eintrag (Stand 08.09.2026):** Nicole Schneiders Sprechstunde endet am
Donnerstag, **17. September 2026** bereits um 14.00 Uhr (Konferenz um 14.00 Uhr). Der Hinweis
erscheint ab Donnerstag, 10. September, 14.30 Uhr (Ende ihrer Sprechstunde in der Woche davor)
und läuft bis einschließlich 17. September; danach kann er entfernt werden. In dieser Zeit steht
in der Sprechzeit-Zeile „Do, 13.00 – 14.00 Uhr", weil im Fenster nur dieser eine Donnerstag liegt.
Wichtig beim Nachbauen: `showFrom` so legen, dass kein regulärer Termin derselben Berater\*in mehr
ins Fenster fällt — sonst zeigt die Zeile für diesen Termin die falsche Zeit.

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
