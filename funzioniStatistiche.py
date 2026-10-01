def mediaCampionaria(self,array : list):
    for i in array:
        self.c += i
    self.c /= len(array)
    return self.c

def medianaCampionaria(self,array : list):
    if len(array) % 2 == 0:
        self.c = len(array) // 2
        self.a = (array[self.c] + array[self.c - 1])/2
        return self.a
    else:
        self.c = len(array) // 2
        return self.c

