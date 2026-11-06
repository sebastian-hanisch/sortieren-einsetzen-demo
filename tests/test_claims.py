"""Jede Zahl der README und der App-Texte, nachgerechnet (DEMO-PLAYBOOK §4 und §11a).

* Das vorberechnete Raster (sei_precomputed.json) wird je Zelle frisch gerechnet und exakt verglichen (ganze Zahlen).
* Die Befunde der README werden aus denselben Auswertungsfunktionen wie in der App berechnet, über das GANZE Raster gezählt und als Text in der README gesucht.
* Der Text des Expanders „Annahmen, Grenzen und bekannte Probleme“ steht wörtlich in der README.
Dezimalzahlen stehen in der README mit Komma, in der App mit Punkt; `de` übersetzt."""

import itertools
from pathlib import Path

import pytest

import sei_algorithm as A
import sei_constants as C
import sei_evaluation as ev
from sei_scenario import beispiel

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
ZELLEN = list(itertools.product(range(len(C.VERTEILUNGEN)), range(len(C.MESS_N))))


def de(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",")


def alle_zeilen():
    return {(d, ni): ev.zeile(d, ni) for d, ni in ZELLEN}


@pytest.mark.parametrize("d,ni", ZELLEN)
def test_vorberechnetes_raster_stimmt_mit_frischer_rechnung(d, ni):
    assert ev.messzelle(d, ni) == ev.vorberechnet()["zellen"][ev.zelle_schluessel(d, ni)]


def test_raster_hat_alle_zellen_und_die_zahl_der_instanzen():
    daten = ev.vorberechnet()
    assert daten["seeds"] == C.SEEDS_PER_CELL == 200 and daten["cap"] == C.MESS_CAP == 1000
    assert set(daten["zellen"]) == {ev.zelle_schluessel(d, ni) for d, ni in ZELLEN} and len(ZELLEN) == 16


# --- Befund: große Teile, n = 200 ---------------------------------------------------------------------------------------------------------------


def test_readme_nennt_die_zahlen_der_zelle_grosse_teile_n_200():
    m = ev.zeile(2, 3)["mittel"]
    zeile = f"Next Fit {de(m['NF'])}, First Fit {de(m['FF'])}, Best Fit {de(m['BF'])}, FFD {de(m['FFD'])}, BFD {de(m['BFD'])}"
    assert zeile in README
    assert m["NF"] > m["FF"] > m["BF"] > m["FFD"]


# --- Befund: FFD und BFD ------------------------------------------------------------------------------------------------------------------------


def test_ffd_und_bfd_unterscheiden_sich_in_einer_von_3200_instanzen():
    summe = sum(z["ffd_ungleich_bfd"] for z in alle_zeilen().values())
    assert summe == 1
    assert len(ZELLEN) * C.SEEDS_PER_CELL == 3200
    assert "**1 von 3200**" in README
    gleich = sum(abs(z["mittel"]["FFD"] - z["mittel"]["BFD"]) < 1e-12 for z in alle_zeilen().values())
    assert gleich == 15 and "in **15 von 16** Zellen" in README


# --- Befund: Best Fit gegen First Fit gegen Sortieren -------------------------------------------------------------------------------------------


def test_best_fit_ist_in_allen_zellen_hoechstens_so_schlecht_wie_first_fit_und_in_13_besser():
    z = alle_zeilen()
    assert all(v["mittel"]["BF"] <= v["mittel"]["FF"] for v in z.values())
    assert sum(v["mittel"]["BF"] < v["mittel"]["FF"] for v in z.values()) == 13
    assert "in **16 von 16** Zellen höchstens so viele Container wie First Fit" in README and "in **13** Zellen weniger" in README


