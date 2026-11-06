"""Konstanten: Regler-Grenzen, feste Beispiele, Messraster, Farben und Presets."""

CAP = 100                 # Kapazität eines Containers in den Beispielen (Handbeispiele und Zufallsreihenfolge)
OPT_LIMIT = 12            # so viele Pakete darf das exakte Optimum (Teilmengen-DP) höchstens aufzählen

# --- Beispiele (Pakete in Lieferreihenfolge) -----------------------------------------------------------------------------------------------
# Beispiel 0: Summe 459, Volumenschranke 5 = Optimum; First Fit, Best Fit und Next Fit in Lieferreihenfolge je 7, FFD 5 (Phase 0, von Hand nachgerechnet).
# Beispiel 1: Summe 467, Optimum 5; Next Fit 7, First Fit und Best Fit 6, FFD 5.
BEISPIELE = {
    0: (42, 23, 19, 44, 30, 35, 47, 50, 51, 53, 51, 14),
    1: (55, 22, 14, 47, 54, 50, 25, 16, 54, 29, 53, 48),
}
BEISPIEL_NAMEN = {0: "Beispiel 1 (zwölf Pakete)", 1: "Beispiel 2 (zwölf andere Pakete)"}

ORDNUNGEN = {0: "wie geliefert", 1: "größte zuerst", 2: "zufällig (Startzahl)"}
REGELN = {0: "immer der letzte Container (Next Fit)", 1: "erster passender (First Fit)", 2: "passendster (Best Fit)"}
REGEL_KURZ = {0: "Next Fit", 1: "First Fit", 2: "Best Fit"}
ORDNUNG_KURZ = {0: "Lieferreihenfolge", 1: "größte zuerst", 2: "zufällige Reihenfolge"}   # Zeilennamen der Tabelle
ORDNUNG_MIT = {0: "der Lieferreihenfolge", 1: "der Reihenfolge „größte zuerst“", 2: "einer zufälligen Reihenfolge"}   # nach „Mit“ im Verdikt

SEED_MAX, DEFAULT_SEED = 999999, 7

# --- Messraster (Reihe „gemessen“) ---------------------------------------------------------------------------------------------------------
MESS_CAP = 1000                      # Kapazität in den Messinstanzen (feinere Größen, weniger Gleichstände)
SEEDS_PER_CELL = 200                 # Instanzen je Zelle; der Wert steht neben jeder Zahl
VERTEILUNGEN = (
    ("klein", "kleine Teile (1 bis 25 % der Kapazität)", 0.01, 0.25),
    ("mittel", "mittlere Teile (10 bis 50 %)", 0.10, 0.50),
    ("gross", "große Teile (20 bis 80 %)", 0.20, 0.80),
    ("breit", "breit gestreute Teile (1 bis 90 %)", 0.01, 0.90),
)
MESS_N = (20, 50, 100, 200)
VERFAHREN = ("NF", "FF", "BF", "FFD", "BFD")
VERFAHREN_NAMEN = {
    "NF": "Next Fit (Lieferreihenfolge)",
    "FF": "First Fit (Lieferreihenfolge)",
    "BF": "Best Fit (Lieferreihenfolge)",
    "FFD": "First Fit, größte zuerst (FFD)",
    "BFD": "Best Fit, größte zuerst (BFD)",
}

VERFAHREN_KURZ = {"NF": "Next Fit", "FF": "First Fit", "BF": "Best Fit", "FFD": "FFD", "BFD": "BFD"}   # Tabellenzeilen (schmal genug für das Telefon)

COLOR_FILL = "#2F6B65"
COLOR_FREE = "rgba(150,150,150,0.35)"
COLOR_LINE = "#c0392b"
COLOR_BARS = "#4c78a8"

PRESETS = {
    "Beispiel 1, wie geliefert, erster passender": {"beispiel": 0, "ordnung": 0, "regel": 1, "seed": DEFAULT_SEED},
    "Beispiel 1, größte zuerst, erster passender": {"beispiel": 0, "ordnung": 1, "regel": 1, "seed": DEFAULT_SEED},
    "Beispiel 2, wie geliefert, erster passender": {"beispiel": 1, "ordnung": 0, "regel": 1, "seed": DEFAULT_SEED},
    "Beispiel 1, zufällige Reihenfolge": {"beispiel": 0, "ordnung": 2, "regel": 1, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Beispiel 1, wie geliefert, erster passender": "Zwölf Pakete in der Reihenfolge, in der sie ankommen, jedes in den ersten Container, in den es passt.",
    "Beispiel 1, größte zuerst, erster passender": "Dieselben zwölf Pakete, aber die größten zuerst. Die Regel bleibt gleich; nur die Reihenfolge ändert sich.",
    "Beispiel 2, wie geliefert, erster passender": "Ein zweites Zahlenbeispiel mit zwölf Paketen, wieder in Lieferreihenfolge.",
    "Beispiel 1, zufällige Reihenfolge": "Dieselben Pakete in einer zufälligen Reihenfolge; die Startzahl in der Seitenleiste bestimmt sie.",
}

# Text des Expanders „Annahmen, Grenzen und bekannte Probleme“; derselbe Wortlaut steht in der README (tests/test_claims.py vergleicht beide).
ASSUMPTIONS_MARKDOWN = f"""**Annahmen.** Ganzzahlige Paketgrößen; eine Sorte Container mit fester Kapazität; alle Pakete sind vor dem Packen bekannt; keine Geometrie, nur Größen.

**Grenzen.** Das Messraster deckt vier Größenbereiche und vier Paketzahlen ab, jeweils mit gleichverteilten Größen und {SEEDS_PER_CELL} Instanzen je Zelle. Praxisdaten kommen nicht vor. Das exakte Optimum gibt es nur bis {OPT_LIMIT} Pakete.

**Bekannte Probleme und Unsicherheiten.** Die Mittelwerte des Rasters gelten für diese festen Instanzen; mit anderen Startzahlen ändern sie sich etwas, und eine einzelne Zelle ist kein Gesetz. Next Fit steht als Maßstab für „nur den letzten Container prüfen“ da und ist kein Vorschlag. Die Gütegarantien im Mathematik-Expander stammen aus Suchtreffern und Sekundärquellen, die Originale wurden nicht gelesen. Die App wurde im Browser bedient (Presets, Würfel-Button und Ausklapper auf Desktopbreite; auf Telefonbreite wurde nur das Layout geprüft), nicht auf einem echten Touch-Gerät."""
