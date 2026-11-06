"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: lädt app.py mit den Standardeinstellungen, klickt jeden Button, stellt jede Auswahl
auf jeden ihrer Werte und das Zahlenfeld an seine Grenzen und prüft, dass kein Python-Fehler auftritt (insbesondere `StreamlitDuplicateElementId`
bei mehreren Diagrammen ohne key= und `StreamlitAPIException` bei Auswahlen mit ungültigem Wert)."""

import os

from streamlit.testing.v1 import AppTest

import sei_constants as C

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_selectbox_value_does_not_raise():
    keys = [s.key for s in _fresh_app().selectbox]
    assert {"beispiel_select", "ordnung_select", "regel_select", "exp_verteilung", "exp_n"} <= set(keys)
    anzahl = {"beispiel_select": len(C.BEISPIELE), "ordnung_select": len(C.ORDNUNGEN), "regel_select": len(C.REGELN),
              "exp_verteilung": len(C.VERTEILUNGEN), "exp_n": len(C.MESS_N)}
    for key in keys:
        for wert in range(anzahl[key]):
            at = _fresh_app()
            at.selectbox(key=key).set_value(wert).run(timeout=TIMEOUT)
            assert not at.exception, (key, wert, [str(e) for e in at.exception])


def test_seed_at_its_min_and_max_does_not_raise():
    for wert in (0, C.SEED_MAX):
        at = _fresh_app()
        at.number_input(key="seed_input").set_value(wert).run(timeout=TIMEOUT)
        assert not at.exception, (wert, [str(e) for e in at.exception])


def test_wuerfeln_waehlt_die_zufaellige_reihenfolge():
    at = _fresh_app()
    at.button[[b.label for b in at.button].index("🎲 Neue zufällige Reihenfolge würfeln")].click().run(timeout=TIMEOUT)
    assert at.selectbox(key="ordnung_select").value == 2


def test_standardansicht_zeigt_das_erwartete_verdikt():
    at = _fresh_app()
    warnungen = [w.value for w in at.warning]
    assert any("**7** Container" in w and "das Optimum ist **5**" in w for w in warnungen)      # Beispiel 1, wie geliefert, First Fit
    erfolge = [s.value for s in at.success]
    assert any("Hier zählt die Reihenfolge mehr" in s for s in erfolge)


def test_expander_stehen_unter_ihren_namen():
    labels = [e.label for e in _fresh_app().expander]
    assert "📐 Mathematische Formulierung" in labels and "⚠️ Annahmen, Grenzen und bekannte Probleme" in labels
