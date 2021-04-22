from buildUtils import Builder
import numpy as np

##################################################################
##################### FITNESS FUNCTIONS  #########################
##################################################################

def housingFitness(block_counts, height_counts, centrality):
    return 0

def townCentreFitness(block_counts, height_counts, centrality):
    if 'minecraft:water' in block_counts:
        water_count = block_counts['minecraft:water']
    else:
        water_count = 0
    
    water_value = 500
    if 10 < water_count < 200:
        water_value = 5
    elif water_count < 10:
        water_value = 100
    
    height_diff = sum(np.diff(list(height_counts.keys())))
    return (height_diff*2) + water_value + (centrality*0.5)

##################################################################
##################### STRUCTURE CLASSES ##########################
##################################################################

class Structure:
    def __init__(self, origin, size, direction):
        self._x = origin[0]
        self._z = origin[1]
        self._size = size
        self._dir = direction

    def getSize(self):
        return self._size
    
    def getDirection(self):
        return self._dir
    
    def build(self, builder):
        for i in range(self._size):
            for j in range(self._size):
                builder.setBlockAt(self._x + i, 0, self._z + j, "cobblestone")
    