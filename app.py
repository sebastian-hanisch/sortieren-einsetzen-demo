"""Packen: erst sortieren, dann einsetzen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 1 der Reihe „Packen: Reihenfolge und Platzierungsregel“. Zwölf Pakete, drei Reihenfolgen, drei Regeln: Was verändert die Containerzahl mehr?
Das Messraster (vorberechnet in sei_precomputed.json) zeigt dieselbe Frage an je 200 Zufallsinstanzen.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sei_constants as C
from sei_evaluation import Settings, analyse, verdict_aktuell, verdict_messung, verdict_raster, zeile
from sei_layout import dunkles_design, kopf_css
from sei_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from sei_visualization import build_container, build_messung

st.set_page_config(page_title="Packen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sei_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Packen: erst sortieren, dann einsetzen")
st.markdown(
    """
Pakete sollen in möglichst wenige **Container** gleicher Größe. Zwei Dinge legen die Packung fest: die **Reihenfolge**, in der man die Pakete nimmt, und die **Regel**, in welchen Container das nächste kommt. Die Demo zeigt an zwölf Paketen und an einem Messraster aus je 200 Zufallsinstanzen, was von beidem die Containerzahl stärker verändert.

Weiter unten: der Abschnitt **🔬 Experiment**, **🚧 Wo die Annahmen enden**, der Expander **⚠️ Annahmen, Grenzen und bekannte Probleme** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert Packen nach Reihenfolge und Regel", expanded=True):
    st.markdown(
        """
1. **Reihenfolge wählen:** die Pakete in der Reihenfolge, wie sie ankommen, die größten zuerst, oder zufällig.
2. **Regel anwenden, Paket für Paket:** *Next Fit* prüft nur den zuletzt geöffneten Container, *First Fit* den ersten Container mit genug Platz, *Best Fit* den Container, in dem danach am wenigsten Platz frei bleibt. Passt das Paket nirgends hin, wird ein neuer Container geöffnet.
3. **Wo die Wirkung sitzt:** Die Regel entscheidet nur über das, was schon im Container liegt. Was als Nächstes kommt, legt die Reihenfolge fest. Das Kästchen *Kernfrage* unten zählt, welche der beiden Stellschrauben hier mehr bewegt.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Pakete**")
    beispiel = st.selectbox("Beispiel", list(C.BEISPIELE), format_func=C.BEISPIEL_NAMEN.get, key="beispiel_select",
                            help="Zwölf feste Paketgrößen, Kapazität eines Containers: 100.")
    st.markdown("**Packen**")
    ordnung = st.selectbox("Reihenfolge der Pakete", list(C.ORDNUNGEN), format_func=C.ORDNUNGEN.get, key="ordnung_select",
                           help="Die Reihenfolge, in der die Pakete in die Container gesetzt werden.")
    regel = st.selectbox("Regel: in welchen Container?", list(C.REGELN), format_func=C.REGELN.get, key="regel_select",
                         help="Wohin das nächste Paket kommt.")
    seed = st.number_input("Startzahl der zufälligen Reihenfolge", *bounds("seed_input"), key="seed_input", step=1,
                           help="Wirkt nur, wenn die Reihenfolge „zufällig“ gewählt ist.")
    st.button("🎲 Neue zufällige Reihenfolge würfeln", width="stretch", on_click=randomize_seed)

sync_query_params({"beispiel_select": int(beispiel), "ordnung_select": int(ordnung), "regel_select": int(regel), "seed_input": int(seed)})

settings = Settings(int(beispiel), int(ordnung), int(regel), int(seed))
a = _analysis(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3 = st.columns(3)
# Delta immer als „mein Wert minus Referenz“; die Farbe regelt delta_color="inverse" (Vorzeichen-Falle, DEMO-PLAYBOOK §2).
if a.opt is not None:
    m1.metric("Container (gewählte Kombination)", a.count, delta=a.count - a.opt, delta_color="inverse", help="Delta: gewählte Containerzahl minus Optimum.")
    m2.metric("Optimum (exakt berechnet)", a.opt, delta="Referenz", delta_color="off")
else:
    m1.metric("Container (gewählte Kombination)", a.count)
    m2.metric("Optimum", "nicht berechnet", delta="mehr als %d Pakete" % C.OPT_LIMIT, delta_color="off")
m3.metric("Untere Schranke (Volumen)", a.schranke_l1, delta="Summe der Größen durch Kapazität, aufgerundet", delta_color="off")
st.caption("Reihenfolge, in der die Pakete gesetzt werden: " + ", ".join(str(a.inst.sizes[i]) for i in a.order) + f"  (Summe {sum(a.inst.sizes)}, Kapazität {a.inst.cap}).")
st.plotly_chart(build_container(a.inst.sizes, a.bins, a.inst.cap), width="stretch", key="main_chart")
st.caption("Grün: Pakete (Beschriftung = Größe), grau: freier Platz, rot gestrichelt: Kapazität eines Containers.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verändert die Containerzahl mehr, die Reihenfolge oder die Regel?")
kind, text = verdict_aktuell(a)
getattr(st, kind)(text)

zeilen = ["| Reihenfolge \\ Regel | " + " | ".join(C.REGEL_KURZ[r] for r in sorted(C.REGELN)) + " |", "|---|" + "---|" * len(C.REGELN)]
for o in sorted(C.ORDNUNGEN):
    name = C.ORDNUNG_KURZ[o] + (f" (Startzahl {settings.seed})" if o == 2 else "")
    zellen = []
    for r in sorted(C.REGELN):
        wert = str(a.raster[o][r])
        zellen.append(f"**{wert}**" if (o, r) == (settings.ordnung, settings.regel) else wert)
    zeilen.append(f"| {name} | " + " | ".join(zellen) + " |")
st.markdown("Containerzahl für alle neun Kombinationen (die gewählte ist fett):\n\n" + "\n".join(zeilen))
kind, text = verdict_raster(a)
getattr(st, kind)(text)

st.markdown("---")

# --- Experiment ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment: Hilft Sortieren auch bei vielen Paketen?")
st.caption(
    f"Gemessen an je {C.SEEDS_PER_CELL} festen Zufallsinstanzen pro Zelle, Kapazität {C.MESS_CAP}, Paketgrößen gleichverteilt im gewählten Bereich. "
    "Maßstab ist die untere Schranke L2 (nicht das Optimum, das für so viele Pakete nicht berechnet wird). Die Zahlen sind vorberechnet (`generate_precomputed.py`)."
)
e1, e2 = st.columns(2)
verteilung = e1.selectbox("Größen der Pakete", list(range(len(C.VERTEILUNGEN))), index=2, format_func=lambda i: C.VERTEILUNGEN[i][1], key="exp_verteilung")
n_index = e2.selectbox("Zahl der Pakete n", list(range(len(C.MESS_N))), index=3, format_func=lambda i: str(C.MESS_N[i]), key="exp_n")
z = zeile(int(verteilung), int(n_index))
st.plotly_chart(build_messung(z["mittel"]), width="stretch", key="exp_chart")
tabelle = ["| Verfahren | Container über L2 | Anteil = L1 | Anteil = L2 |", "|---|---|---|---|"]
for v in C.VERFAHREN:
    tabelle.append(f"| {C.VERFAHREN_KURZ[v]} | {z['mittel'][v]:.2f} | {z['anteil_l1'][v]:.1f} % | {z['anteil_l2'][v]:.1f} % |")
st.markdown("\n".join(tabelle))
st.caption("Next Fit, First Fit und Best Fit in Lieferreihenfolge; FFD und BFD: größte zuerst mit First Fit bzw. Best Fit. Container über L2: Mittel über die Instanzen der Zelle. Anteil = L1 und Anteil = L2: Anteil der Instanzen, in denen das Verfahren die jeweilige Schranke genau trifft.")
kind, text = verdict_messung(z)
getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Pakete sind zufällig und gleichverteilt** | Es gibt Pakete, bei denen auch FFD das Optimum verfehlt: Mit Paketgrößen 502, 254, 252 und 246 (Kapazität 1000; 6, 6, 6 und 12 Stück) braucht FFD 11 Container, das Optimum ist 9. | spätere Stücke dieser Reihe |
| **Das Optimum ist bekannt** | Exakt rechnet die Demo es nur bis zu 12 Paketen. Darüber gilt nur die untere Schranke; verfehlt eine Packung sie, bleibt offen, ob sie optimal ist. Das Messraster zählt deshalb Container über der Schranke L2, nicht über dem Optimum. | - |
| **Alle Pakete sind vor dem Packen bekannt** | Wer jedes Paket sofort einsortieren muss, kann nicht nach der Größe sortieren. Das ist Online-Packen. | [Online-Algorithmen](https://sebastianhanisch.net/konzepte-online-algorithmen.html) |
| **Jedes Paket hat eine einzige Größe** | Hat ein Container zwei Grenzen zugleich (etwa Volumen und Gewicht), ist offen, wonach man sortiert. Die Demo zeigt nur eine Größe. | spätere Stücke dieser Reihe |
"""
)

