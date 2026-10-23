import tkinter as tk
from tkinter import ttk


class TabellaDati(ttk.Frame):
    """Tabella a due colonne (X e Y) con N righe, modificabile cella per cella.

    - Invio / freccia giù: cella sotto (all'ultima riga ne crea una nuova)
    - Freccia su: cella sopra
    - Si può incollare da Excel/Fogli (colonne separate da tab, righe a capo)
    """

    def __init__(self, master, altezza: int = 230, intestazioni=("X", "Y")):
        super().__init__(master)
        self.righe = []  # ogni elemento: (etichetta, entry_1, entry_2)
        self.intestazioni = intestazioni
        self._ultimo_entry = None  # ultima cella in cui l'utente ha cliccato

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

        for col, testo, larg in ((0, "N", 4), (1, intestazioni[0], 16), (2, intestazioni[1], 16)):
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
            e.bind("<FocusIn>", lambda ev, w=e: setattr(self, "_ultimo_entry", w))
        self.righe.append((lbl, ex, ey))
        if focus:
            self._vai(r, 0)

    def elimina_riga(self, indice=None):
        """Elimina la riga indicata (di default l'ultima). Resta sempre almeno una riga."""
        if len(self.righe) <= 1:
            return
        if indice is None or indice >= len(self.righe) - 1:
            for w in self.righe.pop():
                w.destroy()
            return
        valori = [(ex.get(), ey.get()) for _, ex, ey in self.righe]
        del valori[indice]
        self.svuota(0)
        for x, y in valori:
            self.aggiungi_riga(x, y)

    def elimina_selezionata(self):
        """Elimina la riga dell'ultima cella in cui l'utente ha cliccato (o l'ultima)."""
        indice = None
        for i, (_, ex, ey) in enumerate(self.righe):
            if self._ultimo_entry is ex or self._ultimo_entry is ey:
                indice = i
        self.elimina_riga(indice)

    def svuota(self, n: int = 8):
        for riga in self.righe:
            for w in riga:
                w.destroy()
        self.righe = []
        self._ultimo_entry = None
        for _ in range(n):
            self.aggiungi_riga()

    def imposta(self, coppie):
        self.svuota(0)
        for x, y in coppie:
            self.aggiungi_riga(self._testo(x), self._testo(y))

    # ---- lettura ----
    def leggi(self, minimo: int = 2, nome: str = "coppie di valori"):
        """Restituisce (colonna 1, colonna 2). Le righe completamente vuote vengono ignorate."""
        x, y = [], []
        for n, (_, ex, ey) in enumerate(self.righe, start=1):
            sx, sy = ex.get().strip(), ey.get().strip()
            if not sx and not sy:
                continue
            if not sx or not sy:
                raise ValueError(
                    f"Riga {n}: manca il valore di {self.intestazioni[0] if not sx else self.intestazioni[1]}."
                )
            try:
                x.append(float(sx.replace(",", ".")))
                y.append(float(sy.replace(",", ".")))
            except ValueError:
                raise ValueError(f"Riga {n}: i valori devono essere numeri.")
        if len(x) < minimo:
            raise ValueError(f"Servono almeno {minimo} {nome}.")
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