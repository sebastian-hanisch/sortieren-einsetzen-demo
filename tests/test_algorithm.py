"""Kern an der Mini-Instanz von Hand und an den beiden Handbeispielen der App (DEMO-PLAYBOOK §1b).

Handrechnung Mini-Instanz (Kapazität 10, Größen 2, 5, 4, 7, 1, 3 mit Nummern 0 bis 5, Lieferreihenfolge):
  Next Fit:   2 -> C1; 5 -> C1 (7); 4 -> 11 > 10, neuer C2; 7 -> 11 > 10, neuer C3; 1 -> C3 (8); 3 -> 11 > 10, neuer C4.   => [[0,1],[2],[3,4],[5]]
  First Fit:  2, 5 -> C1 (7); 4 -> C2; 7 -> C3; 1 -> C1 (8); 3 -> C1 passt nicht (11), C2 (4 + 3 = 7).                      => [[0,1,4],[2,5],[3]]
  Best Fit:   wie First Fit bis zur 1: sie passt in C1 (Rest 2), C2 (Rest 5), C3 (Rest 2); Gleichstand, der frühere C1 gewinnt (8);
              die 3 passt nicht in C1, in C2 mit Rest 3, in C3 mit Rest 0 => C3.                                              => [[0,1,4],[2],[3,5]]
  FFD:        Reihenfolge 7, 5, 4, 3, 2, 1 (Nummern 3, 1, 2, 5, 0, 4): 7 -> C1; 5 -> C2; 4 -> C2 (9); 3 -> C1 (10); 2 -> neuer C3;
              1 -> C2 (10).                                                                                                    => [[3,5],[1,2,4],[0]]
  Schranken:  Summe 22, L1 = ceil(22/10) = 3. L2 bei alpha = 0: J2 = {7} (freier Platz 3), J3 = {2, 5, 4, 1, 3} mit Summe 15, also 1 + ceil((15 - 3)/10) = 3;
              bei alpha = 3: J3 = {5, 4, 3} mit Summe 12, also 1 + ceil((12 - 3)/10) = 2; das Maximum ist 3.
"""

import pytest

import sei_algorithm as A
import sei_constants as C
import sei_evaluation as ev
from sei_scenario import beispiel


def test_next_fit_auf_der_mini_instanz(mini):
    assert A.pack(mini.sizes, A.reihenfolge(mini.sizes, 0), mini.cap, 0) == [[0, 1], [2], [3, 4], [5]]


def test_first_fit_auf_der_mini_instanz(mini):
    assert A.pack(mini.sizes, A.reihenfolge(mini.sizes, 0), mini.cap, 1) == [[0, 1, 4], [2, 5], [3]]


def test_best_fit_auf_der_mini_instanz_mit_gleichstand_zugunsten_des_frueheren(mini):
    assert A.pack(mini.sizes, A.reihenfolge(mini.sizes, 0), mini.cap, 2) == [[0, 1, 4], [2], [3, 5]]


def test_ffd_auf_der_mini_instanz(mini):
    assert A.reihenfolge(mini.sizes, 1) == [3, 1, 2, 5, 0, 4]
    assert A.pack(mini.sizes, A.reihenfolge(mini.sizes, 1), mini.cap, 1) == [[3, 5], [1, 2, 4], [0]]
    assert A.ffd(mini.sizes, mini.cap) == 3


def test_schranken_und_optimum_der_mini_instanz(mini):
    assert A.l1(mini.sizes, mini.cap) == 3
    assert A.l2(mini.sizes, mini.cap) == 3
    assert A.optimum(mini.sizes, mini.cap) == 3


def test_gross_zuerst_ist_stabil_bei_gleichen_groessen():
    assert A.reihenfolge((3, 5, 3, 5, 4), 1) == [1, 3, 4, 0, 2]


def test_zufallsreihenfolge_ist_eine_feste_permutation_je_startzahl():
    sizes = tuple(range(1, 13))
    erste = A.reihenfolge(sizes, 2, 7)
    assert sorted(erste) == list(range(12))
    assert erste == A.reihenfolge(sizes, 2, 7)


# --- die beiden Handbeispiele der App (Phase-0-Rechnung, von Hand nachgerechnet) -------------------------------------------------------------


def test_beispiel_1_sieben_gegen_fuenf():
    inst = beispiel(0)
    assert sum(inst.sizes) == 459 and A.l1(inst.sizes, inst.cap) == 5 and A.optimum(inst.sizes, inst.cap) == 5
    r = ev.raster(inst, 0)
    assert r[0] == (7, 7, 7)           # wie geliefert: Next Fit, First Fit, Best Fit je 7 Container
    assert r[1] == (7, 5, 5)           # größte zuerst: Next Fit 7, First Fit 5, Best Fit 5


def test_beispiel_1_ffd_von_hand():
    """Größte zuerst: 53, 51, 51, 50, 47, 44, 42, 35, 30, 23, 19, 14 -> 53+47, 51+44, 51+42, 50+35+14, 30+23+19."""
    inst = beispiel(0)
    bins = A.pack(inst.sizes, A.reihenfolge(inst.sizes, 1), inst.cap, 1)
    assert sorted(sorted(inst.sizes[i] for i in b) for b in bins) == sorted([[47, 53], [44, 51], [42, 51], [14, 35, 50], [19, 23, 30]])


def test_beispiel_2():
    inst = beispiel(1)
    assert sum(inst.sizes) == 467 and A.l1(inst.sizes, inst.cap) == 5 and A.optimum(inst.sizes, inst.cap) == 5
    r = ev.raster(inst, 0)
    assert r[0] == (7, 6, 6) and r[1] == (7, 5, 5)


def test_alle_ergebnisse_sind_zulaessige_packungen():
    for b in (0, 1):
        inst = beispiel(b)
        for o in C.ORDNUNGEN:
            for r in C.REGELN:
                bins = A.pack(inst.sizes, A.reihenfolge(inst.sizes, o, 3), inst.cap, r)
                assert A.container_pruefen(inst.sizes, bins, inst.cap), (b, o, r)


def test_container_pruefer_erkennt_fehler():
    sizes = (6, 5, 4)
    assert A.container_pruefen(sizes, [[0, 2], [1]], 10)
    assert not A.container_pruefen(sizes, [[0, 1], [2]], 10)        # 11 > 10
    assert not A.container_pruefen(sizes, [[0, 2], [1], [1]], 10)   # Paket 1 doppelt
    assert not A.container_pruefen(sizes, [[0, 2]], 10)             # Paket 1 fehlt
    assert not A.container_pruefen(sizes, [[0, 2], [1], []], 10)    # leerer Container


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_analyse_stimmt_mit_dem_kern_ueberein(regel):
    a = ev.analyse(ev.Settings(0, 1, regel, 7))
    assert a.count == len(a.bins) == A.anzahl(a.inst.sizes, 1, regel, a.inst.cap)
