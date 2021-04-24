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
        self._buildFountain()
    
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
                    
    def _buildFountain(self):
        centerX = self._x + math.floor(0.5 * self._size)
        centerZ = self._z + math.floor(0.5 * self._size)

        for i in range(3):
            if(i == 2):
                interfaceUtils.setBlock(centerX + 3, self._base_level + 1 + i, centerZ + 3, 'stone_brick_slab')
                interfaceUtils.setBlock(centerX + 3, self._base_level + 1 + i, centerZ - 3, 'stone_brick_slab')
                interfaceUtils.setBlock(centerX - 3, self._base_level + 1 + i, centerZ + 3, 'stone_brick_slab')
                interfaceUtils.setBlock(centerX - 3, self._base_level + 1 + i, centerZ - 3, 'stone_brick_slab')
            else:
                interfaceUtils.setBlock(centerX + 3, self._base_level + 1 + i, centerZ + 3, 'chiseled_stone_bricks')
                interfaceUtils.setBlock(centerX + 3, self._base_level + 1 + i, centerZ - 3, 'chiseled_stone_bricks')
                interfaceUtils.setBlock(centerX - 3, self._base_level + 1 + i, centerZ + 3, 'chiseled_stone_bricks')
                interfaceUtils.setBlock(centerX - 3, self._base_level + 1 + i, centerZ - 3, 'chiseled_stone_bricks')
        for i in range(5):
            interfaceUtils.setBlock(centerX - 2 + i, self._base_level + 1, centerZ - 3, 'stone_brick_stairs[facing=south]')
            interfaceUtils.setBlock(centerX - 2 + i, self._base_level + 1, centerZ + 3, 'stone_brick_stairs[facing=north]')
            interfaceUtils.setBlock(centerX - 3, self._base_level + 1, centerZ - 2 + i, 'stone_brick_stairs[facing=east]')
            interfaceUtils.setBlock(centerX + 3, self._base_level + 1, centerZ - 2 + i, 'stone_brick_stairs[facing=west]')
        
        interfaceUtils.setBlock(centerX, self._base_level + 1, centerZ - 1, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX - 1, self._base_level + 1, centerZ, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX, self._base_level + 1, centerZ + 1, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX + 1, self._base_level + 1, centerZ, 'chiseled_stone_bricks')

        interfaceUtils.setBlock(centerX, self._base_level + 2, centerZ - 1, 'stone_brick_stairs[facing=south]')
        interfaceUtils.setBlock(centerX - 1, self._base_level + 2, centerZ, 'stone_brick_stairs[facing=north]')
        interfaceUtils.setBlock(centerX, self._base_level + 2, centerZ + 1, 'stone_brick_stairs[facing=east]')
        interfaceUtils.setBlock(centerX + 1, self._base_level + 2, centerZ, 'stone_brick_stairs[facing=west]')

        interfaceUtils.setBlock(centerX, self._base_level + 6, centerZ - 1, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX - 1, self._base_level + 6, centerZ, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX, self._base_level + 6, centerZ + 1, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX + 1, self._base_level + 6, centerZ, 'chiseled_stone_bricks')



        for i in range(-1, 2):
            for j in range(-1, 2):
                interfaceUtils.setBlock(centerX + i, self._base_level + 7, centerZ + j, 'chiseled_stone_bricks')
        for i in range(2):
            interfaceUtils.setBlock(centerX, self._base_level + 7 + i, centerZ - 2, 'chiseled_stone_bricks')
            interfaceUtils.setBlock(centerX - 2, self._base_level + 7 + i, centerZ, 'chiseled_stone_bricks')
            interfaceUtils.setBlock(centerX, self._base_level + 7 + i, centerZ + 2, 'chiseled_stone_bricks')
            interfaceUtils.setBlock(centerX + 2, self._base_level + 7 + i, centerZ, 'chiseled_stone_bricks')

        interfaceUtils.setBlock(centerX, self._base_level + 9, centerZ - 2, 'stone_brick_stairs[facing=south]')
        interfaceUtils.setBlock(centerX - 2, self._base_level + 9, centerZ, 'stone_brick_stairs[facing=east]')
        interfaceUtils.setBlock(centerX, self._base_level + 9, centerZ + 2, 'stone_brick_stairs[facing=north]')
        interfaceUtils.setBlock(centerX + 2, self._base_level + 9, centerZ, 'stone_brick_stairs[facing=west]')
        
        for i in range(10):
            interfaceUtils.setBlock(centerX, self._base_level + i, centerZ, 'chiseled_stone_bricks')
        interfaceUtils.setBlock(centerX, self._base_level + 10, centerZ, 'water')





