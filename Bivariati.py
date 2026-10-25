import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche
from grafici import disegna_boxplot, sincronizza_canvas
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


def r_e_retta(x: list, y: list, stat: FunzioniStatistiche):
    """Restituisce (r, (a, b)); ognuno e' None se non definito."""
    try:
        r = stat.coefficienteCorrelazione(x, y)
    except ValueError:
        r = None
    try:
        retta = (stat.intercetta(x, y), stat.coefficienteAngolare(x, y))
    except ValueError:
        retta = None
    return r, retta


def disegna_grafici(fig: Figure, x: list, y: list, r, stat: FunzioniStatistiche, retta=None):
    """In alto il diagramma di dispersione (con la retta di regressione, se richiesta);
    sotto i box plot orizzontali di X e di Y."""
    fig.clear()
    gs = fig.add_gridspec(3, 1, height_ratios=[4, 1.2, 1.2])

    ax = fig.add_subplot(gs[0])
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

    disegna_boxplot(fig.add_subplot(gs[1]), x, stat, "Box plot di X", dettagli=False)
    disegna_boxplot(fig.add_subplot(gs[2]), y, stat, "Box plot di Y", dettagli=False)


class SchermataBivariata(ttk.Frame):
    """Schermata del campione bivariato: tabella (X, Y), risultati e tre pulsanti
    (Calcola, Dati bivariati, Pulisci)."""

    def __init__(self, master):
        super().__init__(master)
        self.stat = FunzioniStatistiche()
        self.fin_grafici = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # --- Tabella dei dati ---
        fd = ttk.LabelFrame(self, text="Campione bivariato (una coppia X, Y per riga)")
        fd.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.tabella = TabellaDati(fd, altezza=230)
        self.tabella.pack(padx=5, pady=(5, 2))
        self.tabella.svuota(8)
        self.nota = ttk.Label(fd, text="", wraplength=600, justify="left", foreground="#1f4e79")
        gestione = ttk.Frame(fd)
        gestione.pack(pady=(0, 5))
        ttk.Button(gestione, text="Aggiungi riga",
                   command=lambda: self.tabella.aggiungi_riga(focus=True)).pack(side="left", padx=5)
        ttk.Button(gestione, text="Elimina ultima riga",
                   command=self.tabella.elimina_riga).pack(side="left", padx=5)

        # --- Pulsanti: solo questi tre ---
        bottoni = ttk.Frame(self)
        bottoni.grid(row=1, column=0, pady=5)
        ttk.Button(bottoni, text="Calcola", command=self.calcola).pack(side="left", padx=5)
        ttk.Button(bottoni, text="Dati bivariati", command=self.apri_grafici).pack(side="left", padx=5)
        ttk.Button(bottoni, text="Pulisci", command=self.pulisci).pack(side="left", padx=5)

        # --- Risultati ---
        fr = ttk.LabelFrame(self, text="Risultati")
        fr.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.area_risultati = scrolledtext.ScrolledText(
            fr, wrap=tk.WORD, height=12, state="disabled", font=("Courier", 10)
        )
        self.area_risultati.pack(fill="both", expand=True, padx=5, pady=5)

    # ---- utilita' ----
    def _scrivi(self, testo):
        self.area_risultati.config(state="normal")
        self.area_risultati.delete("1.0", tk.END)
        self.area_risultati.insert(tk.END, testo)
        self.area_risultati.config(state="disabled")

    def _leggi(self):
        """(x, y) oppure None (dopo aver mostrato l'errore)."""
        try:
            return self.tabella.leggi()
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            return None

    def tabella_vuota(self) -> bool:
        return not any(e.get().strip() for r in self.tabella.righe for e in r[1:])

    def precompila_x(self, dati):
        """Se la tabella e' vuota, mette nella colonna X i dati del campione semplice."""
        if not dati or not self.tabella_vuota():
            return
        self.tabella.svuota(0)
        for v in dati:
            self.tabella.aggiungi_riga(self.tabella._testo(v), "")
        self.nota.config(text="La colonna X contiene i dati inseriti nel campione semplice: "
                              "completa la colonna Y.")
        self.nota.pack(anchor="w", padx=8, pady=(2, 0), before=self.tabella)

    # ---- pulsanti ----
    def calcola(self):
        dati = self._leggi()
        if dati is None:
            return
        testo, _, _ = calcola_bivariati(dati[0], dati[1], self.stat)
        self._scrivi(testo)

    def apri_grafici(self):
        dati = self._leggi()
        if dati is None:
            return
        if self.fin_grafici is not None and self.fin_grafici.winfo_exists():
            self.fin_grafici.destroy()
        self.fin_grafici = FinestraGraficiBivariati(self, dati[0], dati[1])

    def pulisci(self):
        self.tabella.svuota(8)
        self._scrivi("")
        self.nota.pack_forget()
        if self.fin_grafici is not None and self.fin_grafici.winfo_exists():
            self.fin_grafici.destroy()


class FinestraGraficiBivariati(tk.Toplevel):
    """Diagramma di dispersione (con retta di regressione opzionale) e box plot di X e Y."""

    def __init__(self, master, x: list, y: list):
        super().__init__(master)
        self.title("Dati bivariati")
        self.geometry("900x820")
        self.minsize(600, 500)
        self.x, self.y = x, y
        self.stat = FunzioniStatistiche()
        self.r, self.retta = r_e_retta(x, y, self.stat)
        self.mostra_retta = tk.BooleanVar(value=True)

        ttk.Checkbutton(
            self, text="Mostra retta di regressione",
            variable=self.mostra_retta, command=self.ridisegna,
        ).pack(side="top", anchor="w", padx=10, pady=(8, 0))
        self.fig = Figure(figsize=(7, 8), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        NavigationToolbar2Tk(self.canvas, self).update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.ridisegna()
        self.after(150, lambda: sincronizza_canvas(self.canvas))

    def ridisegna(self):
        disegna_grafici(self.fig, self.x, self.y, self.r, self.stat,
                        self.retta if self.mostra_retta.get() else None)
        self.canvas.draw()