"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sei_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Sechs Pakete mit Größen 2, 5, 4, 7, 1, 3 (Nummern 0 bis 5), Kapazität 10, Summe 22.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Volumenschranke 3, Optimum 3; Next Fit 4 Container, First Fit, Best Fit und FFD je 3."""
    return Instance((2, 5, 4, 7, 1, 3), 10)
