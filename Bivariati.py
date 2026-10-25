import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche
from grafici import sincronizza_canvas
from Tabella import TabellaDati


def _fmt(x):
    return f"{x:.4f}".rstrip("0").rstrip(".")


def _quartili(dati: list, stat: FunzioniStatistiche) -> str:
    return " / ".join(_fmt(q) for q in (
        stat.primoQuartile(dati), stat.secondoQuartile(dati), stat.terzoQuartile(dati)))


def interpreta(r: float) -> str:
    a = abs(r)
    forza = "debole" if a < 0.3 else "moderata" if a < 0.7 else "forte"
    segno = "positiva" if r > 0 else "negativa"
    return f"Correlazione {segno} {forza}"


def calcola_bivariati(x: list, y: list, stat: FunzioniStatistiche):
    """Restituisce (testo dei risultati, r oppure None, (a, b) oppure None)."""
    righe = [
        f"{'N coppie':<24}: {len(x)}",
        "",
        f"{'Media X':<24}: {_fmt(stat.mediaCampionaria(x))}",
        f"{'Media Y':<24}: {_fmt(stat.mediaCampionaria(y))}",
        f"{'Deviazione standard X':<24}: {_fmt(stat.deviazioneStandard(x))}",
        f"{'Deviazione standard Y':<24}: {_fmt(stat.deviazioneStandard(y))}",
        "",
        f"{'Quartili X (Q1/Q2/Q3)':<24}: {_quartili(x, stat)}",
        f"{'Quartili Y (Q1/Q2/Q3)':<24}: {_quartili(y, stat)}",
        "",
        f"{'Covarianza':<24}: {_fmt(stat.covarianza(x, y))}",
    ]
    try:
        r = stat.coefficienteCorrelazione(x, y)
        righe += [f"{'Coeff. correlazione r':<24}: {_fmt(r)}", "", interpreta(r)]
    except ValueError as e:
        r = None
        righe += [f"{'Coeff. correlazione r':<24}: non definito", "", str(e)]

    retta = None
    try:
        b = stat.coefficienteAngolare(x, y)
        a = stat.intercetta(x, y)
        retta = (a, b)
        segno = "+" if b >= 0 else "-"
        righe += [
            "",
            f"{'Coeff. angolare (b)':<24}: {_fmt(b)}",
            f"{'Intercetta (a)':<24}: {_fmt(a)}",
            f"Retta: y = {_fmt(a)} {segno} {_fmt(abs(b))} x",
        ]
    except ValueError as e:
        righe += ["", str(e)]
    return "\n".join(righe), r, retta


def disegna_grafici(fig: Figure, x: list, y: list, r, stat: FunzioniStatistiche, retta=None):
    """Diagramma di dispersione (con la retta di regressione, se richiesta)."""
    fig.clear()
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x, y, color="#4C78A8", edgecolor="none", s=30, zorder=3)
    if retta is not None:
        a, b = retta
        x0, x1 = min(x), max(x)
        segno = "+" if b >= 0 else "-"
        ax.plot([x0, x1], [a + b * x0, a + b * x1], color="#E41A1C", linewidth=2.5,
                zorder=2, label=f"y = {_fmt(a)} {segno} {_fmt(abs(b))} x")
        ax.legend(loc="upper left", fontsize=9)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    titolo = "Diagramma di dispersione"
    if r is not None:
        titolo += f" (r = {r:.4f})"
    ax.set_title(titolo)
    ax.grid(linestyle="--", alpha=0.4)


class FinestraBivariati(tk.Toplevel):
    """Finestra per i dati bivariati: diagramma di dispersione e correlazione."""

    def __init__(self, master, dati_x=None):
        super().__init__(master)
        self.title("Dati bivariati")
        self.geometry("1180x760")
        self.minsize(1000, 640)
        self.stat = FunzioniStatistiche()
        self._ultimo = None  # (x, y, r, retta) dell'ultimo calcolo
        self.mostra_retta = tk.BooleanVar(value=True)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Colonna sinistra: input e risultati ---
        sx = ttk.Frame(self)
        sx.grid(row=0, column=0, sticky="ns", padx=(10, 5), pady=10)
        sx.rowconfigure(2, weight=1)

        fd = ttk.LabelFrame(sx, text="Dati")
        fd.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        if dati_x:
            ttk.Label(
                fd, text="La colonna X contiene i dati inseriti nella schermata principale: "
                         "completa la colonna Y.",
                wraplength=380, justify="left", foreground="#1f4e79",
            ).pack(anchor="w", padx=8, pady=(4, 0))
        self.tabella = TabellaDati(fd, altezza=230)
        self.tabella.pack(fill="x", padx=5, pady=(5, 2))
        if dati_x:
            self.tabella.svuota(0)
            for v in dati_x:
                self.tabella.aggiungi_riga(self.tabella._testo(v), "")
            self.after(200, lambda: self.tabella.righe[0][2].focus_set())
        else:
            self.tabella.svuota(8)
        gestione = ttk.Frame(fd)
        gestione.pack(pady=(0, 5))
        ttk.Button(gestione, text="Aggiungi riga",
                   command=lambda: self.tabella.aggiungi_riga(focus=True)).pack(side="left", padx=5)
        ttk.Button(gestione, text="Elimina ultima riga",
                   command=self.tabella.elimina_riga).pack(side="left", padx=5)

        bottoni = ttk.Frame(sx)
        bottoni.grid(row=1, column=0, pady=5)
        ttk.Button(bottoni, text="Calcola", command=self.calcola).pack(side="left", padx=5)
        ttk.Button(bottoni, text="Pulisci", command=self.pulisci).pack(side="left", padx=5)

        fr = ttk.LabelFrame(sx, text="Risultati")
        fr.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        self.area_risultati = scrolledtext.ScrolledText(
            fr, width=46, height=12, wrap=tk.WORD, state="disabled", font=("Courier", 10)
        )
        self.area_risultati.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Colonna destra: diagramma di dispersione ---
        dx = ttk.LabelFrame(self, text="Diagramma di dispersione")
        dx.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        ttk.Checkbutton(
            dx, text="Mostra retta di regressione",
            variable=self.mostra_retta, command=self.ridisegna,
        ).pack(side="top", anchor="w", padx=8, pady=(4, 0))
        self.fig = Figure(figsize=(6, 5), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=dx)
        NavigationToolbar2Tk(self.canvas, dx).update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.after(150, lambda: sincronizza_canvas(self.canvas))

    def _scrivi(self, testo):
        self.area_risultati.config(state="normal")
        self.area_risultati.delete("1.0", tk.END)
        self.area_risultati.insert(tk.END, testo)
        self.area_risultati.config(state="disabled")

    def calcola(self):
        try:
            x, y = self.tabella.leggi()
        except ValueError as e:
            messagebox.showerror("Errore", str(e), parent=self)
            return

        testo, r, retta = calcola_bivariati(x, y, self.stat)
        self._ultimo = (x, y, r, retta)
        self._scrivi(testo)
        self.ridisegna()

    def ridisegna(self):
        """Ridisegna i grafici (usato anche dalla casella della retta)."""
        if self._ultimo is None:
            return
        x, y, r, retta = self._ultimo
        disegna_grafici(self.fig, x, y, r, self.stat, retta if self.mostra_retta.get() else None)
        self.canvas.draw()

    def pulisci(self):
        self.tabella.svuota()
        self._ultimo = None
        self._scrivi("")
        self.fig.clear()
        self.canvas.draw()