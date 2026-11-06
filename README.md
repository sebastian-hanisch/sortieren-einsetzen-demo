# Packen: erst sortieren, dann einsetzen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-sortieren-einsetzen-demo.streamlit.app/)** -->

Erstes Stück der Konzepte-Reihe **„Packen: Reihenfolge und Platzierungsregel“** für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (ein Verfahren mit wachsendem Beispiel: eine Packung entsteht aus einer Reihenfolge der Pakete und einer Regel, wohin das nächste kommt). Die Demo startet bei einer Größe pro Paket (eindimensional) und fragt, was die Containerzahl stärker verändert: die Regel oder die Reihenfolge. Die dreidimensionale Fall-Demo [pack_demo](https://sebastianhanisch-pack-demo.streamlit.app/) packt Kisten mit Geometrie; diese Demo erklärt den einfachsten Fall davor.

## Warum dieses Problem

Pakete kommen nacheinander an und sollen in möglichst wenige gleich große Container. Man kann an zwei Stellen eingreifen: an der Regel, in welchen Container das nächste Paket kommt, und an der Reihenfolge, in der man die Pakete nimmt. Die Demo zeigt an zwei Mengen von zwölf Paketen, dass die Reihenfolge die Containerzahl bei First Fit und Best Fit stärker verändert als der Wechsel zwischen beiden Regeln (bei Beispiel 2 nicht bei jeder Startzahl der Zufallsreihenfolge), und misst dasselbe an je 200 Zufallsinstanzen in 16 Zellen.

## Modell

Ganzzahlige Paketgrößen s₁ … sₙ mit 1 ≤ sᵢ ≤ C, Container der Kapazität C, alle Pakete vorab bekannt. **Regeln:** *Next Fit* (nur der zuletzt geöffnete Container), *First Fit* (der erste Container mit genug Platz), *Best Fit* (der Container mit dem kleinsten freien Platz danach; Gleichstand: der früher geöffnete). **Reihenfolgen:** wie geliefert, größte zuerst (Gleichstand: kleinere Nummer zuerst) oder zufällig mit fester Startzahl. *FFD* ist First Fit mit größten zuerst, *BFD* Best Fit mit größten zuerst. **Schranken:** Volumenschranke L₁ = ⌈Σ sᵢ / C⌉ und die Schranke L₂ nach Martello und Toth; **exaktes Optimum** bis zwölf Pakete per Teilmengen-DP. Formeln im Expander 📐 der App.

## Methodik

- **Kern** (`sei_algorithm.py`): `reihenfolge`, `pack` (Next, First, Best Fit), `l1`, `l2`, `optimum` (DP über Bitmasken: lexikographisch kleinstes Paar aus Containerzahl und Füllung des letzten Containers), `container_pruefen` (unabhängiger Zulässigkeitsprüfer).
- **Handbeispiele:** zwei feste Mengen von je zwölf Paketen (Kapazität 100). Die App zeigt für die gewählte Kombination die Container als gestapelte Balken, daneben alle neun Kombinationen aus Reihenfolge und Regel.
- **Messraster:** vier Größenbereiche (kleine Teile 1 bis 25 %, mittlere 10 bis 50 %, große 20 bis 80 %, breite 1 bis 90 % der Kapazität) × vier Paketzahlen (20, 50, 100, 200) × **200 feste Instanzen** je Zelle, Kapazität 1000, Größen gleichverteilt und ganzzahlig. Maßstab ist die Schranke L₂, weil das Optimum für so viele Pakete nicht berechnet wird. Die Summen stehen als ganze Zahlen in `sei_precomputed.json` (erzeugt von `generate_precomputed.py`, je nach Rechner in rund 10 bis 30 Sekunden neu zu rechnen).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind Messungen an den Instanzen dieser Demo (feste Seeds), nachgerechnet in `tests/test_claims.py`, `tests/test_algorithm.py` und `tests/test_oracle_sortieren_einsetzen.py`. „Container über L₂“ ist der Mittelwert über die 200 Instanzen einer Zelle von (Containerzahl des Verfahrens minus L₂).

| Frage | Befund |
|---|---|
| Beispiel 1 (zwölf Pakete, Summe 459, Volumenschranke 5, Optimum 5) | Wie geliefert brauchen Next Fit, First Fit und Best Fit **7, 7, 7** Container; größte zuerst **7, 5, 5**. Die Reihenfolge verändert die Containerzahl um 2, ein Wechsel zwischen First Fit und Best Fit in keiner Zeile (`tests/test_algorithm.py`, `tests/test_claims.py`) |
| Beispiel 2 (Summe 467, Optimum 5) | Wie geliefert **7, 6, 6**, größte zuerst **7, 5, 5** (Next Fit, First Fit, Best Fit) |
| Wie weit hilft Sortieren bei großen Teilen und 200 Paketen? | Container über L₂ im Mittel: Next Fit 35,32, First Fit 7,54, Best Fit 5,67, FFD 0,72, BFD 0,72 (200 Instanzen) |
| Unterscheiden sich FFD und BFD? | In **1 von 3200** Instanzen (mit anderen Startzahlen können es einige mehr sein); die Mittelwerte sind in **15 von 16** Zellen gleich |
| Best Fit gegen First Fit, beide in Lieferreihenfolge | Im Mittel über die 200 Instanzen einer Zelle braucht Best Fit in **16 von 16** Zellen höchstens so viele Container wie First Fit und in **13** Zellen weniger (einzelne Instanzen können anders ausfallen) |
| Wie viel spart Sortieren gegenüber First Fit in Lieferreihenfolge? | Im Mittel in **7 von 16** Zellen mindestens einen Container; in den anderen neun nicht (kleine Teile, mittlere Teile bis n = 100, große und breite Teile mit n = 20). In den 13 Zellen, in denen Best Fit besser ist als First Fit, ist der Gewinn durch Sortieren mindestens **3,6-mal** so groß wie der durch den Wechsel auf Best Fit (kleinster Wert bei großen Teilen mit n = 200) |
| Trifft FFD die Volumenschranke L₁? (Anteil der Instanzen, n = 20 / 50 / 100 / 200) | kleine Teile: 99,0 / 100,0 / 97,0 / 96,0 %; mittlere Teile: 79,5 / 63,0 / 33,0 / 1,0 %; große Teile: 18,0 / 6,5 / 1,5 / 0,0 %; breite Teile: 34,0 / 17,5 / 15,5 / 9,0 %. Die Hypothese „FFD trifft L₁ fast immer“ gilt nur bei kleinen Teilen |
| Trifft FFD die Schranke L₂? | In 15 von 16 Zellen nicht in allen Instanzen; nur bei kleinen Teilen mit n = 50 in allen 200 |
| Gibt es Pakete, bei denen auch FFD das Optimum verfehlt? | Ja: 502, 254, 252 und 246 (Kapazität 1000; 6, 6, 6 und 12 Stück): braucht FFD 11 Container, das Optimum ist 9 (explizite Packung mit 9 Containern in `tests/test_oracle_sortieren_einsetzen.py`) |

## Ehrliche Grenzen

- Alle Aussagen gelten für gleichverteilte Paketgrößen in vier Bereichen, vier Paketzahlen und **eine** Größe je Paket. Mit zwei Grenzen gleichzeitig (Volumen und Gewicht) ist die Frage „wonach sortiert man?“ offen und nicht Gegenstand dieser Demo.
- Das Optimum rechnet die Demo nur bis zu zwölf Paketen. Im Messraster steht deshalb der Abstand zur Schranke L₂, nicht zum Optimum; wo L₂ unter dem Optimum liegt, ist der Abstand zu groß.
- Die Gütegarantien (FFD höchstens 11/9·OPT + 4 nach Johnson u. a. 1974, 11/9·OPT + 6/9 nach Dósa 2007) stammen aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen; die zweite Schranke prüft ein Test an kleinen Instanzen gegen das exakte Optimum.
- Das Raster sagt nichts über Praxisdaten und nichts über Pakete, die einzeln nacheinander ohne Kenntnis der späteren eintreffen (Online-Packen, Konzepte-Reihe Online-Algorithmen).
- Next Fit steht als Maßstab für „nur den letzten Container prüfen“ da, nicht als Vorschlag.

### Annahmen, Grenzen und bekannte Probleme (Text wie in der App)

**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen.

**Grenzen.** Das Messraster deckt vier Größenbereiche und vier Paketzahlen ab, jeweils mit gleichverteilten Größen und 200 Instanzen je Zelle. Praxisdaten kommen nicht vor. Das exakte Optimum gibt es nur bis 12 Pakete.

**Bekannte Probleme und Unsicherheiten.** Die Mittelwerte des Rasters gelten für diese festen Instanzen; mit anderen Startzahlen ändern sie sich etwas, und eine einzelne Zelle ist kein Gesetz. Next Fit steht als Maßstab für „nur den letzten Container prüfen“ da und ist kein Vorschlag. Die Gütegarantien im Mathematik-Expander stammen aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät.

## Verifikation

- **Kern:** Next, First und Best Fit sowie FFD an einer von Hand gerechneten Mini-Instanz (sechs Pakete, Kapazität 10, Gleichstand bei Best Fit); die beiden Handbeispiele; unabhängiger Zulässigkeitsprüfer; Randfälle (leere Eingabe, ein Paket, Paket gleich Kapazität, gleich große Pakete, ungültige Eingaben).
- **Orakel** (`tests/test_oracle_sortieren_einsetzen.py`): Optimum gegen Aufzählung aller Zerlegungen (n ≤ 8, 80 Instanzen) und gegen eine zweite DP über Untermengen (n ≤ 10, 40 Instanzen); die drei Regeln gegen eine bewusst naive Zweitumsetzung (150 Instanzen, zufällige Reihenfolgen); L₂ gegen die Rechnung über alle ganzzahligen α (200 Instanzen); Eigenschaften mit exaktem Optimum: FFD ≥ OPT ≥ L₂ ≥ L₁, FFD ≤ 11/9·OPT + 6/9 (exakte Bruchrechnung), Next Fit ≤ 2·OPT; die konstruierte Instanz.
- **Messraster:** jede der 16 Zellen wird frisch gerechnet und exakt mit `sei_precomputed.json` verglichen (`tests/test_claims.py`).
- **Verdikte:** alle Zweige und Schwellen an von Hand gesetzten Werten (`tests/test_verdicts.py`), je Preset die erwartete Art.
- **Presets und Layout:** vollständig, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung; Schnellstart oben in der Seitenleiste, fester Kopf, genau das passende Preset hervorgehoben (`tests/test_layout.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jede Auswahl in jedem Wert, Startzahl an den Grenzen) und Footer-Test.
- **Tests gesamt:** 113, Laufzeit je nach Rechner rund zwei bis drei Minuten (ohne Parallelisierung).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `generate_precomputed.py` | erzeugt `sei_precomputed.json` (Messraster); `--check` vergleicht |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `sei_algorithm.py` | Kern: Reihenfolgen, Regeln, Schranken, exaktes Optimum, Zulässigkeitsprüfer |
| `sei_constants.py` | Beispiele, Reglerwerte, Messraster, Farben, Presets, Text der Annahmen |
| `sei_evaluation.py` | Analyse, Verdikte, Messzellen |
| `sei_layout.py` | Fester Kopf (Stylesheet) |
| `sei_precomputed.json` | vorberechnete Summen des Messrasters |
| `sei_presets.py` | Permalink (Begrenzen), Presets (Schnellstart, aktives Preset hervorgehoben), Würfel-Button |
| `sei_scenario.py` | Instanzen: Handbeispiele und Zufallsinstanzen mit festen Seeds |
| `sei_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Mini-Instanz und Handrechnung, Orakel, Randfälle, Verdikte, Presets, Layout, Messraster und Zahlen der README, AppTest-Rauchtest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **PDF-Export des Packplans:** die Demo zeigt zwölf Pakete; ein Export bräuchte `fpdf2` und trüge nichts zur Frage bei.
- **Zwei Grenzen (Volumen und Gewicht), Rechtecke, Quader, Reihenfolge suchen:** spätere Stücke der Reihe.
- **Optimum über zwölf Pakete:** bräuchte ein Modell mit Spaltenerzeugung oder Arc-Flow, nicht Gegenstand dieses Stücks.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit und Plotly.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
