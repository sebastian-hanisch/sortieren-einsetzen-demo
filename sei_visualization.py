"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import sei_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_container(sizes, bins, cap):
    """Ein Balken je Container, darin die Pakete als gestapelte Segmente (Beschriftung = Größe), oben der freie Platz in Grau.

    Die rote Linie ist die Kapazität. Beschriftungen als Text (C1, C2 ...), damit Plotly keine lineare Achse anlegt."""
    labels = [f"C{b + 1}" for b in range(len(bins))]
    schichten = max((len(b) for b in bins), default=0)
    fig = go.Figure()
    for k in range(schichten):
        werte = [sizes[b[k]] if k < len(b) else 0 for b in bins]
        texte = [str(sizes[b[k]]) if k < len(b) else "" for b in bins]
        fig.add_trace(go.Bar(x=labels, y=werte, text=texte, textposition="inside", insidetextanchor="middle", marker=dict(color=C.COLOR_FILL, line=dict(color="white", width=1.5)),
                             showlegend=False, hovertemplate="%{x}: Paket %{text}<extra></extra>"))
    frei = [cap - sum(sizes[i] for i in b) for b in bins]
    fig.add_trace(go.Bar(x=labels, y=frei, text=[f"frei {f}" if f > 0 else "" for f in frei], textposition="inside", insidetextanchor="middle",
                         marker=dict(color=C.COLOR_FREE), showlegend=False, hovertemplate="%{x}: %{y} frei<extra></extra>"))
    fig.add_hline(y=cap, line=dict(color=C.COLOR_LINE, width=2, dash="dash"))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title_text="Füllung (Kapazität %d)" % cap, range=[0, cap * 1.05])
    return _base(fig)


def build_messung(mittel):
    """Mittlere Container über der Schranke L2 für die fünf Verfahren (Balken); mittel = {Verfahren: Wert}."""
    namen = [C.VERFAHREN_NAMEN[v] for v in C.VERFAHREN]
    werte = [mittel[v] for v in C.VERFAHREN]
    farben = [C.COLOR_BARS if v in ("NF", "FF", "BF") else C.COLOR_FILL for v in C.VERFAHREN]
    fig = go.Figure(go.Bar(x=namen, y=werte, marker_color=farben, text=[f"{w:.2f}" for w in werte], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x}: %{y:.2f}<extra></extra>"))
    fig.update_yaxes(title_text="Container über der Schranke L2 (Mittel)")
    return _base(fig, 340)
