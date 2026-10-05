import tkinter as tk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche


def _etichetta(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.2f}"


def crea_figura(dati: list, stat: FunzioniStatistiche) -> Figure:
    """Crea una figura con 4 grafici a barre delle frequenze."""
    valori = sorted(set(dati))
    etichette = [_etichetta(v) for v in valori]

    f_ass = [stat.frequenzaAssoluta(v, dati) for v in valori]
    f_rel = [stat.frequenzaRelativa(v, dati) for v in valori]
    cum_ass = stat.frequenzaAssolutaCumulativa(dati)
    cum_rel = stat.frequenzaRelativaCumulativa(dati)
    F_ass = [cum_ass[v] for v in valori]
    F_rel = [cum_rel[v] for v in valori]

    grafici = [
        ("Frequenza assoluta", f_ass, "#4C78A8", "{:d}"),
        ("Frequenza relativa", f_rel, "#F58518", "{:.2f}"),
        ("Frequenza assoluta cumulativa", F_ass, "#54A24B", "{:d}"),
        ("Frequenza relativa cumulativa", F_rel, "#E45756", "{:.2f}"),
    ]

    fig = Figure(figsize=(10, 7), tight_layout=True)
    for i, (titolo, y, colore, fmt) in enumerate(grafici, start=1):
        ax = fig.add_subplot(2, 2, i)
        barre = ax.bar(etichette, y, color=colore, edgecolor="black")
        ax.set_title(titolo)
        ax.set_xlabel("Valore")
        ax.set_ylabel("Frequenza")
        ax.set_ylim(0, max(y) * 1.15)
        ax.bar_label(barre, labels=[fmt.format(h) for h in y], padding=2, fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
    return fig


class FinestraGrafici(tk.Toplevel):
    """Seconda finestra con i grafici a barre (matplotlib)."""

    def __init__(self, master, dati: list):
        super().__init__(master)
        self.title("Grafici a barre")
        self.geometry("900x700")

        fig = crea_figura(dati, FunzioniStatistiche())
        canvas = FigureCanvasTkAgg(fig, master=self)
        toolbar = NavigationToolbar2Tk(canvas, self)  # zoom, salva immagine, ecc.
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()