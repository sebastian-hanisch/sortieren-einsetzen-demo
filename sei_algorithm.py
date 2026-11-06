"""Kern: Reihenfolge, Platzierungsregeln (Next Fit, First Fit, Best Fit), Schranken L1 und L2, exaktes Optimum.

Eine Packung entsteht aus einer Reihenfolge der Pakete und einer Regel, wohin das nächste Paket kommt (Dekodierer). Alle Funktionen sind rein
und nehmen Paketgrößen als ganze Zahlen; Container werden als Listen von Paketnummern (Index in der Lieferreihenfolge) zurückgegeben."""

import math
import random

# ------------------------------------------------------------------------------------------------------------------------------------------
# Reihenfolgen


def reihenfolge(sizes, ordnung: int, seed: int = 0) -> list[int]:
    """Permutation der Paketnummern. 0: wie geliefert, 1: größte zuerst (Gleichstand: kleinere Nummer zuerst), 2: zufällig mit fester Startzahl."""
    idx = list(range(len(sizes)))
    if ordnung == 0:
        return idx
    if ordnung == 1:
        return sorted(idx, key=lambda i: (-sizes[i], i))
    if ordnung == 2:
        random.Random(seed).shuffle(idx)
        return idx
    raise ValueError(f"unbekannte Reihenfolge {ordnung!r}")


# ------------------------------------------------------------------------------------------------------------------------------------------
# Platzierungsregeln


def pack(sizes, order, cap: int, regel: int) -> list[list[int]]:
    """Packt die Pakete in der Reihenfolge `order` mit der Regel `regel` (0 Next Fit, 1 First Fit, 2 Best Fit); liefert die Container.

    Next Fit: nur der zuletzt geöffnete Container wird geprüft. First Fit: der erste Container mit genug Platz. Best Fit: unter den Containern mit genug
    Platz der mit dem wenigsten freien Platz danach (Gleichstand: der früher geöffnete)."""
    if sorted(order) != list(range(len(sizes))):
        raise ValueError("order muss eine Permutation der Paketnummern sein")
    if any(s <= 0 or s > cap for s in sizes):
        raise ValueError("Paketgröße muss zwischen 1 und der Kapazität liegen")
    bins: list[list[int]] = []
    loads: list[int] = []
    for i in order:
        s = sizes[i]
        ziel = -1
        if regel == 0:
            if loads and loads[-1] + s <= cap:
                ziel = len(loads) - 1
        elif regel == 1:
            for b, load in enumerate(loads):
                if load + s <= cap:
                    ziel = b
                    break
        elif regel == 2:
            rest_best = None
            for b, load in enumerate(loads):
                rest = cap - load - s
                if rest >= 0 and (rest_best is None or rest < rest_best):
                    rest_best, ziel = rest, b
        else:
            raise ValueError(f"unbekannte Regel {regel!r}")
        if ziel < 0:
            bins.append([i])
            loads.append(s)
        else:
            bins[ziel].append(i)
            loads[ziel] += s
    return bins


def anzahl(sizes, ordnung: int, regel: int, cap: int, seed: int = 0) -> int:
    return len(pack(sizes, reihenfolge(sizes, ordnung, seed), cap, regel))


def ffd(sizes, cap: int) -> int:
    """First Fit Decreasing: größte zuerst, erster passender Container."""
    return anzahl(sizes, 1, 1, cap)


def bfd(sizes, cap: int) -> int:
    """Best Fit Decreasing: größte zuerst, passendster Container."""
    return anzahl(sizes, 1, 2, cap)


def container_pruefen(sizes, bins, cap: int) -> bool:
    """Unabhängiger Zulässigkeitsprüfer: jedes Paket genau einmal, keine Überfüllung, keine leeren Container."""
    gesehen = sorted(i for b in bins for i in b)
    return gesehen == list(range(len(sizes))) and all(b and sum(sizes[i] for i in b) <= cap for b in bins)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Schranken


def l1(sizes, cap: int) -> int:
    """Volumenschranke: Summe der Größen durch die Kapazität, aufgerundet."""
    return -(-sum(sizes) // cap) if sizes else 0


def l2(sizes, cap: int) -> int:
    """Schranke L2 nach Martello und Toth: Pakete über der halben Kapazität brauchen je einen eigenen Container, und die kleineren füllen deren Restplatz.

    Für jedes alpha (null und jede Paketgröße bis zur halben Kapazität) werden J1 = {s > cap - alpha}, J2 = {cap - alpha >= s > cap/2} und
    J3 = {cap/2 >= s >= alpha} gebildet; L(alpha) = |J1| + |J2| + max(0, ceil((Summe J3 - (|J2| cap - Summe J2)) / cap)); L2 ist das Maximum."""
    best = l1(sizes, cap)
    for alpha in {0} | {s for s in sizes if 2 * s <= cap}:
        j1 = [s for s in sizes if s > cap - alpha]
        j2 = [s for s in sizes if cap - alpha >= s and 2 * s > cap]
        j3 = [s for s in sizes if 2 * s <= cap and s >= alpha]
        frei = len(j2) * cap - sum(j2)
        extra = max(0, -(-(sum(j3) - frei) // cap)) if j3 else 0
        best = max(best, len(j1) + len(j2) + extra)
    return best


# ------------------------------------------------------------------------------------------------------------------------------------------
# Exaktes Optimum


def optimum(sizes, cap: int, limit: int = 12):
    """Kleinste mögliche Containerzahl per Teilmengen-DP, oder None, wenn mehr als `limit` Pakete vorliegen.

    dp[Menge] = (Container, Füllung des letzten) lexikographisch minimal; ein Paket kommt entweder in den letzten Container oder in einen neuen."""
    n = len(sizes)
    if n > limit:
        return None
    if n == 0:
        return 0
    full = (1 << n) - 1
    inf = (n + 1, cap + 1)
    dp = [inf] * (full + 1)
    dp[0] = (1, 0)
    for mask in range(full + 1):
        b, last = dp[mask]
        if b > n:
            continue
        for i in range(n):
            if mask >> i & 1:
                continue
            s = sizes[i]
            nxt = (b, last + s) if last + s <= cap else (b + 1, s)
            m2 = mask | (1 << i)
            if nxt < dp[m2]:
                dp[m2] = nxt
    return dp[full][0]