class House(Structure):
    def __init__(self, origin, size, builder, build_map):
        super().__init__(origin, size, builder)
        self._houseSize = size - 4
        self._houseX = self._x + 2
        self._houseZ = self._z + 2
        self._build_map = build_map
        self._color = self._setColor()
        self._direction = self._setDirection()
        self._first_floor_level = self._layFirstFloor()
        self._buildCorners()
        self._walls()
        self._decorateInterior()

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
            else:
                direction = 'E'
        else:
            if(self._z > map_centerZ):
                direction = 'S'
            else:
                direction = 'N'
        return direction

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

    def _walls(self):
        self._buildFrontWall()
        if(self._direction == 'S'):
            self._xAxisWall(self._houseZ)
            self._xAxisWall(self._houseZ + self._houseSize - 1)
            self._zAxisWall(self._houseX)
            self._zAxisRoof()
        if(self._direction == 'N'):
            self._xAxisWall(self._houseZ)
            self._xAxisWall(self._houseZ + self._houseSize - 1)
            self._zAxisWall(self._houseX + self._houseSize - 1)
            self._zAxisRoof()
        if(self._direction == 'W'):
            self._zAxisWall(self._houseX)
            self._zAxisWall(self._houseX + self._houseSize - 1)
            self._xAxisWall(self._houseZ)
            self._xAxisRoof()
        if(self._direction == 'E'):
            self._zAxisWall(self._houseX)
            self._zAxisWall(self._houseX + self._houseSize - 1)
            self._xAxisWall(self._houseZ + self._houseSize - 1)
            self._xAxisRoof()

    def _zAxisWall(self, x):
        z1 = self._houseZ
        for height in range(1, 5):
            for i in range(1, 6):
                if(height == 4):
                    interfaceUtils.setBlock(x, self._first_floor_level + height, z1 + i, 'dark_oak_log')
                    continue
                if(height == 2 and (i == 2 or i == 4)):
                    interfaceUtils.setBlock(x, self._first_floor_level + height, z1 + i, 'glass_pane')
                else:
                    interfaceUtils.setBlock(x, self._first_floor_level + height, z1 + i, self._color)

    def _xAxisWall(self, z):
        x1 = self._houseX
        for height in range(1, 5):
            for i in range(1, 6):
                if(height == 4):
                    interfaceUtils.setBlock(x1 + i, self._first_floor_level + height, z, 'dark_oak_log')
                    continue
                if(height == 2 and (i == 2 or i == 4)):
                    interfaceUtils.setBlock(x1 + i, self._first_floor_level + height, z, 'glass_pane')
                else:
                    interfaceUtils.setBlock(x1 + i, self._first_floor_level + height, z, self._color)

    def _xAxisRoof(self):
        # creating peaks
        for i in range(1, 6):
            if(i != 2 and i != 4):
                interfaceUtils.setBlock(self._houseX + i, self._first_floor_level + 5, self._houseZ, self._color)
                interfaceUtils.setBlock(self._houseX + i, self._first_floor_level + 5, self._houseZ + self._houseSize - 1, self._color)
            else:
                interfaceUtils.setBlock(self._houseX + i, self._first_floor_level + 5, self._houseZ, 'dark_oak_log')
                interfaceUtils.setBlock(self._houseX + i, self._first_floor_level + 5, self._houseZ + self._houseSize - 1, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + 2, self._first_floor_level + 6, self._houseZ, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + 2, self._first_floor_level + 6, self._houseZ + self._houseSize - 1, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 6, self._houseZ, 'glass_pane')
        interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 6, self._houseZ + self._houseSize - 1, 'glass_pane')
        interfaceUtils.setBlock(self._houseX + 4, self._first_floor_level + 6, self._houseZ, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + 4, self._first_floor_level + 6, self._houseZ + self._houseSize - 1, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 7, self._houseZ, self._color)
        interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 7, self._houseZ + self._houseSize - 1, self._color)

        # shingles
        spacing = -1
        for height in range(4, 9):
            for j in range(self._houseSize):
                if(height == 8):
                    interfaceUtils.setBlock(self._houseX + spacing, self._first_floor_level + height, self._houseZ + j, 'dark_oak_slab')
                    continue
                interfaceUtils.setBlock(self._houseX + spacing, self._first_floor_level + height, self._houseZ + j, 'dark_oak_stairs[facing=east]')
                interfaceUtils.setBlock(self._houseX + self._houseSize - 1 - spacing, self._first_floor_level + height, self._houseZ + j, 'dark_oak_stairs[facing=west]')
            spacing += 1

    def _zAxisRoof(self):
        # creating peaks
        for i in range(1, 6):
            if(i != 2 and i != 4):
                interfaceUtils.setBlock(self._houseX, self._first_floor_level + 5, self._houseZ + i, self._color)
                interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + 5, self._houseZ + i, self._color)
            else:
                interfaceUtils.setBlock(self._houseX, self._first_floor_level + 5, self._houseZ + i, 'dark_oak_log')
                interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + 5, self._houseZ + i, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX, self._first_floor_level + 6, self._houseZ + 2, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + 6, self._houseZ + 2, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX, self._first_floor_level + 6, self._houseZ + 3, 'glass_pane')
        interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + 6, self._houseZ + 3, 'glass_pane')
        interfaceUtils.setBlock(self._houseX, self._first_floor_level + 6, self._houseZ + 4, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + 6, self._houseZ + 4, 'dark_oak_log')
        interfaceUtils.setBlock(self._houseX, self._first_floor_level + 7, self._houseZ + 3, self._color)
        interfaceUtils.setBlock(self._houseX + self._houseSize - 1, self._first_floor_level + 7, self._houseZ + 3, self._color)

        # shingles
        spacing = -1
        for height in range(4, 9):
            for j in range(self._houseSize):
                if(height == 8):
                    interfaceUtils.setBlock(self._houseX + j, self._first_floor_level + height, self._houseZ + spacing, 'dark_oak_slab')
                    continue
                interfaceUtils.setBlock(self._houseX + j, self._first_floor_level + height, self._houseZ + spacing, 'dark_oak_stairs[facing=south]')
                interfaceUtils.setBlock(self._houseX + j, self._first_floor_level + height, self._houseZ + self._houseSize - 1 - spacing, 'dark_oak_stairs[facing=north]')
            spacing += 1

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

            # add stone doorstep and updating build map
            for out in range(1, 3):
                for i in range(3):
                    if(self._direction == 'S'):
                        interfaceUtils.setBlock(x + out, self._first_floor_level, z1 + 2 + i, 'stone_bricks')
                        interfaceUtils.setBlock(x + out, self._first_floor_level + 1, z1 + 2 + i, 'air')            
                        self._build_map.setBuildAt(x + 3, z1 + 3, 3)
                    else:
                        interfaceUtils.setBlock(x - out, self._first_floor_level, z1 + 2 + i, 'stone_bricks')
                        interfaceUtils.setBlock(x - out, self._first_floor_level + 1, z1 + 2 + i, 'air')
                        self._build_map.setBuildAt(x - 3, z1 + 3, 3)

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
            
            # add stone doorstep and updating build map
            for out in range(1, 3):
                for i in range(3):
                    if(self._direction == 'W'):
                        interfaceUtils.setBlock(x1 + 2 + i, self._first_floor_level, z + out, 'stone_bricks')
                        interfaceUtils.setBlock(x1 + 2 + i, self._first_floor_level + 1, z + out, 'air')
                        self._build_map.setBuildAt(x1 + 3, z + 3, 3)
                    
                    else:
                        interfaceUtils.setBlock(x1 + 2 + i, self._first_floor_level, z - out, 'stone_bricks')
                        interfaceUtils.setBlock(x1 + 2 + i, self._first_floor_level + 1, z - out, 'air')
                        self._build_map.setBuildAt(x1 + 3, z - 3, 3)

    def _decorateInterior(self):
        rand = random.rand()
        if(rand < 0.25):
            bed = 'green_bed'
        elif(rand < 0.5):
            bed = 'brown_bed'
        elif(rand < 0.75):
            bed = 'yellow_bed'
        else:
            bed = 'blue_bed'
        if(self._direction == 'N'):
            interfaceUtils.setBlock(self._houseX + 5, self._first_floor_level + 1, self._houseZ + 3, bed + '[facing=east]')
            interfaceUtils.setBlock(self._houseX + 6, self._first_floor_level + 1, self._houseZ + 3, bed + '[part=head, facing=east]')
            

        elif(self._direction == 'S'):
            interfaceUtils.setBlock(self._houseX + 2, self._first_floor_level + 1, self._houseZ + 3, bed + '[facing=west]')
            interfaceUtils.setBlock(self._houseX + 1, self._first_floor_level + 1, self._houseZ + 3, bed + '[part=head, facing=west]')
            interfaceUtils.setBlock(self._houseX + 2, self._first_floor_level + 1, self._houseZ + 1, 'chest[facing=south]')
            interfaceUtils.setBlock(self._houseX + 1, self._first_floor_level + 1, self._houseZ + 1, 'chest[facing=south]')
            interfaceUtils.setBlock(self._houseX + 5, self._first_floor_level + 1, self._houseZ + 5, 'crafting_table')
            interfaceUtils.setBlock(self._houseX + 1, self._first_floor_level + 2, self._houseZ + 3, 'wall:torch[facing=east]')
            interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 1, self._houseZ + 5, 'furnace')

        elif(self._direction == 'E'):
            interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 1, self._houseZ + 5, bed + '[facing=south]')
            interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 1, self._houseZ + 6, bed + '[part=head, facing=south]')
        else:
            interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 1, self._houseZ + 2, bed)
            interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 1, self._houseZ + 1, bed + '[part=head]')
            interfaceUtils.setBlock(self._houseX + 1, self._first_floor_level + 1, self._houseZ + 1, 'chest[facing=east]')
            interfaceUtils.setBlock(self._houseX + 1, self._first_floor_level + 1, self._houseZ + 2, 'chest[facing=east]')
            interfaceUtils.setBlock(self._houseX + 5, self._first_floor_level + 1, self._houseZ + 5, 'crafting_table')
            interfaceUtils.setBlock(self._houseX + 3, self._first_floor_level + 2, self._houseZ + 1, 'wall:torch[facing=south]')
            interfaceUtils.setBlock(self._houseX + 5, self._first_floor_level + 1, self._houseZ + 3, 'furnace[facing=west]')
            