with st.expander("⚠️ Annahmen, Grenzen und bekannte Probleme"):
    st.markdown(C.ASSUMPTIONS_MARKDOWN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** *Gegeben:* Pakete mit ganzzahligen Größen und Container einer festen Kapazität. *Gesucht:* eine Zuordnung der Pakete zu möglichst wenigen Containern, sodass die Größen in jedem Container höchstens die Kapazität ergeben.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Pakete |
| $s_i$ | Größe von Paket $i$, $1 \le s_i \le C$ |
| $C$ | Kapazität eines Containers |
| $\mathrm{OPT}$ | kleinste mögliche Zahl von Containern |
| $L_1$, $L_2$ | untere Schranken für $\mathrm{OPT}$ |

**Reihenfolge und Regel.** Eine Reihenfolge $\pi$ der Pakete und eine Regel bestimmen die Packung: Paket $\pi(1)$ kommt in den ersten Container; jedes weitere Paket kommt nach *Next Fit* in den zuletzt geöffneten Container, nach *First Fit* in den Container mit der kleinsten Nummer und nach *Best Fit* in den Container mit dem kleinsten freien Platz danach, jeweils nur, wenn es dort noch passt; sonst öffnet es einen neuen. *FFD* (First Fit Decreasing) ist First Fit in der Reihenfolge fallender Größe, *BFD* ebenso mit Best Fit.

**Volumenschranke.** $L_1 = \left\lceil \tfrac{1}{C} \sum_i s_i \right\rceil \le \mathrm{OPT}$.

**Schranke $L_2$** (Martello und Toth). Für $\alpha \ge 0$ sei $J_1 = \{ s_i > C - \alpha \}$, $J_2 = \{ C - \alpha \ge s_i > C/2 \}$, $J_3 = \{ C/2 \ge s_i \ge \alpha \}$. Pakete aus $J_1 \cup J_2$ brauchen je einen eigenen Container, und die Pakete aus $J_3$ füllen zuerst den freien Platz der $J_2$-Container:
$$L(\alpha) = |J_1| + |J_2| + \max\!\left(0, \left\lceil \frac{\sum_{J_3} s_i - (|J_2|\,C - \sum_{J_2} s_i)}{C} \right\rceil\right), \qquad L_2 = \max_\alpha L(\alpha).$$
Es genügt $\alpha \in \{0\} \cup \{ s_i : s_i \le C/2 \}$. Es gilt $L_1 \le L_2 \le \mathrm{OPT}$.

**Exaktes Optimum** (bis 12 Pakete). Für eine Menge $M$ von Paketen sei $f(M) = (b, \ell)$ das lexikographisch kleinste Paar aus Containerzahl $b$ und Füllung $\ell$ des letzten Containers. Ein Paket $i \notin M$ kommt entweder in den letzten Container (wenn $\ell + s_i \le C$) oder in einen neuen; $\mathrm{OPT} = b$ von $f(\{1,\dots,n\})$.

**Gütegarantie (Literatur, aus Suchtreffern, Originale nicht gelesen).** Johnson, Demers, Ullman, Garey und Graham (SIAM J. Comput. 3, 1974): $\mathrm{FFD} \le \tfrac{11}{9}\,\mathrm{OPT} + 4$. Dósa (2007): $\mathrm{FFD} \le \tfrac{11}{9}\,\mathrm{OPT} + \tfrac{6}{9}$, und die Konstante $\tfrac{6}{9}$ ist bestmöglich. Die Demo prüft die zweite Schranke an kleinen Instanzen gegen das exakte Optimum.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
