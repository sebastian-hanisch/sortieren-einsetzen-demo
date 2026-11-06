"""Kennzahlen, Verdikt-Logik und das Messraster (vorberechnet in sei_precomputed.json, erzeugt von generate_precomputed.py)."""

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import sei_algorithm as A
import sei_constants as C
from sei_scenario import Instance, beispiel, mess_seed, zufallsinstanz

PRECOMPUTED = Path(__file__).resolve().parent / "sei_precomputed.json"
GAIN_SCHWELLE = 1.0   # ab so vielen Containern im Mittel nennt das Verdikt des Messrasters das Sortieren „deutlich“


@dataclass(frozen=True)
class Settings:
    beispiel: int = 0
    ordnung: int = 0
    regel: int = 1
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True)
class Analysis:
    inst: Instance
    order: tuple          # gewählte Reihenfolge (Paketnummern)
    bins: tuple           # Container als Tupel von Paketnummern
    count: int
    schranke_l1: int
    schranke_l2: int
    opt: object           # exaktes Optimum (int) oder None bei mehr als OPT_LIMIT Paketen
    raster: tuple         # raster[ordnung][regel] = Containerzahl, 3 x 3
    settings: Settings


def raster(inst: Instance, seed: int) -> tuple:
    """Containerzahl für jede Kombination aus Reihenfolge (Zeile) und Regel (Spalte)."""
    return tuple(tuple(A.anzahl(inst.sizes, o, r, inst.cap, seed) for r in sorted(C.REGELN)) for o in sorted(C.ORDNUNGEN))


def analyse(s: Settings) -> Analysis:
    inst = beispiel(s.beispiel)
    order = A.reihenfolge(inst.sizes, s.ordnung, s.seed)
    bins = A.pack(inst.sizes, order, inst.cap, s.regel)
    assert A.container_pruefen(inst.sizes, bins, inst.cap)
    return Analysis(inst, tuple(order), tuple(tuple(b) for b in bins), len(bins), A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap),
                    A.optimum(inst.sizes, inst.cap, C.OPT_LIMIT), raster(inst, s.seed), s)


# ------------------------------------------------------------------------------------------------------------------------------------------
# Verdikte (reine Funktionen: (Art, Text))


def verdict_aktuell(a: Analysis) -> tuple[str, str]:
    """Verdikt zur gewählten Kombination: Containerzahl gegen Schranke und exaktes Optimum."""
    wie = f"{C.ORDNUNG_MIT[a.settings.ordnung]} und {C.REGEL_KURZ[a.settings.regel]}"
    if a.opt is None:
        return "info", f"Mit {wie} brauchen die Pakete **{a.count}** Container; die untere Schranke ist {a.schranke_l2}. Das Optimum ist bei dieser Paketzahl nicht berechnet."
    if a.count == a.opt:
        return "success", f"Mit {wie} brauchen die Pakete **{a.count}** Container. Das ist das Optimum (die Volumenschranke allein ergäbe {a.schranke_l1})."
    zu_viel = a.count - a.opt
    return "warning", f"Mit {wie} brauchen die Pakete **{a.count}** Container, das Optimum ist **{a.opt}**: {zu_viel} zu viel."


def spannen(r: tuple) -> tuple[int, int, int]:
    """(a, b, c) des 3 x 3 Rasters (Zeile = Reihenfolge, Spalte = Regel in der Reihenfolge Next Fit, First Fit, Best Fit).

    a = größter Unterschied zwischen First Fit und Best Fit in einer Zeile; b = größter Unterschied zwischen den Reihenfolgen in der Spalte First Fit oder
    Best Fit; c = größter Mehrbedarf von Next Fit gegenüber dem besseren der beiden anderen Regeln in derselben Zeile."""
    a = max(abs(z[1] - z[2]) for z in r)
    b = max(max(r[o][c] for o in range(len(r))) - min(r[o][c] for o in range(len(r))) for c in (1, 2))
    c = max(max(0, z[0] - min(z[1], z[2])) for z in r)
    return a, b, c


def verdict_raster(a: Analysis) -> tuple[str, str]:
    """Kernfrage: Was verändert die Containerzahl mehr, die Reihenfolge oder die Regel? Gezählt über das ganze 3 x 3 Raster, nicht über die gewählte Zelle.

    Verglichen werden First Fit und Best Fit (beide prüfen alle offenen Container); Next Fit prüft nur den letzten und steht gesondert."""
    regel, ordnung, nf = spannen(a.raster)
    teil = (f"Zwischen First Fit und Best Fit unterscheidet sich die Containerzahl über alle drei Reihenfolgen um höchstens **{regel}**; "
            f"ein Wechsel der Reihenfolge verändert sie bei diesen beiden Regeln um bis zu **{ordnung}**. "
            f"Next Fit, das nur den zuletzt geöffneten Container prüft, braucht bis zu **{nf}** Container mehr als der bessere der beiden anderen bei gleicher Reihenfolge.")
    if ordnung > regel:
        return "success", teil + " Hier zählt die Reihenfolge mehr als die Wahl zwischen First Fit und Best Fit."
    if ordnung == regel:
        return "info", teil + " Beide wirken hier gleich stark."
    return "warning", teil + " Hier wirkt die Wahl zwischen First Fit und Best Fit stärker als die Reihenfolge."