def test_sortieren_spart_mindestens_einen_container_in_7_von_16_zellen_und_ist_viel_staerker_als_best_fit():
    z = alle_zeilen()
    gewinn = {k: v["mittel"]["FF"] - v["mittel"]["FFD"] for k, v in z.items()}
    assert sum(g >= ev.GAIN_SCHWELLE for g in gewinn.values()) == 7
    assert "in **7 von 16** Zellen mindestens einen Container" in README
    # Die neun anderen Zellen: kleine Teile (alle n), mittlere Teile mit n <= 100, große und breite Teile mit n = 20.
    klein = {k for k, g in gewinn.items() if g < ev.GAIN_SCHWELLE}
    assert klein == {(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2), (2, 0), (3, 0)}
    # In den 13 Zellen, in denen Best Fit gewinnt, ist der Gewinn durch Sortieren mindestens so viel mal größer.
    verhaeltnis = [gewinn[k] / (v["mittel"]["FF"] - v["mittel"]["BF"]) for k, v in z.items() if v["mittel"]["FF"] > v["mittel"]["BF"]]
    assert len(verhaeltnis) == 13 and 3.6 <= min(verhaeltnis) < 3.7
    assert "mindestens **3,6-mal**" in README


# --- Befund: FFD trifft die Volumenschranke -----------------------------------------------------------------------------------------------------


def test_readme_nennt_die_anteile_ffd_trifft_l1():
    z = alle_zeilen()
    for d, name in ((0, "kleine"), (1, "mittlere"), (2, "große"), (3, "breite")):
        werte = [z[(d, ni)]["anteil_l1"]["FFD"] for ni in range(4)]
        zeile = " / ".join(de(w, 1) for w in werte)
        assert f"{name} Teile: {zeile} %" in README, (name, zeile)
    assert min(z[(0, ni)]["anteil_l1"]["FFD"] for ni in range(4)) >= 96.0


def test_ffd_trifft_l2_in_15_von_16_zellen_nicht_in_allen_instanzen():
    z = alle_zeilen()
    assert sum(v["anteil_l2"]["FFD"] < 100.0 for v in z.values()) == 15
    assert z[(0, 1)]["anteil_l2"]["FFD"] == 100.0


# --- Handbeispiele -------------------------------------------------------------------------------------------------------------------------------


def test_readme_nennt_die_handbeispiele():
    a = ev.analyse(ev.Settings(0, 0, 1, 7))
    assert (sum(a.inst.sizes), a.schranke_l1, a.opt) == (459, 5, 5) and a.raster[0] == (7, 7, 7) and a.raster[1] == (7, 5, 5)
    b = ev.analyse(ev.Settings(1, 0, 1, 7))
    assert (sum(b.inst.sizes), b.schranke_l1, b.opt) == (467, 5, 5) and b.raster[0] == (7, 6, 6) and b.raster[1] == (7, 5, 5)
    for snippet in ("Summe 459", "Next Fit, First Fit und Best Fit **7, 7, 7**", "**7, 5, 5**", "Summe 467", "**7, 6, 6**"):
        assert snippet in README, snippet


def test_beispiele_haben_zwoelf_pakete_und_kapazitaet_100():
    for i in C.BEISPIELE:
        assert beispiel(i).n == 12 and beispiel(i).cap == 100
    assert C.OPT_LIMIT == 12


def test_konstruierte_instanz_in_app_und_readme():
    sizes = [502] * 6 + [254] * 6 + [252] * 6 + [246] * 12
    assert A.ffd(sizes, 1000) == 11 and A.l1(sizes, 1000) == 9
    assert "502, 254, 252 und 246" in README and "braucht FFD 11 Container, das Optimum ist 9" in README
    assert "502, 254, 252 und 246" in (ROOT / "app.py").read_text(encoding="utf-8") and "braucht FFD 11 Container, das Optimum ist 9" in (ROOT / "app.py").read_text(encoding="utf-8")


# --- Texte -----------------------------------------------------------------------------------------------------------------------------------------


def test_annahmen_text_der_app_steht_woertlich_in_der_readme():
    assert C.ASSUMPTIONS_MARKDOWN in README


def test_zahlen_im_annahmen_text_sind_die_der_konstanten():
    assert f"{C.SEEDS_PER_CELL} Instanzen je Zelle" in C.ASSUMPTIONS_MARKDOWN and f"bis {C.OPT_LIMIT} Pakete" in C.ASSUMPTIONS_MARKDOWN
