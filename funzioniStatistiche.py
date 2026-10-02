class FunzioniStatistiche:

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

    def frequenzaAssoultaCummulativa(self, array: list):
        b = self.creazioneArrayFrequenzeAssolute(array)
        for

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