# ------------------------------------------------------------------------------------------------------------------------------------------
# Messraster


def messzelle(verteilung: int, n_index: int, seeds: int = C.SEEDS_PER_CELL) -> dict:
    """Rechnet eine Zelle des Messrasters frisch: Summen (ganze Zahlen, damit der Vergleich exakt ist) über `seeds` feste Instanzen.

    ueber_l2[v] = Summe über die Instanzen von (Container des Verfahrens minus Schranke L2); gleich_l1[v], gleich_l2[v] = Zahl der Instanzen, in denen das
    Verfahren die Schranke genau trifft; ffd_ungleich_bfd = Zahl der Instanzen, in denen FFD und BFD verschieden viele Container brauchen."""
    _, _, lo, hi = C.VERTEILUNGEN[verteilung]
    n = C.MESS_N[n_index]
    out = {"ueber_l2": dict.fromkeys(C.VERFAHREN, 0), "gleich_l1": dict.fromkeys(C.VERFAHREN, 0), "gleich_l2": dict.fromkeys(C.VERFAHREN, 0), "ffd_ungleich_bfd": 0}
    kombi = {"NF": (0, 0), "FF": (0, 1), "BF": (0, 2), "FFD": (1, 1), "BFD": (1, 2)}
    for j in range(seeds):
        inst = zufallsinstanz(lo, hi, n, mess_seed(verteilung, n_index, j))
        s1, s2 = A.l1(inst.sizes, inst.cap), A.l2(inst.sizes, inst.cap)
        zahlen = {v: A.anzahl(inst.sizes, o, r, inst.cap) for v, (o, r) in kombi.items()}
        for v, z in zahlen.items():
            out["ueber_l2"][v] += z - s2
            out["gleich_l1"][v] += z == s1
            out["gleich_l2"][v] += z == s2
        out["ffd_ungleich_bfd"] += zahlen["FFD"] != zahlen["BFD"]
    return out


@lru_cache(maxsize=1)
def vorberechnet() -> dict:
    return json.loads(PRECOMPUTED.read_text(encoding="utf-8"))


def zelle_schluessel(verteilung: int, n_index: int) -> str:
    return f"{C.VERTEILUNGEN[verteilung][0]}|{C.MESS_N[n_index]}"


def zeile(verteilung: int, n_index: int, daten: dict | None = None) -> dict:
    """Mittelwerte und Anteile einer Zelle aus den vorberechneten Summen."""
    daten = daten or vorberechnet()
    z = daten["zellen"][zelle_schluessel(verteilung, n_index)]
    k = daten["seeds"]
    return {
        "name": C.VERTEILUNGEN[verteilung][1],
        "n": C.MESS_N[n_index],
        "seeds": k,
        "mittel": {v: z["ueber_l2"][v] / k for v in C.VERFAHREN},
        "anteil_l1": {v: 100.0 * z["gleich_l1"][v] / k for v in C.VERFAHREN},
        "anteil_l2": {v: 100.0 * z["gleich_l2"][v] / k for v in C.VERFAHREN},
        "ffd_ungleich_bfd": z["ffd_ungleich_bfd"],
    }


def verdict_messung(z: dict) -> tuple[str, str]:
    """Verdikt zur gewählten Zelle: Sortieren gegen die Lieferreihenfolge, gemessen in Containern über der Schranke L2."""
    m = z["mittel"]
    gewinn = m["FF"] - m["FFD"]
    kopf = (f"Für »{z['name']}« mit n = {z['n']} Paketen liegen die Container im Mittel über {z['seeds']} Instanzen so weit über der Schranke L2: "
            f"Next Fit {m['NF']:.2f}, First Fit {m['FF']:.2f}, Best Fit {m['BF']:.2f} in Lieferreihenfolge; nach dem Sortieren First Fit {m['FFD']:.2f} und Best Fit {m['BFD']:.2f}.")
    fuss = f" FFD trifft die Volumenschranke L1 in {z['anteil_l1']['FFD']:.1f} % der Instanzen."
    if gewinn >= GAIN_SCHWELLE:
        return "success", kopf + f" Sortieren spart gegenüber First Fit in Lieferreihenfolge im Mittel **{gewinn:.2f}** Container." + fuss
    return "info", kopf + f" Sortieren spart hier gegenüber First Fit in Lieferreihenfolge im Mittel nur **{gewinn:.2f}** Container." + fuss
