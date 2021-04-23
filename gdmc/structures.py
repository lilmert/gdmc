from buildUtils import Builder
import numpy as np
from numpy import random
import math
import interfaceUtils

##################################################################
##################### FITNESS FUNCTIONS  #########################
##################################################################

def housingFitness(block_counts, height_counts, centrality):
    if 'minecraft:water' in block_counts:
        water_count = block_counts['minecraft:water']
    else:
        water_count = 0
    height_diff = sum(np.diff(list(height_counts.keys())))
    return (height_diff * 2) + (water_count * 2)

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
    def __init__(self, origin, size):
        self._x = origin[0]
        self._z = origin[1]
        self._size = size

    def getSize(self):
        return self._size
    
    def build(self, builder):
        for i in range(self._size):
            for j in range(self._size):
                builder.setBlockAt(self._x + i, 0, self._z + j, "cobblestone")

class House(Structure):
    def __init__(self, origin, size, builder):
        super().__init__(origin, size)
   #     self._floors = self._calcFloors() 
        self._houseSize = size - 4
        self._houseX = self._x + 2
        self._houseZ = self._z + 2
        self._builder = builder
#        self._direction = self._setDirection()
        self._first_floor_level = self._layFirstFloor()
        self._buildCorners()

#    def _setDirection(self):
#        map_centerX = BUILDER.
#        if(house.)

    def _calcFloors(self):
        if(self._size >= 9):
            self._floors = 2

    def _layFirstFloor(self):
        average = 0
        for i in range(self._houseX, self._houseX + self._houseSize):
            for j in range(self._houseZ, self._houseZ + self._houseSize):
                average += self._builder.getHeightAt(i, j)
        average /= self._houseSize * self._houseSize
        average = math.floor(average)
        for i in range(self._houseX, self._houseX + self._houseSize):
            for j in range(self._houseZ, self._houseZ + self._houseSize):
                curHeight = self._builder.getHeightAt(i, j)
                while(curHeight < average):
                    interfaceUtils.setBlock(i, curHeight, j, 'stone_bricks')
                    curHeight += 1
                while(curHeight > average):
                    interfaceUtils.setBlock(i, curHeight, j, 'air')
                    curHeight -= 1
                interfaceUtils.setBlock(i, curHeight, j, 'dark_oak_planks')
        return curHeight

    def _buildCorners(self):
        for i in range(0, 5):
            interfaceUtils.setBlock(self._houseX, self._first_floor_level + i, self._houseZ, "dark_oak_log")
            interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + i, self._houseZ, "dark_oak_log")
            interfaceUtils.setBlock(self._houseX, self._first_floor_level + i, self._houseZ + self._houseSize - 1, "dark_oak_log")
            interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + i, self._houseZ + self._houseSize - 1, "dark_oak_log")
            
        
    # lay  2nd floor function
        # for every block in height = 3, inside the house perimeter (size + 1 to size - 1)
            # set block type to dark oak slab on the upper side
    # lay front wall function

    # lay first wall function

    # lay second wall function

    # build attic peak walls

    # build roof