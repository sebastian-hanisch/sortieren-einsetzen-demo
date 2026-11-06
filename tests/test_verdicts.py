"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier.

Ein Verdikt ist eine reine Funktion (Art, Text). Die Analysen und Zeilen werden von Hand gebaut, nicht aus Seeds gerechnet."""

import sei_constants as C
import sei_evaluation as ev
from sei_scenario import Instance


def _analyse(count, opt, raster=None, ordnung=1, regel=1, l1=5, l2=5):
    raster = raster or ((7, 7, 7), (7, 5, 5), (6, 5, 5))
    inst = Instance((10, 20), 100)
    return ev.Analysis(inst, (0, 1), ((0, 1),), count, l1, l2, opt, raster, ev.Settings(0, ordnung, regel, 7))


# --- verdict_aktuell ------------------------------------------------------------------------------------------------------------------------


def test_aktuell_optimum_getroffen_ist_ein_erfolg_und_nennt_die_volumenschranke():
    kind, text = ev.verdict_aktuell(_analyse(5, 5, ordnung=1, regel=1, l1=4))
    assert kind == "success"
    assert "Mit der Reihenfolge „größte zuerst“ und First Fit brauchen" in text and "**5** Container" in text and "ergäbe 4" in text


def test_aktuell_zu_viele_container_ist_eine_warnung_und_zaehlt_die_differenz():
    kind, text = ev.verdict_aktuell(_analyse(7, 5, ordnung=0, regel=2))
    assert kind == "warning"
    assert "Mit der Lieferreihenfolge und Best Fit brauchen" in text and "**7** Container" in text and "das Optimum ist **5**" in text and "2 zu viel" in text


def test_aktuell_ein_container_zu_viel_steht_im_singular_der_differenz():
    assert "1 zu viel" in ev.verdict_aktuell(_analyse(6, 5))[1]


def test_aktuell_ohne_optimum_nennt_die_schranke():
    kind, text = ev.verdict_aktuell(_analyse(9, None, ordnung=2, regel=0, l2=8))
    assert kind == "info" and "**9** Container" in text and "untere Schranke ist 8" in text and "Mit einer zufälligen Reihenfolge und Next Fit brauchen" in text


# --- spannen und verdict_raster ------------------------------------------------------------------------------------------------------------


def test_spannen_an_handgesetzten_rastern():
    # Zeilen = Reihenfolgen, Spalten = Next, First, Best.
    assert ev.spannen(((7, 7, 7), (7, 5, 5), (6, 5, 5))) == (0, 2, 2)
    assert ev.spannen(((7, 6, 6), (7, 5, 5), (6, 6, 6))) == (0, 1, 2)
    assert ev.spannen(((5, 5, 6), (5, 7, 5), (5, 5, 5))) == (2, 2, 0)   # First und Best Fit verschieden in Zeile 2; Next Fit nie schlechter
    assert ev.spannen(((4, 4, 4), (4, 4, 4), (4, 4, 4))) == (0, 0, 0)
    # Nur die Best-Fit-Spalte schwankt (5, 8, 5): b muss sie mitzählen; a ist der Unterschied zwischen First und Best Fit in Zeile 2.
    assert ev.spannen(((5, 5, 5), (5, 5, 8), (5, 5, 5))) == (3, 3, 0)
    # Nur die First-Fit-Spalte schwankt (5, 8, 5).
    assert ev.spannen(((5, 5, 5), (5, 8, 5), (5, 5, 5))) == (3, 3, 0)
    # Next Fit braucht mehr als beide anderen (Zeile 2: 9 gegen 4 und 6): c = 5.
    assert ev.spannen(((4, 4, 4), (9, 4, 6), (4, 4, 4))) == (2, 2, 5)


def test_raster_reihenfolge_wirkt_staerker_ist_ein_erfolg_mit_beiden_zahlen():
    kind, text = ev.verdict_raster(_analyse(7, 5, raster=((7, 7, 7), (7, 5, 5), (6, 5, 5))))
    assert kind == "success"
    assert "höchstens **0**" in text and "bis zu **2**" in text and "bis zu **2** Container mehr" in text and "zählt die Reihenfolge mehr" in text


def test_raster_gleichstand_ist_info():
    kind, text = ev.verdict_raster(_analyse(5, 5, raster=((5, 6, 5), (5, 5, 6), (5, 5, 5))))   # a = 1, b = 1
    assert kind == "info" and "gleich stark" in text


def test_raster_regel_deutlich_staerker_ist_eine_warnung():
    r = ((5, 5, 8), (5, 5, 8), (5, 5, 8))          # a = 3, b = 0
    kind, text = ev.verdict_raster(_analyse(5, 5, raster=r))
    assert ev.spannen(r) == (3, 0, 0)
    assert kind == "warning" and "höchstens **3**" in text and "bis zu **0**" in text and "stärker als die Reihenfolge" in text


# --- verdict_messung -----------------------------------------------------------------------------------------------------------------------


def _zeile(ff, ffd, anteil_l1=40.0):
    return {
        "name": "große Teile (20 bis 80 %)", "n": 200, "seeds": 200,
        "mittel": {"NF": 35.5, "FF": ff, "BF": 5.25, "FFD": ffd, "BFD": ffd},
        "anteil_l1": {v: anteil_l1 for v in C.VERFAHREN}, "anteil_l2": {v: 50.0 for v in C.VERFAHREN}, "ffd_ungleich_bfd": 0,
    }


def test_messung_schwelle_ist_inklusive_bei_einem_container():
    assert ev.verdict_messung(_zeile(2.0, 1.0))[0] == "success"         # genau 1,0 gespart
    assert ev.verdict_messung(_zeile(1.75, 1.0))[0] == "info"           # 0,75 gespart


def test_messung_nennt_alle_zahlen_und_den_namen_der_zelle():
    kind, text = ev.verdict_messung(_zeile(7.5, 0.5, anteil_l1=12.0))
    assert kind == "success"
    assert "»große Teile (20 bis 80 %)« mit n = 200" in text and "über 200 Instanzen" in text
    assert "Next Fit 35.50" in text and "First Fit 7.50" in text and "Best Fit 5.25" in text
    assert "First Fit 0.50 und Best Fit 0.50" in text
    assert "**7.00** Container" in text and "in 12 % der Instanzen" in text


def test_messung_info_nennt_den_kleinen_gewinn():
    kind, text = ev.verdict_messung(_zeile(0.5, 0.25))
    assert kind == "info" and "nur **0.25** Container" in text
