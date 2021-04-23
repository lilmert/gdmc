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
    def __init__(self, origin, size, builder):
        self._x = origin[0]
        self._z = origin[1]
        self._size = size
        self._builder = builder

    def getSize(self):
        return self._size
    
    def build(self):
        for i in range(self._size):
            for j in range(self._size):
                self._builder.setBlockAt(self._x + i, 0, self._z + j, "cobblestone")
    
    def clear(self):
        _, heights, _ = self._builder.getPlotStats(self._x, self._z, self._size)
        max_height = max(list(heights.keys()))
        for i in range(self._size):
            for j in range(self._size):
                for y_i in range(10):
                    interfaceUtils.placeBlockBatched(self._x+i, max_height+y_i, self._z+j, "air")


class TownCentre(Structure):
    def __init__(self, origin, size, builder):
        super().__init__(origin, size, builder)
        self._blocks = [
            "cobblestone", 
            "grass_path", 
            "mossy_cobblestone",
            "grass_block"
        ]

        # set base level of the plot
        self._base_level = self._findAverageHeight() - 1

        # create the foundation
        print("Laying foundation")
        self._layFoundation()
        print("Done laying foundation")

        # clear all blocks above the structure
        self.clear()
    
    def _findAverageHeight(self):
        total_height = 0
        total_tiles = self._size**2
        for i in range(self._x, self._x + self._size):
            for j in range(self._z, self._z + self._size):
                total_height += self._builder.getHeightAt(i, j)        
        return math.floor(total_height / total_tiles) 

    def _layFoundation(self):
        for i in range(self._x, self._x + self._size):
            for j in range(self._z, self._z + self._size):
                curHeight = self._builder.getHeightAt(i, j)
                while(curHeight < self._base_level):
                    interfaceUtils.placeBlockBatched(i, curHeight, j, 'stone_bricks')
                    curHeight += 1
                while(curHeight > self._base_level):
                    interfaceUtils.placeBlockBatched(i, curHeight, j, 'air')
                    curHeight -= 1                
                interfaceUtils.placeBlockBatched(i, curHeight, j, self._blocks[random.randint(0, len(self._blocks))])

    def buildPaths(self, build_map):
        mid_point = int((self._size - 1) / 2)
        l_switch = True
        l_side = (-1, 1)
        # bottom to top
        for j in range(-1, 2):
            x = self._builder._x
            z = self._builder._z + self._z + mid_point + j
            top = self._builder._x + self._builder._size
            while (x < top):
                if self._x <= x < (self._x+self._size):
                    x += 1
                else:
                    y = self._builder.getHeightAt(x, z)
                    block = self._builder.getBlockAt(x, -1, z)
                    if block == "minecraft:water":
                        self._builder.setBlockAt(x, -1, z, "oak_planks")
                        build_map.setBuildAt(x,z, 2)
                    else:
                        self._builder.setBlockAt(x, -1, z, "grass_path")
                        build_map.setBuildAt(x,z, 2)
                    
                    # clear above path
                    for y_i in range(10):
                        if interfaceUtils.getBlock(x, y + y_i, z) == "minecraft:oak_fence":
                            pass
                        else:
                            interfaceUtils.placeBlockBatched(x, y + y_i, z, "air")
                    
                    # build path lamps
                    if j == 0:
                        if (x % 7 == 0):
                            l_z = self._builder._z + self._z + mid_point + l_side[l_switch]
                            for ii in range(6):
                                interfaceUtils.placeBlockBatched(x, y+ii, l_z, "oak_fence")
                            interfaceUtils.placeBlockBatched(x, y+ii, z, "sea_lantern")
                            l_switch = not(l_switch)

                    x += 1
        
        # left to right
        for i in range(-1, 2):
            z = self._builder._z
            x = self._builder._x + self._x + mid_point + i
            bound = self._builder._z + self._builder._size
            while (z < bound):
                if self._z <= z < (self._z+self._size):
                    z += 1
                else:
                    y = self._builder.getHeightAt(x, z)
                    block = self._builder.getBlockAt(x, -1, z)
                    if block == "minecraft:water":
                        self._builder.setBlockAt(x, -1, z, "oak_planks")
                        build_map.setBuildAt(x,z, 2)
                    else:
                        self._builder.setBlockAt(x, -1, z, "grass_path")
                        build_map.setBuildAt(x,z, 2)
                    
                    # clear above path
                    for y_i in range(10):
                        if interfaceUtils.getBlock(x, y + y_i, z) == "minecraft:oak_fence":
                            pass
                        else:
                            interfaceUtils.placeBlockBatched(x, y + y_i, z, "air")
                    
                    # build path lamps
                    if i == 0:
                        if (z % 7 == 0):
                            l_x = self._builder._x + self._x + mid_point + l_side[l_switch]
                            for jj in range(6):
                                interfaceUtils.placeBlockBatched(l_x, y+jj, z, "oak_fence")
                            interfaceUtils.placeBlockBatched(x, y+jj, z, "sea_lantern")
                            l_switch = not(l_switch)
                    z += 1
                    

class House(Structure):
    def __init__(self, origin, size, builder):
        super().__init__(origin, size, builder)
        #self._floors = self._calcFloors() 
        self._houseSize = size - 4
        self._houseX = self._x + 2
        self._houseZ = self._z + 2
        #self._direction = self._setDirection()
        self.clear()
        self._first_floor_level = self._layFirstFloor()
        self._buildCorners()

    #def _setDirection(self):
        #map_centerX = BUILDER.
        #if(house.)

    #def _calcFloors(self):
        #if(self._size >= 9):
            #self._floors = 2

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