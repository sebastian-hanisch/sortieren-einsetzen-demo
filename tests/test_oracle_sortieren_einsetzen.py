"""Orakel-Tests (DEMO-PLAYBOOK §12): jede Kernroutine gegen einen anderen Rechenweg, feste Seeds, zusammen unter 10 Sekunden.

  Optimum (Teilmengen-DP über Bitmasken)    gegen  (a) Aufzählung aller Zerlegungen der Paketmenge in Container (n <= 8),
                                                   (b) zweite DP über Untermengen, O(3^n) (n <= 10).
  Regeln (Next, First, Best Fit)            gegen  eine bewusst naive Zweitumsetzung (Pakete als Listen, Füllung jedes Mal neu summiert).
  Schranke L2                               gegen  die Rechnung über ALLE ganzzahligen alpha statt nur über die Paketgrößen.
  Eigenschaften mit exaktem Optimum (n <= 12): FFD >= OPT >= L2 >= L1; FFD <= 11/9 OPT + 6/9 (Dósa); Next Fit <= 2 OPT.
  Literatur: konstruierte Instanz (502, 254, 252, 246): Optimum 9 durch explizite Packung, FFD 11.
"""

import itertools
import random
from fractions import Fraction

import pytest

import sei_algorithm as A


def instanzen(anzahl, n_lo, n_hi, cap_lo=5, cap_hi=40, seed0=0):
    for seed in range(seed0, seed0 + anzahl):
        rng = random.Random(seed)
        cap = rng.randint(cap_lo, cap_hi)
        n = rng.randint(n_lo, n_hi)
        yield cap, [rng.randint(1, cap) for _ in range(n)]


# --- Orakel für das Optimum -------------------------------------------------------------------------------------------------------------------


def optimum_aufzaehlung(sizes, cap):
    """Kleinste Containerzahl durch Aufzählung aller Zerlegungen (Wachstumszeichenketten: Paket i kommt in einen Container mit Nummer <= bisher + 1)."""
    n = len(sizes)
    if n == 0:
        return 0
    best = n

    def rec(i, loads):
        nonlocal best
        if len(loads) >= best:
            return
        if i == n:
            best = len(loads)
            return
        for b in range(len(loads)):
            if loads[b] + sizes[i] <= cap:
                loads[b] += sizes[i]
                rec(i + 1, loads)
                loads[b] -= sizes[i]
        loads.append(sizes[i])
        rec(i + 1, loads)
        loads.pop()

    rec(0, [])
    return best


def optimum_untermengen(sizes, cap):
    """Zweite DP: g(M) = kleinste Containerzahl für die Menge M; der Container mit dem niedrigsten Paket von M nimmt eine Untermenge auf, die in 'cap' passt."""
    n = len(sizes)
    full = (1 << n) - 1
    summe = [0] * (full + 1)
    for m in range(1, full + 1):
        low = (m & -m).bit_length() - 1
        summe[m] = summe[m & (m - 1)] + sizes[low]
    g = [0] * (full + 1)
    for m in range(1, full + 1):
        low = m & -m
        rest = m ^ low
        sub = rest
        beste = n + 1
        while True:
            t = sub | low
            if summe[t] <= cap and g[m ^ t] + 1 < beste:
                beste = g[m ^ t] + 1
            if sub == 0:
                break
            sub = (sub - 1) & rest
        g[m] = beste
    return g[full]


def test_optimum_stimmt_mit_der_aufzaehlung_ueberein():
    for cap, sizes in instanzen(80, 1, 8):
        assert A.optimum(sizes, cap) == optimum_aufzaehlung(sizes, cap), (cap, sizes)


def test_optimum_stimmt_mit_der_untermengen_dp_ueberein():
    for cap, sizes in instanzen(40, 1, 10, seed0=1000):
        assert A.optimum(sizes, cap) == optimum_untermengen(sizes, cap), (cap, sizes)


def test_optimum_randfaelle():
    assert A.optimum([], 10) == 0
    assert A.optimum([10], 10) == 1
    assert A.optimum([10, 10, 10], 10) == 3           # jedes Paket füllt einen Container
    assert A.optimum([5, 5, 5, 5], 10) == 2
    assert A.optimum([1] * 12, 12) == 1
    assert A.optimum([1] * 13, 12, limit=12) is None  # mehr Pakete als das Limit


# --- Orakel für die Regeln --------------------------------------------------------------------------------------------------------------------


def naiv(sizes, order, cap, regel):
    """Bewusst naive Zweitumsetzung: jeder Container ist eine Liste von Größen; die Füllung wird bei jeder Prüfung neu summiert."""
    container = []
    for i in order:
        s = sizes[i]
        kandidaten = list(range(len(container))) if regel != 0 else ([len(container) - 1] if container else [])
        passend = [b for b in kandidaten if sum(container[b]) + s <= cap]
        if not passend:
            container.append([s])
            continue
        if regel == 2:
            ziel = min(passend, key=lambda b: (cap - sum(container[b]) - s, b))
        else:
            ziel = passend[0]
        container[ziel].append(s)
    return [sorted(c) for c in container]


