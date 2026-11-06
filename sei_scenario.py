"""Instanzen: feste Beispiele und Zufallsinstanzen für das Messraster."""

import random
from dataclasses import dataclass

import sei_constants as C


@dataclass(frozen=True)
class Instance:
    sizes: tuple          # Paketgrößen in Lieferreihenfolge, ganzzahlig und positiv
    cap: int = C.CAP      # Kapazität eines Containers

    def __post_init__(self):
        if self.cap <= 0:
            raise ValueError("Kapazität muss positiv sein")
        for s in self.sizes:
            if not isinstance(s, int) or s <= 0 or s > self.cap:
                raise ValueError(f"Paketgröße {s!r} ungültig (ganz, 1 bis {self.cap})")

    @property
    def n(self) -> int:
        return len(self.sizes)


def beispiel(index: int) -> Instance:
    return Instance(tuple(C.BEISPIELE[index]), C.CAP)


def mess_seed(verteilung: int, n_index: int, j: int) -> int:
    """Fester Seed der j-ten Instanz einer Zelle des Messrasters (Verteilung, Paketzahl); stabil über Läufe und Rechner."""
    return 1_000_000 * (verteilung + 1) + 1_000 * (n_index + 1) + j


def zufallsinstanz(lo: float, hi: float, n: int, seed: int, cap: int = C.MESS_CAP) -> Instance:
    """n Pakete, Größen gleichverteilt (ganzzahlig) zwischen lo*cap und hi*cap."""
    rng = random.Random(seed)
    a, b = int(lo * cap), int(hi * cap)
    return Instance(tuple(rng.randint(a, b) for _ in range(n)), cap)
