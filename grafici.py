import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche

BARRE = "Grafico a barre"
ASTA = "Grafico ad asta"
LINEE = "Grafico a linee"
TORTA = "Grafico a torta"
BOXPLOT = "Box plot"
TIPI_GRAFICO = [BARRE, ASTA, LINEE, TORTA, BOXPLOT]


def sincronizza_canvas(canvas):
    """Allinea la figura alle dimensioni reali del widget: all'apertura della
    finestra la figura puo' risultare piu' grande dell'area e venire tagliata."""
    try:
        w = canvas.get_tk_widget()
        w.event_generate("<Configure>", width=w.winfo_width(), height=w.winfo_height())
    except tk.TclError:
        pass  # finestra gia' chiusa


def _etichetta(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}"


def disegna_boxplot(ax, dati: list, stat: FunzioniStatistiche,
                    titolo: str = "Box plot", dettagli: bool = True):
    """Box plot costruito con i quartili della classe FunzioniStatistiche.
    Se dettagli=True aggiunge il riquadro con i valori numerici."""
    e = _etichetta
    q1 = stat.primoQuartile(dati)
    med = stat.medianaCampionaria(dati)
    q3 = stat.terzoQuartile(dati)
    media = stat.mediaCampionaria(dati)
    lim_inf, lim_sup = stat.limitiOutlier(dati)
    anomali = stat.outlier(dati)
    interni = [v for v in dati if lim_inf <= v <= lim_sup]
    baffo_inf, baffo_sup = min(interni), max(interni)

    ax.bxp(
        [{"med": med, "q1": q1, "q3": q3, "whislo": baffo_inf, "whishi": baffo_sup,
          "fliers": anomali, "mean": media}],
        showmeans=True,
        patch_artist=True,
        boxprops={"facecolor": "#9ecae1", "edgecolor": "black"},
        medianprops={"color": "#d62728", "linewidth": 2},
        meanprops={"marker": "D", "markerfacecolor": "white", "markeredgecolor": "black"},
        flierprops={"marker": "o", "markerfacecolor": "none"},
    )
    if dettagli:
        righe = [
            f"Massimo (baffo)  : {e(baffo_sup)}",
            f"Terzo quartile   : {e(q3)}",
            f"Mediana          : {e(med)}",
            f"Primo quartile   : {e(q1)}",
            f"Minimo (baffo)   : {e(baffo_inf)}",
            f"Media (rombo)    : {e(media)}",
            f"Scarto interquart: {e(q3 - q1)}",
            "Outlier          : " + (", ".join(e(v) for v in sorted(set(anomali))) or "nessuno"),
        ]
        ax.text(0.58, 0.5, "\n".join(righe), transform=ax.transAxes, va="center",
                family="monospace", fontsize=9,
                bbox={"boxstyle": "round", "facecolor": "white", "edgecolor": "gray"})
        ax.set_xlim(0.4, 2.2)
    ax.set_title(titolo)
    ax.set_ylabel("Valori")
    ax.set_xticks([])
    ax.grid(axis="y", linestyle="--", alpha=0.4)


