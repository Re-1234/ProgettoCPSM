import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from funzioniStatistiche import FunzioniStatistiche
from grafici import FinestraGrafici


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Statistica descrittiva")
        self.geometry("760x680")
        self.minsize(600, 500)
        self.stat = FunzioniStatistiche()
        self.ultimi_dati = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        # --- L'unico campo di testo a riga singola (JTextField) ---
        frame_in = ttk.LabelFrame(self, text="Dati (numeri separati da spazio, virgola o ;)")
        frame_in.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        frame_in.columnconfigure(0, weight=1)
        self.entry = ttk.Entry(frame_in)
        self.entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.entry.insert(0, "2, 4, 4, 5, 7, 9, 4")
        self.entry.bind("<Return>", lambda e: self.calcola())

        # --- Pulsanti ---
        buttons = ttk.Frame(self)
        buttons.grid(row=1, column=0, pady=5)
        ttk.Button(buttons, text="Calcola", command=self.calcola).pack(side="left", padx=5)
        ttk.Button(buttons, text="Mostra grafici", command=self.apri_grafici).pack(side="left", padx=5)
        ttk.Button(buttons, text="Pulisci", command=self.pulisci).pack(side="left", padx=5)

        # --- TextArea 1: tabella frequenze ---
        f1 = ttk.LabelFrame(self, text="Tabella delle frequenze")
        f1.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.area_freq = scrolledtext.ScrolledText(
            f1, wrap=tk.NONE, height=8, state="disabled", font=("Courier", 10)
        )
        self.area_freq.pack(fill="both", expand=True, padx=5, pady=5)

        # --- TextArea 2: indici ---
        f2 = ttk.LabelFrame(self, text="Indici statistici")
        f2.grid(row=3, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.area_indici = scrolledtext.ScrolledText(
            f2, wrap=tk.WORD, height=10, state="disabled", font=("Courier", 10)
        )
        self.area_indici.pack(fill="both", expand=True, padx=5, pady=5)

    @staticmethod
    def scrivi(area, testo):
        area.config(state="normal")
        area.delete("1.0", tk.END)
        area.insert(tk.END, testo)
        area.config(state="disabled")

    def leggi_dati(self):
        raw = self.entry.get().replace(",", " ").replace(";", " ").split()
        if not raw:
            raise ValueError("Inserisci almeno un numero.")
        try:
            return [float(x.replace(",", ".")) for x in raw]
        except ValueError:
            raise ValueError("Sono ammessi solo numeri.")

    @staticmethod
    def fmt(x):
        return f"{x:.4f}".rstrip("0").rstrip(".")

    def calcola(self):
        try:
            dati = self.leggi_dati()
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            return

        self.ultimi_dati = dati
        s, fmt = self.stat, self.fmt
        cum_ass = s.frequenzaAssolutaCumulativa(dati)
        cum_rel = s.frequenzaRelativaCumulativa(dati)

        # tabella frequenze
        righe = [f"{'Valore':>10}{'f ass':>8}{'f rel':>10}{'F ass':>8}{'F rel':>10}"]
        for v in sorted(set(dati)):
            righe.append(
                f"{fmt(v):>10}{s.frequenzaAssoluta(v, dati):>8}"
                f"{s.frequenzaRelativa(v, dati):>10.4f}{cum_ass[v]:>8}{cum_rel[v]:>10.4f}"
            )
        self.scrivi(self.area_freq, "\n".join(righe))

        # indici
        out = [
            f"N osservazioni        : {len(dati)}",
            "",
            "-- Posizione --",
            f"Media campionaria     : {fmt(s.mediaCampionaria(dati))}",
            f"Mediana campionaria   : {fmt(s.medianaCampionaria(dati))}",
            f"Moda campionaria      : {fmt(s.modaCampionaria(dati))}",
            "",
            "-- Variabilità --",
            f"Varianza              : {fmt(s.varianza(dati))}",
            f"Deviazione standard   : {fmt(s.deviazioneStandard(dati))}",
            f"Scarto medio assoluto : {fmt(s.scartoMedioAssoluto(dati))}",
            f"Ampiezza di campo     : {fmt(s.ampiezzaCampoVarianza(dati))}",
            "",
            "-- Forma --",
        ]
        if s.deviazioneStandard(dati) == 0:
            out.append("Asimmetria e curtosi non definite (deviazione standard = 0)")
        else:
            out += [
                f"Indice di asimmetria  : {fmt(s.indiceAsimmetria(dati))}",
                f"Curtosi               : {fmt(s.curtosi(dati))}",
                f"Curtosi in eccesso    : {fmt(s.curtosiEccesso(dati))}",
            ]
        self.scrivi(self.area_indici, "\n".join(out))

    def apri_grafici(self):
        try:
            dati = self.leggi_dati()
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            return
        FinestraGrafici(self, dati)

    def pulisci(self):
        self.ultimi_dati = None
        self.entry.delete(0, tk.END)
        self.scrivi(self.area_freq, "")
        self.scrivi(self.area_indici, "")


if __name__ == "__main__":
    App().mainloop()