import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche


def _fmt(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def leggi_numeri(testo: str, nome: str) -> list:
    """Legge numeri separati da spazi, a capo, virgole o punto e virgola."""
    raw = testo.replace(",", " ").replace(";", " ").split()
    if not raw:
        raise ValueError(f"Inserisci i valori di {nome}.")
    try:
        return [float(v) for v in raw]
    except ValueError:
        raise ValueError(f"I valori di {nome} devono essere numeri.")


def interpreta(r: float) -> str:
    a = abs(r)
    forza = "debole" if a < 0.3 else "moderata" if a < 0.7 else "forte"
    segno = "positiva" if r > 0 else "negativa"
    return f"Correlazione {segno} {forza}"


def calcola_bivariati(x: list, y: list, stat: FunzioniStatistiche):
    """Restituisce (testo dei risultati, r oppure None se non definito)."""
    righe = [
        f"{'N coppie':<24}: {len(x)}",
        "",
        f"{'Media X':<24}: {_fmt(stat.mediaCampionaria(x))}",
        f"{'Media Y':<24}: {_fmt(stat.mediaCampionaria(y))}",
        f"{'Deviazione standard X':<24}: {_fmt(stat.deviazioneStandard(x))}",
        f"{'Deviazione standard Y':<24}: {_fmt(stat.deviazioneStandard(y))}",
        "",
        f"{'Covarianza':<24}: {_fmt(stat.covarianza(x, y))}",
    ]
    try:
        r = stat.coefficienteCorrelazione(x, y)
    except ValueError as e:
        righe.append(f"{'Coeff. correlazione r':<24}: non definito")
        righe += ["", str(e)]
        return "\n".join(righe), None
    righe.append(f"{'Coeff. correlazione r':<24}: {_fmt(r)}")
    righe += ["", interpreta(r)]
    return "\n".join(righe), r


def disegna_dispersione(fig: Figure, x: list, y: list, r=None):
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x, y, color="#4C78A8", edgecolor="black", s=50, zorder=3)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    titolo = "Diagramma di dispersione"
    if r is not None:
        titolo += f" (r = {r:.4f})"
    ax.set_title(titolo)
    ax.grid(linestyle="--", alpha=0.4)


class FinestraBivariati(tk.Toplevel):
    """Finestra per i dati bivariati: diagramma di dispersione e correlazione."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Dati bivariati")
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.stat = FunzioniStatistiche()

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Colonna sinistra: input e risultati ---
        sx = ttk.Frame(self)
        sx.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        sx.rowconfigure(3, weight=1)

        fx = ttk.LabelFrame(sx, text="Valori di X")
        fx.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.text_x = scrolledtext.ScrolledText(fx, width=36, height=4, wrap=tk.WORD)
        self.text_x.pack(padx=5, pady=5)
        self.text_x.insert("1.0", "1 2 3 4 5 6 7 8")

        fy = ttk.LabelFrame(sx, text="Valori di Y")
        fy.grid(row=1, column=0, sticky="ew", pady=5)
        self.text_y = scrolledtext.ScrolledText(fy, width=36, height=4, wrap=tk.WORD)
        self.text_y.pack(padx=5, pady=5)
        self.text_y.insert("1.0", "2 4 5 4 5 7 8 9")

        bottoni = ttk.Frame(sx)
        bottoni.grid(row=2, column=0, pady=5)
        ttk.Button(bottoni, text="Calcola", command=self.calcola).pack(side="left", padx=5)
        ttk.Button(bottoni, text="Pulisci", command=self.pulisci).pack(side="left", padx=5)

        fr = ttk.LabelFrame(sx, text="Risultati")
        fr.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        self.area_risultati = scrolledtext.ScrolledText(
            fr, width=36, height=12, wrap=tk.WORD, state="disabled", font=("Courier", 10)
        )
        self.area_risultati.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Colonna destra: diagramma di dispersione ---
        dx = ttk.LabelFrame(self, text="Diagramma di dispersione")
        dx.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.fig = Figure(figsize=(6, 5), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=dx)
        NavigationToolbar2Tk(self.canvas, dx).update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.calcola()

    def _scrivi(self, testo):
        self.area_risultati.config(state="normal")
        self.area_risultati.delete("1.0", tk.END)
        self.area_risultati.insert(tk.END, testo)
        self.area_risultati.config(state="disabled")

    def calcola(self):
        try:
            x = leggi_numeri(self.text_x.get("1.0", "end-1c"), "X")
            y = leggi_numeri(self.text_y.get("1.0", "end-1c"), "Y")
            if len(x) != len(y):
                raise ValueError(
                    f"X e Y devono avere lo stesso numero di valori (X: {len(x)}, Y: {len(y)})."
                )
            if len(x) < 2:
                raise ValueError("Servono almeno 2 coppie di valori.")
        except ValueError as e:
            messagebox.showerror("Errore", str(e), parent=self)
            return

        testo, r = calcola_bivariati(x, y, self.stat)
        self._scrivi(testo)
        disegna_dispersione(self.fig, x, y, r)
        self.canvas.draw()

    def pulisci(self):
        self.text_x.delete("1.0", tk.END)
        self.text_y.delete("1.0", tk.END)
        self._scrivi("")
        self.fig.clear()
        self.canvas.draw()