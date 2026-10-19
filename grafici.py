import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche

BARRE = "Grafico a barre"
ASTA = "Grafico ad asta"
LINEE = "Grafico a linee"
TORTA = "Grafico a torta"
TIPI_GRAFICO = [BARRE, ASTA, LINEE, TORTA]


def _etichetta(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}"


def disegna(fig: Figure, dati: list, stat: FunzioniStatistiche, tipo: str):
    """Pulisce la figura e disegna i grafici del tipo scelto."""
    fig.clear()

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

    def aggiorna(self):
        disegna(self.fig, self.dati, self.stat, self.scelta.get())
        self.canvas.draw()