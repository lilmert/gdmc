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
    def __init__(self, origin, size, builder, build_map):
        super().__init__(origin, size)
   #     self._floors = self._calcFloors() 
        self._houseSize = size - 4
        self._houseX = self._x + 2
        self._houseZ = self._z + 2
        self._builder = builder
        self._build_map = build_map
        self._color = self._setColor()
        self._direction = self._setDirection()
        self._first_floor_level = self._layFirstFloor()
        self._buildCorners()
        self._buildFrontWall()

    def _setColor(self):
        rand = random.rand()
        if(rand < 0.25):
            return 'orange_wool'
        elif(rand < 0.5):
            return 'yellow_wool'
        elif(rand < 0.75):
            return 'green_wool'
        else:
            return 'red_wool'

    def _setDirection(self):
        map_centerX = self._builder.getX() - 0.5 * self._builder.getSize()
        map_centerZ = self._builder.getZ() - 0.5 * self._builder.getSize()
        direction = ''
        if(abs(self._houseX - map_centerX) > abs(self._houseZ - map_centerZ)):
            if(self._houseX > map_centerX):
                direction = 'W'
                front_x = self._x
                front_z = int(self._z + self._size * 0.5)
                self._build_map.setBuildAt(front_x, front_z, 3)
            else:
                direction = 'E'
                front_x = self._x + self._size - 1
                front_z = int(self._z + self._size * 0.5)
                self._build_map.setBuildAt(front_x, front_z, 3)
        else:
            if(self._z > map_centerZ):
                direction = 'S'
                front_x = int(self._x + self._size * 0.5)
                front_z = self._z + self._size - 1
                self._build_map.setBuildAt(front_x, front_z, 3)
            else:
                direction = 'N'
                front_x = int(self._x + self._size * 0.5)
                front_z = self._z
                self._build_map.setBuildAt(front_x, front_z, 3)
        return direction

    def _calcFloors(self):
        if(self._size >= 9):
            self._floors = 2

    def _layFirstFloor(self):
        average = 0
        for i in range(self._houseX, self._houseX + self._houseSize):
            for j in range(self._houseZ, self._houseZ + self._houseSize):
                average += self._builder.getHeightAt(i, j)
        average /= self._houseSize * self._houseSize
        average = int(average) - 1
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

    def _buildFrontWall(self):
        if(self._direction == 'N' or self._direction == 'S'):
            z1 = self._houseZ
            z2 = self._houseZ + self._houseSize - 1
            if(self._direction == 'N'):
                x = self._houseX
            if(self._direction == 'S'):
                x = self._houseX + self._houseSize - 1

            # adjacent to corners
            for i in range(1, 5):
                if( i == 1 or i == 3):
                    interfaceUtils.setBlock(x, self._first_floor_level + i, z1 + 1, self._color)
                    interfaceUtils.setBlock(x, self._first_floor_level + i, z2 - 1, self._color)
                if(i == 2):
                    interfaceUtils.setBlock(x, self._first_floor_level + i, z1 + 1, 'glass_pane')
                    interfaceUtils.setBlock(x, self._first_floor_level + i, z2 - 1, 'glass_pane')  
                if(i == 4):
                    interfaceUtils.setBlock(x, self._first_floor_level + i, z1 + 1, 'dark_oak_log')
                    interfaceUtils.setBlock(x, self._first_floor_level + i, z2 - 1, 'dark_oak_log')

            # one away from middle
            for i in range(1, 5):
                interfaceUtils.setBlock(x, self._first_floor_level + i, z1 + 2, 'dark_oak_log')
                interfaceUtils.setBlock(x, self._first_floor_level + i, z2 - 2, 'dark_oak_log')

            # middle
            interfaceUtils.setBlock(x, self._first_floor_level + 1, z1 + 3, 'dark_oak_door[half=lower, facing=east]')
            interfaceUtils.setBlock(x, self._first_floor_level + 2, z1 + 3, 'dark_oak_door[half=upper, facing=east]')
            interfaceUtils.setBlock(x, self._first_floor_level + 3, z1 + 3, self._color)
            interfaceUtils.setBlock(x, self._first_floor_level + 4, z1 + 3, 'dark_oak_log')
            
        if(self._direction == 'E' or self._direction == 'W'):
            x1 = self._houseX
            x2 = self._houseX + self._houseSize - 1
            if(self._direction == 'E'):
                z = self._houseZ
            if(self._direction == 'W'):
                z = self._houseZ + self._houseSize - 1

            # adjacent to corners
            for i in range(1, 5):
                if( i == 1 or i == 3):
                    interfaceUtils.setBlock(x1 + 1, self._first_floor_level + i, z, self._color)
                    interfaceUtils.setBlock(x2 - 1, self._first_floor_level + i, z, self._color)
                if(i == 2):
                    interfaceUtils.setBlock(x1 + 1, self._first_floor_level + i, z, 'glass_pane')
                    interfaceUtils.setBlock(x2 - 1, self._first_floor_level + i, z, 'glass_pane')  
                if(i == 4):
                    interfaceUtils.setBlock(x1 + 1, self._first_floor_level + i, z, 'dark_oak_log')
                    interfaceUtils.setBlock(x2 - 1, self._first_floor_level + i, z, 'dark_oak_log')

            # one away from middle
            for i in range(1, 5):
                interfaceUtils.setBlock(x1 + 2, self._first_floor_level + i, z, 'dark_oak_log')
                interfaceUtils.setBlock(x2 - 2, self._first_floor_level + i, z, 'dark_oak_log')

            # middle
            interfaceUtils.setBlock(x1 + 3, self._first_floor_level + 1, z, 'dark_oak_door[half=lower, facing=east]')
            interfaceUtils.setBlock(x1 + 3, self._first_floor_level + 2, z, 'dark_oak_door[half=upper, facing=east]')
            interfaceUtils.setBlock(x1 + 3, self._first_floor_level + 3, z, self._color)
            interfaceUtils.setBlock(x1 + 3, self._first_floor_level + 4, z, 'dark_oak_log')
        


    #    if(self._direction == 'E'):
    #    if(self._direction == 'S'):
    #    if(self._direction == 'N'):
    # lay first wall function

    # lay second wall function

    # build attic peak walls

    # build roof