def disegna(fig: Figure, dati: list, stat: FunzioniStatistiche, tipo: str):
    """Pulisce la figura e disegna i grafici del tipo scelto."""
    fig.clear()

    if tipo == BOXPLOT:
        disegna_boxplot(fig.add_subplot(1, 1, 1), dati, stat)
        return

    valori = sorted(set(dati))
    etichette = [_etichetta(v) for v in valori]
    f_ass = [stat.frequenzaAssoluta(v, dati) for v in valori]
    f_rel = [stat.frequenzaRelativa(v, dati) for v in valori]
    cum_ass = stat.frequenzaAssolutaCumulativa(dati)
    cum_rel = stat.frequenzaRelativaCumulativa(dati)
    F_ass = [cum_ass[v] for v in valori]
    F_rel = [cum_rel[v] for v in valori]

    # Il grafico a torta ha senso solo per la distribuzione delle frequenze
    # (non per le cumulative, che non rappresentano parti di un tutto).
    if tipo == TORTA:
        ax = fig.add_subplot(1, 1, 1)
        etichette_torta = [f"{e} (f={f})" for e, f in zip(etichette, f_ass)]
        ax.pie(
            f_ass,
            labels=etichette_torta,
            autopct=lambda p: f"{p:.1f}%",
            startangle=90,
            counterclock=False,
            wedgeprops={"edgecolor": "white"},
        )
        ax.set_title("Distribuzione delle frequenze")
        ax.axis("equal")
        return

    grafici = [
        ("Frequenza assoluta", f_ass, "#4C78A8", "{:d}"),
        ("Frequenza relativa", f_rel, "#F58518", "{:.2f}"),
        ("Frequenza assoluta cumulativa", F_ass, "#54A24B", "{:d}"),
        ("Frequenza relativa cumulativa", F_rel, "#E45756", "{:.2f}"),
    ]
    x = list(range(len(valori)))

    for i, (titolo, y, colore, fmt) in enumerate(grafici, start=1):
        ax = fig.add_subplot(2, 2, i)
        testi = [fmt.format(h) for h in y]

        if tipo == BARRE:
            barre = ax.bar(x, y, color=colore, edgecolor="black")
            ax.bar_label(barre, labels=testi, padding=2, fontsize=8)
        elif tipo == ASTA:
            marker, steli, base = ax.stem(x, y)
            marker.set_color(colore)
            steli.set_color(colore)
            base.set_color("black")
            for xi, yi, t in zip(x, y, testi):
                ax.annotate(t, (xi, yi), textcoords="offset points",
                            xytext=(0, 6), ha="center", fontsize=8)
        elif tipo == LINEE:
            ax.plot(x, y, color=colore, marker="o", linewidth=2)
            for xi, yi, t in zip(x, y, testi):
                ax.annotate(t, (xi, yi), textcoords="offset points",
                            xytext=(0, 7), ha="center", fontsize=8)

        ax.set_title(titolo)
        ax.set_xlabel("Valore")
        ax.set_ylabel("Frequenza")
        ax.set_xticks(x)
        ax.set_xticklabels(etichette)
        ax.set_xlim(-0.6, len(x) - 0.4)
        ax.set_ylim(0, max(y) * 1.2)
        ax.grid(axis="y", linestyle="--", alpha=0.4)


def crea_figura(dati: list, stat: FunzioniStatistiche, tipo: str = BARRE) -> Figure:
    fig = Figure(figsize=(10, 7), tight_layout=True)
    disegna(fig, dati, stat, tipo)
    return fig


class FinestraGrafici(tk.Toplevel):
    """Seconda finestra: l'utente sceglie il tipo di grafico (matplotlib)."""

    def __init__(self, master, dati: list):
        super().__init__(master)
        self.title("Grafici")
        self.geometry("900x740")
        self.dati = dati
        self.stat = FunzioniStatistiche()

        # --- Scelta del tipo di grafico ---
        barra = ttk.Frame(self)
        barra.pack(fill="x", padx=10, pady=8)
        ttk.Label(barra, text="Tipo di grafico:").pack(side="left")
        self.scelta = tk.StringVar(value=BARRE)
        combo = ttk.Combobox(
            barra, textvariable=self.scelta, values=TIPI_GRAFICO,
            state="readonly", width=22,
        )
        combo.pack(side="left", padx=8)
        combo.bind("<<ComboboxSelected>>", lambda e: self.aggiorna())

        # --- Figura matplotlib ---
        self.fig = Figure(figsize=(10, 7), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.aggiorna()
        self.after(150, lambda: sincronizza_canvas(self.canvas))

    def aggiorna(self):
        disegna(self.fig, self.dati, self.stat, self.scelta.get())
        self.canvas.draw()