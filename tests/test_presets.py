"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen; jedes Preset liefert die erwartete Zeile des Rasters."""

import pytest

import sei_algorithm as A
import sei_constants as C
import sei_evaluation as ev
import sei_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for preset in C.PRESETS.values():
        for key, state_key in P.PRESET_KEYS.items():
            lo, hi = P.bounds(state_key)
            assert lo <= preset[key] <= hi, (key, preset)


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**next(iter(C.PRESETS.values()))) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_regler_bounds_decken_alle_auswahlwerte_ab():
    assert P.bounds("beispiel_select") == (0, max(C.BEISPIELE))
    assert P.bounds("ordnung_select") == (0, max(C.ORDNUNGEN)) and P.bounds("regel_select") == (0, max(C.REGELN))
    assert set(C.ORDNUNGEN) == set(C.ORDNUNG_KURZ) == set(range(3)) and set(C.REGELN) == set(C.REGEL_KURZ) == set(range(3))


# Erwartete Containerzahl je Preset (Handrechnung der Beispiele, Phase 0): Beispiel 1 wie geliefert + First Fit = 7, größte zuerst + First Fit = 5,
# Beispiel 2 wie geliefert + First Fit = 6. Die zufällige Reihenfolge hängt an der Startzahl; hier wird nur die Zulässigkeit und die Ordnung zum Optimum geprüft.
ERWARTET = {
    "Beispiel 1, wie geliefert, erster passender": 7,
    "Beispiel 1, größte zuerst, erster passender": 5,
    "Beispiel 2, wie geliefert, erster passender": 6,
}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_jedes_preset_liefert_die_erwartete_containerzahl(name):
    a = ev.analyse(ev.Settings(**C.PRESETS[name]))
    if name in ERWARTET:
        assert a.count == ERWARTET[name]
    else:
        assert a.opt <= a.count and A.container_pruefen(a.inst.sizes, a.bins, a.inst.cap)


def test_verdikt_je_preset_stimmt_mit_der_erwarteten_art():
    arten = {name: ev.verdict_aktuell(ev.analyse(ev.Settings(**C.PRESETS[name])))[0] for name in ERWARTET}
    assert arten["Beispiel 1, wie geliefert, erster passender"] == "warning"       # 7 gegen Optimum 5
    assert arten["Beispiel 1, größte zuerst, erster passender"] == "success"       # 5 = Optimum
    assert arten["Beispiel 2, wie geliefert, erster passender"] == "warning"       # 6 gegen Optimum 5
