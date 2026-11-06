"""Randfälle: leere Eingabe, ein Paket, Paket gleich Kapazität, gleich große Pakete, Gleichstände, ungültige Eingaben."""

import pytest

import sei_algorithm as A
from sei_scenario import Instance, mess_seed, zufallsinstanz


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_leere_eingabe_ergibt_keine_container(regel):
    assert A.pack((), [], 10, regel) == []
    assert A.l1((), 10) == 0 and A.l2((), 10) == 0 and A.optimum((), 10) == 0


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_ein_paket_und_paket_gleich_kapazitaet(regel):
    assert A.pack((7,), [0], 10, regel) == [[0]]
    assert A.pack((10, 10), [0, 1], 10, regel) == [[0], [1]]


@pytest.mark.parametrize("regel", [0, 1, 2])
def test_gleich_grosse_pakete_fuellen_container_genau(regel):
    bins = A.pack((5, 5, 5, 5), [0, 1, 2, 3], 10, regel)
    assert bins == [[0, 1], [2, 3]]


def test_next_fit_oeffnet_nie_wieder_einen_alten_container():
    # 6, 5, 4: First Fit setzt die 4 zu der 6 (10), Next Fit nicht (die 5 steht in C2, 5 + 4 = 9 passt dort, also C2).
    assert A.pack((6, 5, 4), [0, 1, 2], 10, 0) == [[0], [1, 2]]
    # 6, 5, 5, 4: die 4 hätte in C1 gepasst (10); Next Fit prüft nur C2 (5 + 5 = 10 voll) und öffnet C3.
    assert A.pack((6, 5, 5, 4), [0, 1, 2, 3], 10, 0) == [[0], [1, 2], [3]]
    assert A.pack((6, 5, 5, 4), [0, 1, 2, 3], 10, 1) == [[0, 3], [1, 2]]


def test_best_fit_waehlt_den_passendsten_und_bei_gleichstand_den_fruehesten():
    # C1 hat 6 belegt (Rest 4), C2 hat 8 belegt (Rest 2); ein Paket der Größe 2 passt in beide: Best Fit nimmt C2, First Fit C1.
    assert A.pack((6, 8, 2), [0, 1, 2], 10, 2) == [[0], [1, 2]]
    assert A.pack((6, 8, 2), [0, 1, 2], 10, 1) == [[0, 2], [1]]
    # Gleichstand der Reste: früherer Container.
    assert A.pack((6, 6, 4), [0, 1, 2], 10, 2) == [[0, 2], [1]]


def test_gleichstand_beim_sortieren_haelt_die_lieferreihenfolge():
    assert A.reihenfolge((4, 4, 4, 4), 1) == [0, 1, 2, 3]


def test_ungueltige_eingaben_werfen():
    with pytest.raises(ValueError):
        A.pack((11,), [0], 10, 1)          # Paket größer als die Kapazität
    with pytest.raises(ValueError):
        A.pack((0,), [0], 10, 1)           # Größe null
    with pytest.raises(ValueError):
        A.pack((3, 4), [0, 0], 10, 1)      # keine Permutation
    with pytest.raises(ValueError):
        A.pack((3, 4), [0], 10, 1)         # unvollständige Reihenfolge
    with pytest.raises(ValueError):
        A.pack((3, 4), [0, 1], 10, 7)      # unbekannte Regel
    with pytest.raises(ValueError):
        A.reihenfolge((3, 4), 9)           # unbekannte Reihenfolge
    with pytest.raises(ValueError):
        Instance((3, 4), 0)                # Kapazität null
    with pytest.raises(ValueError):
        Instance((3, 12), 10)              # Paket größer als die Kapazität
    with pytest.raises(ValueError):
        Instance((3.5,), 10)               # keine ganze Zahl


def test_zufallsinstanzen_sind_fest_und_liegen_im_bereich():
    a = zufallsinstanz(0.2, 0.8, 50, mess_seed(2, 1, 3))
    assert a == zufallsinstanz(0.2, 0.8, 50, mess_seed(2, 1, 3))
    assert a.n == 50 and all(200 <= s <= 800 for s in a.sizes) and a.cap == 1000
    assert zufallsinstanz(0.2, 0.8, 50, mess_seed(2, 1, 4)) != a


def test_mess_seeds_sind_je_zelle_und_instanz_verschieden():
    seeds = {mess_seed(d, n, j) for d in range(4) for n in range(4) for j in range(200)}
    assert len(seeds) == 4 * 4 * 200
