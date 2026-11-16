# Statistica descrittiva – applicazione desktop in Python

Programma con interfaccia grafica per l'analisi statistica descrittiva di un campione, scritto interamente in **Python**. Permette di lavorare con:

- **campioni semplici** (una variabile): tabella delle frequenze, indici di posizione, variabilità e forma, quartili, box plot, grafici delle frequenze e, a scelta, **classi** di valori con istogramma;
- **campioni bivariati** (coppie X, Y): covarianza, coefficiente di correlazione campionaria, retta di regressione, diagramma di dispersione e box plot di X e di Y.

---

## Tecnologie utilizzate

| Tecnologia | Ruolo nel progetto |
|---|---|
| **Python 3** | Linguaggio di tutto il progetto (sviluppato e provato con Python 3.12) |
| **Tkinter / ttk** | Interfaccia grafica (finestre, campi di testo, tabelle, pulsanti) |
| **Matplotlib** | Grafici, incorporati direttamente nelle finestre Tkinter |
| **Libreria standard (`math`)** | Tutti i calcoli statistici sono scritti a mano, senza NumPy o pandas |

### Python e libreria standard

Tutta la logica statistica è implementata in Python puro: nessuna libreria esterna fa i calcoli. Le formule sono scritte esplicitamente nella classe `FunzioniStatistiche`, così il codice resta leggibile e vicino a quello visto a lezione. L'unico modulo importato per i calcoli è `math` della libreria standard.


### Matplotlib incorporato in Tkinter

I grafici sono disegnati con [Matplotlib](https://matplotlib.org/) e incorporati nelle finestre Tkinter tramite:

- **`Figure`**: l'API orientata agli oggetti di Matplotlib, senza `pyplot`, per non usare stato globale e integrarsi bene con il ciclo eventi di Tkinter;
- **`FigureCanvasTkAgg`**: il "canvas" che mostra la figura dentro una finestra Tkinter;
- **`NavigationToolbar2Tk`**: la barra con zoom, spostamento e salvataggio dell'immagine.

Tipi di grafico utilizzati: barre (`bar`), asta (`stem`), linee (`plot`), torta (`pie`), box plot (`bxp`), istogramma (`bar` con larghezze variabili) e diagramma di dispersione (`scatter`).

Due scelte tecniche da segnalare:

- **Il box plot è costruito con `Axes.bxp`** e non con `boxplot`: in questo modo Matplotlib disegna i quartili calcolati dalla nostra classe e non quelli calcolati con il suo metodo (che interpola e può dare valori leggermente diversi). Il disegno è quindi sempre coerente con i numeri mostrati nei risultati. Il codice funziona sia con le versioni recenti di Matplotlib (parametro `orientation`) sia con quelle precedenti (parametro `vert`).
- **`sincronizza_canvas`** (in `grafici.py`) allinea la figura alla dimensione reale del widget subito dopo l'apertura della finestra: senza, il grafico poteva apparire leggermente più grande dell'area e venire tagliato finché non si ridimensionava la finestra.

---

## Architettura

Il progetto separa nettamente **logica** e **interfaccia**:

```
┌─────────────────────────────────────────────────────────┐
│  Interfaccia (Tkinter)                                  │
│  main.py   bivariati.py   classi.py           │
│  tabella.py          grafici.py (Matplotlib)            │
└──────────────────────────┬──────────────────────────────┘
                           │ usa
┌──────────────────────────▼──────────────────────────────┐
│  Logica (Python puro, nessuna dipendenza grafica)       │
│  funzioni_statistiche.py → classe FunzioniStatistiche   │
└─────────────────────────────────────────────────────────┘
```

La classe `FunzioniStatistiche` non importa né Tkinter né Matplotlib: si può usare e verificare da sola, anche senza avviare l'interfaccia.

### Struttura dei file

| File | Contenuto |
|---|---|
| `main.py` | **Punto di avvio.** Finestra principale con la scelta del tipo di campione e la schermata del campione semplice |
| `funzioniStatistiche.py` | Classe `FunzioniStatistiche` con tutte le formule |
| `grafici.py` | Grafici del campione semplice (barre, asta, linee, torta, box plot, istogramma) e relativa finestra |
| `Classi.py` | Pagina per definire gli intervalli delle classi e tabella delle frequenze per classi |
| `Bivariati.py` | Schermata del campione bivariato e finestra con diagramma di dispersione e box plot |
| `Tabella.py` | Widget riutilizzabile per inserire dati in tabella |

### Schermate e flusso

La finestra principale (`App`) contiene due schermate (`Frame`) che si alternano con la scelta "Tipo di campione":

- **Campione semplice**: campo di testo + pulsanti *Calcola*, *Classi...*, *Mostra grafici*, *Pulisci*;
- **Campione bivariato**: tabella X/Y + pulsanti *Calcola*, *Dati bivariati*, *Pulisci*.

Con le **classi attive** la tabella delle frequenze diventa quella per classi e nei grafici resta disponibile solo l'**istogramma**.

---

## Metodi statistici e convenzioni

| Elemento | Convenzione adottata |
|---|---|
| Varianza e deviazione standard | Divisione per **n** (non n − 1) |
| Covarianza | Divisione per **n**, coerente con la varianza; il coefficiente di correlazione non cambia |
| Quartili | Metodo dei quantili: se *n·p* non è intero si prende il dato in posizione ⌈*n·p*⌉, altrimenti la media tra le posizioni *n·p* e *n·p* + 1. Per *p* = 0,5 coincide con la mediana |
| Outlier | Valori fuori dall'intervallo [Q1 − 1,5·IQR ; Q3 + 1,5·IQR]; i baffi del box plot arrivano al dato più estremo non anomalo |
| Retta di regressione | Minimi quadrati: *b* = cov(X, Y) / var(X), *a* = media(Y) − *b*·media(X) |
| Classi | Intervalli **[a, b)**: includono l'estremo inferiore ed escludono il superiore; l'ultima classe include anche il superiore |
| Istogramma | Larghezza di ogni barra = ampiezza della classe. Con ampiezze uguali l'altezza è la frequenza assoluta; con ampiezze diverse è la **densità di frequenza** (frequenza / ampiezza), così l'area di ogni barra resta proporzionale alla frequenza |
| Grafici delle frequenze | Barre, asta e linee rappresentano la **frequenza assoluta** |

---

## Requisiti e avvio

### Installazione

1. Installare **Python 3** (da [python.org](https://www.python.org/downloads/)). Su Windows e macOS Tkinter è incluso. Su Linux (Debian/Ubuntu) può servire:
   ```bash
   sudo apt install python3-tk
   ```
2. Installare Matplotlib (è l'unica dipendenza esterna; si porta dietro NumPy da sola). Serve almeno la versione 3.4:
   ```bash
   pip install matplotlib
   ```

### Esecuzione

Con tutti i file nella **stessa cartella**:

```bash
python main.py
```

---

## Uso rapido

- **Campione semplice**: scrivere i numeri nel campo di testo, separati da spazio, virgola o punto e virgola (es. `2, 4, 4, 5, 7, 9`), poi premere *Calcola*. Il separatore decimale è il punto.
- **Classi**: il pulsante *Classi...* apre la pagina in cui aggiungere, modificare o eliminare gli intervalli.
- **Campione bivariato**: scegliere "Campione bivariato", compilare la tabella (si può incollare da Excel) e premere *Calcola*; *Dati bivariati* apre i grafici. Nelle celle della tabella la virgola è accettata come separatore decimale.