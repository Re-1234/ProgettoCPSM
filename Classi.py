import tkinter as tk
from tkinter import ttk, messagebox

from funzioniStatistiche import FunzioniStatistiche
from Tabella import TabellaDati


def _num(v) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def etichetta_classe(a, b, ultima: bool = False) -> str:
    """[a, b) per le classi normali, [a, b] per l'ultima."""
    return f"[{_num(a)}, {_num(b)}{']' if ultima else ')'}"


def leggi_classi(tabella: TabellaDati) -> list:
    """Legge e controlla gli intervalli. Restituisce la lista ordinata di (a, b)."""
    da, a = tabella.leggi(minimo=1, nome="classe")
    classi = []
    for x, y in zip(da, a):
        if x >= y:
            raise ValueError(
                f"Classe da {_num(x)} a {_num(y)}: l'estremo inferiore deve essere minore del superiore."
            )
        classi.append((x, y))
    classi.sort()
    for (a1, b1), (a2, b2) in zip(classi, classi[1:]):
        if b1 > a2:
            raise ValueError(
                f"Le classi {etichetta_classe(a1, b1)} e {etichetta_classe(a2, b2)} si sovrappongono."
            )
    return classi


def testo_tabella_classi(dati: list, classi: list, stat: FunzioniStatistiche) -> str:
    """Tabella delle frequenze per classi (testo per la textArea)."""
    n = len(dati)
    freq = stat.frequenzeClassi(dati, classi)
    righe = [
        f"{'Classe':<16}{'Ampiezza':>9}{'f ass':>7}{'f rel':>9}{'F ass':>7}{'F rel':>9}{'Densità':>10}"
    ]
    cum = 0
    for k, ((a, b), f) in enumerate(zip(classi, freq)):
        cum += f
        righe.append(
            f"{etichetta_classe(a, b, k == len(classi) - 1):<16}"
            f"{_num(stat.ampiezzaClasse(a, b)):>9}{f:>7}{f / n:>9.4f}{cum:>7}{cum / n:>9.4f}"
            f"{f / (b - a):>10.4f}"
        )
    fuori = n - cum
    if fuori:
        righe += ["", f"Dati fuori dalle classi: {fuori} (su {n})"]
    return "\n".join(righe)


class FinestraClassi(tk.Toplevel):
    """Pagina in cui l'utente aggiunge, modifica o elimina gli intervalli delle classi."""

    def __init__(self, master, classi, applica, suggerimento: str = ""):
        super().__init__(master)
        self.title("Classi")
        self.geometry("430x560")
        self.minsize(400, 480)
        self.applica = applica  # funzione chiamata con la lista di classi (o None)

        ttk.Label(
            self,
            text=(
                "Inserisci gli intervalli delle classi (da / a).\n"
                "Ogni classe [da, a) include l'estremo inferiore ed esclude il superiore; "
                "l'ultima classe include anche il superiore.\n"
                "Per modificare un intervallo basta riscrivere i valori nelle celle."
            ),
            wraplength=390, justify="left",
        ).pack(anchor="w", padx=12, pady=(10, 4))
        if suggerimento:
            ttk.Label(self, text=suggerimento, foreground="#1f4e79").pack(anchor="w", padx=12)

        cornice = ttk.LabelFrame(self, text="Intervalli")
        cornice.pack(fill="x", padx=12, pady=8)
        self.tabella = TabellaDati(cornice, altezza=250, intestazioni=("Da", "A"))
        self.tabella.pack(fill="x", padx=5, pady=(5, 2))
        if classi:
            self.tabella.imposta(classi)
        else:
            self.tabella.svuota(4)

        gestione = ttk.Frame(cornice)
        gestione.pack(pady=(0, 5))
        ttk.Button(gestione, text="Aggiungi classe",
                   command=lambda: self.tabella.aggiungi_riga(focus=True)).pack(side="left", padx=5)
        ttk.Button(gestione, text="Elimina classe selezionata",
                   command=self.tabella.elimina_selezionata).pack(side="left", padx=5)

        azioni = ttk.Frame(self)
        azioni.pack(pady=6)
        ttk.Button(azioni, text="Applica", command=self.conferma).pack(side="left", padx=5)
        ttk.Button(azioni, text="Rimuovi classi", command=self.rimuovi).pack(side="left", padx=5)
        ttk.Button(azioni, text="Annulla", command=self.destroy).pack(side="left", padx=5)

        self.transient(master)
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass

    def conferma(self):
        try:
            classi = leggi_classi(self.tabella)
        except ValueError as e:
            messagebox.showerror("Errore", str(e), parent=self)
            return
        self.applica(classi)
        self.destroy()

    def rimuovi(self):
        self.applica(None)
        self.destroy()