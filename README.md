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
