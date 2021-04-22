class House:
    def __init__(self, origin, size):
        self._x = origin[0]
        self._z = origin[1]
        self._size = size

    def _setEntrance(self,area):
        return 0
    
    def _fillBase(self):
        return 0

    def build(self):
        return 0

def housingFitness(block_counts, height_counts):
    # Determining the fitness 
    #   Water increases fitness
    #   Height differential increases fitness
    if 'minecraft:water' in block_counts:
        fitness = len(height_counts) + (block_counts['minecraft:water']*3.5)
    else:
        fitness = len(height_counts)
    return fitness