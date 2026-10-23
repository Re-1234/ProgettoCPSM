import math


class FunzioniStatistiche:
    # frequenze
    def frequenzaAssoluta(self, elemento, array: list):
        c = 0
        for x in array:
            if x == elemento:
                c += 1
        return c

    def creazioneArrayFrequenzeAssolute(self, array: list):
        return [self.frequenzaAssoluta(x, array) for x in array]

    def frequenzaRelativa(self, elemento, array: list):
        return self.frequenzaAssoluta(elemento, array) / len(array)

    def frequenzaAssolutaCumulativa(self, array: list):
        cumulata = {}
        totale = 0
        for valore in sorted(set(array)):
            totale += self.frequenzaAssoluta(valore, array)
            cumulata[valore] = totale
        return cumulata

    def frequenzaRelativaCumulativa(self, array: list):
        n = len(array)
        assolute = self.frequenzaAssolutaCumulativa(array)
        return {valore: f / n for valore, f in assolute.items()}

    # indici di posizione
    def mediaCampionaria(self, array: list):
        return sum(array) / len(array)

    def medianaCampionaria(self, array: list):
        a = sorted(array)
        n = len(a)
        if n % 2 == 0:
            return (a[n // 2] + a[n // 2 - 1]) / 2
        return a[n // 2]

    def modaCampionaria(self, array: list):
        freq = self.creazioneArrayFrequenzeAssolute(array)
        return array[freq.index(max(freq))]

    # indici di variabilità
    def varianza(self, array: list):
        media = self.mediaCampionaria(array)
        return sum((x - media) ** 2 for x in array) / len(array)

    def deviazioneStandard(self, array: list):
        return self.varianza(array) ** 0.5

    def scartoMedioAssoluto(self, array: list):
        # corretto: si scorrono TUTTI i valori (non set(array)),
        # altrimenti i valori ripetuti verrebbero contati una sola volta
        c = self.mediaCampionaria(array)
        return sum(abs(x - c) for x in array) / len(array)

    def ampiezzaCampoVarianza(self, array: list):
        return max(array) - min(array)

    # indici di forma
    def indiceAsimmetria(self, array: list):
        n = len(array)
        media = self.mediaCampionaria(array)
        s = self.deviazioneStandard(array)
        m3 = sum((x - media) ** 3 for x in array) / n
        return m3 / s ** 3

    def curtosi(self, array: list):
        n = len(array)
        media = self.mediaCampionaria(array)
        s = self.deviazioneStandard(array)
        m4 = sum((x - media) ** 4 for x in array) / n
        return m4 / s ** 4

    def curtosiEccesso(self, array: list):
        return self.curtosi(array) - 3

    # quartili (stesso metodo della mediana: p-esimo quantile)
    def percentile(self, array: list, p: float):
        """p-esimo quantile, con 0 < p < 1 (dati ordinati, posizioni da 1).
        Se n*p non e' intero si prende il dato in posizione ceil(n*p);
        se n*p e' intero si fa la media tra i dati in posizione n*p e n*p + 1."""
        if not 0 < p < 1:
            raise ValueError("p deve essere compreso tra 0 e 1 (estremi esclusi)")
        a = sorted(array)
        k = len(a) * p
        if abs(k - round(k)) < 1e-9:
            k = round(k)
            return (a[k - 1] + a[k]) / 2
        return a[math.ceil(k) - 1]

    def primoQuartile(self, array: list):
        return self.percentile(array, 0.25)

    def secondoQuartile(self, array: list):
        return self.medianaCampionaria(array)

    def terzoQuartile(self, array: list):
        return self.percentile(array, 0.75)

    def scartoInterquartile(self, array: list):
        return self.terzoQuartile(array) - self.primoQuartile(array)

    def limitiOutlier(self, array: list):
        q1 = self.primoQuartile(array)
        q3 = self.terzoQuartile(array)
        iqr = q3 - q1
        return q1 - 1.5 * iqr, q3 + 1.5 * iqr

    def outlier(self, array: list):
        inf, sup = self.limitiOutlier(array)
        return sorted(x for x in array if x < inf or x > sup)

    # dati bivariati
    def covarianza(self, x: list, y: list):
        if len(x) != len(y):
            raise ValueError("x e y devono avere lo stesso numero di valori")
        mx = self.mediaCampionaria(x)
        my = self.mediaCampionaria(y)
        return sum((a - mx) * (b - my) for a, b in zip(x, y)) / len(x)

    def coefficienteCorrelazione(self, x: list, y: list):
        sx = self.deviazioneStandard(x)
        sy = self.deviazioneStandard(y)
        if math.isclose(sx, 0, abs_tol=1e-12) or math.isclose(sy, 0, abs_tol=1e-12):
            raise ValueError("Correlazione non definita: una delle due variabili è costante")
        return self.covarianza(x, y) / (sx * sy)

    # retta di regressione  y = a + b x  (minimi quadrati)
    def coefficienteAngolare(self, x: list, y: list):
        vx = self.varianza(x)
        if math.isclose(vx, 0, abs_tol=1e-12):
            raise ValueError("Retta non definita: tutti i valori di X sono uguali")
        return self.covarianza(x, y) / vx

    def intercetta(self, x: list, y: list):
        return self.mediaCampionaria(y) - self.coefficienteAngolare(x, y) * self.mediaCampionaria(x)

    # classi: intervalli [a, b); l'ultima classe include anche l'estremo b
    def frequenzaAssolutaClasse(self, array: list, a, b, ultima: bool = False):
        c = 0
        for x in array:
            if a <= x < b or (ultima and x == b):
                c += 1
        return c

    def frequenzaRelativaClasse(self, array: list, a, b, ultima: bool = False):
        return self.frequenzaAssolutaClasse(array, a, b, ultima) / len(array)

    def ampiezzaClasse(self, a, b):
        return b - a

    def densitaFrequenza(self, array: list, a, b, ultima: bool = False):
        """Frequenza assoluta divisa per l'ampiezza della classe."""
        return self.frequenzaAssolutaClasse(array, a, b, ultima) / (b - a)

    def frequenzeClassi(self, array: list, classi: list):
        """Frequenze assolute di ogni classe (lista di coppie (a, b) ordinate)."""
        return [
            self.frequenzaAssolutaClasse(array, a, b, k == len(classi) - 1)
            for k, (a, b) in enumerate(classi)
        ]