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