import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funzioniStatistiche import FunzioniStatistiche
from grafici import disegna_boxplot, sincronizza_canvas


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
    """In alto il diagramma di dispersione (con la retta, se richiesta),
    sotto i box plot di X e di Y."""
    fig.clear()
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 2])

    ax = fig.add_subplot(gs[0, :])
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

    disegna_boxplot(fig.add_subplot(gs[1, 0]), x, stat, "Box plot di X", dettagli=False)
    disegna_boxplot(fig.add_subplot(gs[1, 1]), y, stat, "Box plot di Y", dettagli=False)


class TabellaDati(ttk.Frame):
    """Tabella a due colonne (X e Y) con N righe, modificabile cella per cella.

    - Invio / freccia giù: cella sotto (all'ultima riga ne crea una nuova)
    - Freccia su: cella sopra
    - Si può incollare da Excel/Fogli (colonne separate da tab, righe a capo)
    """

    def __init__(self, master, altezza: int = 230):
        super().__init__(master)
        self.righe = []  # ogni elemento: (etichetta, entry_x, entry_y)

        self.canvas = tk.Canvas(self, height=altezza, highlightthickness=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barra.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.interno = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.interno, anchor="nw")
        self.interno.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        for col, testo, larg in ((0, "N", 4), (1, "X", 16), (2, "Y", 16)):
            ttk.Label(self.interno, text=testo, width=larg, anchor="center",
                      font=("TkDefaultFont", 9, "bold")).grid(row=0, column=col, padx=2, pady=(0, 3))

        # rotellina del mouse (solo quando il puntatore è sopra la tabella)
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(evento, self._rotellina, add="+")

    # ---- gestione righe ----
    @staticmethod
    def _testo(v) -> str:
        return str(int(v)) if float(v).is_integer() else str(v)

    def aggiungi_riga(self, x="", y="", focus: bool = False):
        r = len(self.righe)
        lbl = ttk.Label(self.interno, text=str(r + 1), width=4, anchor="center")
        ex = ttk.Entry(self.interno, width=16, justify="center")
        ey = ttk.Entry(self.interno, width=16, justify="center")
        lbl.grid(row=r + 1, column=0, padx=2, pady=1)
        ex.grid(row=r + 1, column=1, padx=2, pady=1)
        ey.grid(row=r + 1, column=2, padx=2, pady=1)
        ex.insert(0, x)
        ey.insert(0, y)
        for col, e in enumerate((ex, ey)):
            e.bind("<Return>", lambda ev, i=r, c=col: self._vai(i + 1, c))
            e.bind("<Down>", lambda ev, i=r, c=col: self._vai(i + 1, c))
            e.bind("<Up>", lambda ev, i=r, c=col: self._vai(i - 1, c))
            e.bind("<<Paste>>", lambda ev, i=r, c=col: self._incolla(i, c))
        self.righe.append((lbl, ex, ey))
        if focus:
            self._vai(r, 0)

    def elimina_riga(self):
        if len(self.righe) > 1:
            for w in self.righe.pop():
                w.destroy()

    def svuota(self, n: int = 5):
        for riga in self.righe:
            for w in riga:
                w.destroy()
        self.righe = []
        for _ in range(n):
            self.aggiungi_riga()

    def imposta(self, coppie):
        self.svuota(0)
        for x, y in coppie:
            self.aggiungi_riga(self._testo(x), self._testo(y))

    # ---- lettura ----
    def leggi(self):
        """Restituisce (x, y). Le righe completamente vuote vengono ignorate."""
        x, y = [], []
        for n, (_, ex, ey) in enumerate(self.righe, start=1):
            sx, sy = ex.get().strip(), ey.get().strip()
            if not sx and not sy:
                continue
            if not sx or not sy:
                raise ValueError(f"Riga {n}: manca il valore di {'X' if not sx else 'Y'}.")
            try:
                x.append(float(sx.replace(",", ".")))
                y.append(float(sy.replace(",", ".")))
            except ValueError:
                raise ValueError(f"Riga {n}: i valori devono essere numeri.")
        if len(x) < 2:
            raise ValueError("Servono almeno 2 coppie di valori.")
        return x, y

    # ---- navigazione, incolla, scroll ----
    def _vai(self, i: int, c: int):
        if i < 0:
            return "break"
        if i >= len(self.righe):
            self.aggiungi_riga()
        entry = self.righe[i][1 + c]
        entry.focus_set()
        entry.selection_range(0, tk.END)
        self.update_idletasks()
        totale = max(self.interno.winfo_height(), 1)
        alto = self.canvas.canvasy(0)
        visibile = self.canvas.winfo_height()
        if entry.winfo_y() < alto:
            self.canvas.yview_moveto(entry.winfo_y() / totale)
        elif entry.winfo_y() + entry.winfo_height() > alto + visibile:
            self.canvas.yview_moveto((entry.winfo_y() + entry.winfo_height() - visibile) / totale)
        return "break"

    def _incolla(self, i: int, c: int):
        try:
            testo = self.clipboard_get()
        except tk.TclError:
            return None
        if "\n" not in testo.strip() and "\t" not in testo:
            return None  # testo semplice: incolla normale nella cella
        for k, riga in enumerate(l for l in testo.splitlines() if l.strip()):
            if "\t" in riga:
                valori = [v.strip() for v in riga.split("\t")]
            else:
                valori = riga.replace(";", " ").split()
            while i + k >= len(self.righe):
                self.aggiungi_riga()
            for j, v in enumerate(valori):
                if c + j > 1:
                    break
                e = self.righe[i + k][1 + c + j]
                e.delete(0, tk.END)
                e.insert(0, v)
        return "break"

    def _rotellina(self, ev):
        w = self.winfo_containing(ev.x_root, ev.y_root)
        if w is None or not str(w).startswith(str(self)):
            return
        su = ev.num == 4 or getattr(ev, "delta", 0) > 0
        self.canvas.yview_scroll(-1 if su else 1, "units")


class FinestraBivariati(tk.Toplevel):
    """Finestra per i dati bivariati: diagramma di dispersione e correlazione."""

    def __init__(self, master):
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
        self.tabella = TabellaDati(fd, altezza=230)
        self.tabella.pack(fill="x", padx=5, pady=(5, 2))
        self.tabella.imposta([(1, 2), (2, 4), (3, 5), (4, 4), (5, 5), (6, 7), (7, 8), (8, 9)])
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
        dx = ttk.LabelFrame(self, text="Grafici")
        dx.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        ttk.Checkbutton(
            dx, text="Mostra retta di regressione",
            variable=self.mostra_retta, command=self.ridisegna,
        ).pack(side="top", anchor="w", padx=8, pady=(4, 0))
        self.fig = Figure(figsize=(6, 6.5), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=dx)
        NavigationToolbar2Tk(self.canvas, dx).update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.calcola()
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