def test_regeln_stimmen_mit_der_naiven_zweitumsetzung_ueberein():
    for cap, sizes in instanzen(150, 0, 14, seed0=2000):
        rng = random.Random(len(sizes) + cap)
        order = list(range(len(sizes)))
        rng.shuffle(order)
        for regel in (0, 1, 2):
            bins = A.pack(sizes, order, cap, regel)
            assert [sorted(sizes[i] for i in b) for b in bins] == naiv(sizes, order, cap, regel), (cap, sizes, order, regel)
            assert A.container_pruefen(sizes, bins, cap)


# --- Orakel für L2 ----------------------------------------------------------------------------------------------------------------------------


def l2_alle_alpha(sizes, cap):
    best = -(-sum(sizes) // cap) if sizes else 0
    for alpha in range(0, cap // 2 + 1):
        j1 = sum(1 for s in sizes if s > cap - alpha)
        j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
        j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
        extra = max(0, -(-(sum(j3) - (len(j2) * cap - sum(j2))) // cap))
        best = max(best, j1 + len(j2) + extra)
    return best


def test_l2_stimmt_mit_der_rechnung_ueber_alle_alpha_ueberein():
    for cap, sizes in instanzen(200, 0, 20, seed0=3000):
        assert A.l2(sizes, cap) == l2_alle_alpha(sizes, cap), (cap, sizes)


# --- Eigenschaften mit exaktem Optimum ----------------------------------------------------------------------------------------------------------


def test_schranken_und_verfahren_liegen_in_der_richtigen_ordnung():
    for cap, sizes in instanzen(60, 1, 12, seed0=4000):
        opt = A.optimum(sizes, cap)
        assert A.l1(sizes, cap) <= A.l2(sizes, cap) <= opt, (cap, sizes)
        for o, r in itertools.product((0, 1, 2), (0, 1, 2)):
            assert A.anzahl(sizes, o, r, cap, seed=5) >= opt, (cap, sizes, o, r)


def test_ffd_haelt_die_guetegarantie_von_dosa():
    """FFD <= 11/9 OPT + 6/9 mit exakter Bruchrechnung (Fachkanon: Dósa 2007; hier an kleinen Instanzen gegen das exakte Optimum geprüft)."""
    for cap, sizes in instanzen(60, 1, 12, seed0=5000):
        opt = A.optimum(sizes, cap)
        assert Fraction(A.ffd(sizes, cap)) <= Fraction(11, 9) * opt + Fraction(6, 9), (cap, sizes)


def test_next_fit_braucht_hoechstens_das_doppelte_des_optimums():
    for cap, sizes in instanzen(60, 1, 12, seed0=6000):
        assert A.anzahl(sizes, 0, 0, cap) <= 2 * A.optimum(sizes, cap), (cap, sizes)


# --- Literatur: die konstruierte Instanz --------------------------------------------------------------------------------------------------------


def test_konstruierte_instanz_optimum_neun_ffd_elf():
    """Kapazität 1000; 6 Pakete 502, 6 Pakete 254, 6 Pakete 252, 12 Pakete 246. Eine explizite Packung mit 9 Containern (6 x 502+252+246 und 3 x 254+254+246+246)
    zeigt Optimum <= 9; die Volumenschranke 9000/1000 = 9 zeigt Optimum >= 9. FFD braucht 11 (Verhältnis 11/9)."""
    sizes = [502] * 6 + [254] * 6 + [252] * 6 + [246] * 12
    cap = 1000
    assert A.l1(sizes, cap) == 9
    idx = {g: [i for i, s in enumerate(sizes) if s == g] for g in (502, 254, 252, 246)}
    packung = [[idx[502][k], idx[252][k], idx[246][k]] for k in range(6)]
    packung += [[idx[254][2 * k], idx[254][2 * k + 1], idx[246][6 + 2 * k], idx[246][6 + 2 * k + 1]] for k in range(3)]
    assert len(packung) == 9 and A.container_pruefen(sizes, packung, cap)
    assert A.ffd(sizes, cap) == 11
    assert A.bfd(sizes, cap) == 11


@pytest.mark.parametrize("k", [1, 2, 3])
def test_konstruierte_instanz_waechst_mit_dem_vielfachen(k):
    sizes = [502] * (6 * k) + [254] * (6 * k) + [252] * (6 * k) + [246] * (12 * k)
    assert A.l1(sizes, 1000) == 9 * k and A.ffd(sizes, 1000) == 11 * k
