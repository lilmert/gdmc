import random
import math
import numpy as np
import mapUtils
import interfaceUtils
from worldLoader import WorldSlice

#######################################################################
###################### SETUP CODE BELOW ###############################
#######################################################################

# x position, z position, x size, z size
area = (0, 0, 256, 256) # default build area

# Do we send blocks in batches to speed up the generation process?
USE_BATCHING = True

print("Build area is at position %s, %s with size %s, %s" % area)

# load the world data
# this uses the /chunks endpoint in the background
worldSlice = WorldSlice(area)

# caclulate a heightmap that ignores trees:
heightmap = mapUtils.calcGoodHeightmap(worldSlice)

# define a function for easier heightmap access
# heightmap coordinates are not equal to world coordinates!
def heightAt(x, z):
    return heightmap[(x - area[0], z - area[1])]

# a wrapper function for setting blocks
def setBlock(x, y, z, block):
    if USE_BATCHING:
        interfaceUtils.placeBlockBatched(x, y, z, block, 100)
    else:
        interfaceUtils.setBlock(x, y, z, block)

# build a fence around the build area perimeter
for x in range(area[0], area[0] + area[2]):
    z = area[1]
    y = heightAt(x, z)
    setBlock(x, y-1, z, "cobblestone")
    setBlock(x, y,   z, "oak_fence")
for z in range(area[1], area[1] + area[3]):
    x = area[0]
    y = heightAt(x, z)
    setBlock(x, y-1, z, "cobblestone")
    setBlock(x, y  , z, "oak_fence")
for x in range(area[0], area[0] + area[2]):
    z = area[1] + area[3] - 1
    y = heightAt(x, z)
    setBlock(x, y-1, z, "cobblestone")
    setBlock(x, y,   z, "oak_fence")
for z in range(area[1], area[1] + area[3]):
    x = area[0] + area[2] - 1
    y = heightAt(x, z)
    setBlock(x, y-1, z, "cobblestone")
    setBlock(x, y  , z, "oak_fence")

#######################################################################
################## SETTLEMENT CODE BELOW ##############################
#######################################################################

SETTLEMENT_AREA_SIZE = 128

# The purpose of this code is to determine the best 128x128 settlement area for a village
def getSettlingArea(nbhd_size, build_area):        
    # number of neighbourhoods to try
    number_to_check = 4
    x_stepping_size = math.floor((build_area[2] - nbhd_size) / number_to_check)
    z_stepping_size = math.floor((build_area[3] - nbhd_size) / number_to_check)
    # create a map to store the array of maps 
    possible_nbhds = {}
    # for every slice in the map:
    for x in range(build_area[0], build_area[2] - nbhd_size, x_stepping_size): 
        for z in range(build_area[1], build_area[3] - nbhd_size, z_stepping_size):            
            # get the world slice
            area = (x, z, nbhd_size, nbhd_size)
            world_slice = WorldSlice(area)

            # get the height map
            height_map = mapUtils.calcGoodHeightmap(world_slice)

            terrain_map = {}
            height_counts = {}
            water = 0
            grass = 0
            for i in range(nbhd_size):
                for j in range(nbhd_size):
                    # calculate terrain map
                    block = world_slice.getBlockAt((i+x, height_map[i][j], j+z))
                    
                    # if blockID is not in terrainMap add it and set val to 1, else increment val
                    if block in terrain_map:
                        terrain_map[block] += 1
                    else:
                        terrain_map[block] = 1
            
                    # find highest number of blocks with the same height
                    if(height_map[i][j] in height_counts):
                        height_counts[height_map[i][j]] += 1
                    else:
                        height_counts[height_map[i][j]] = 1
            
                    # find the number of water blocks
                    if(world_slice.getBlockAt((i + x, height_map[i][j], j + z)) == "minecraft:water"):
                        water += 1
            
                    # find the number of grass blocks
                    if(world_slice.getBlockAt((i + x, height_map[i][j], j + z)) == "minecraft:grass"):
                        grass += 1 
            
            # find highest count of blocks with the same height
            common_val = 0
            for height_count in height_counts:
                if height_count > common_val:
                    common_val = height_count

            # calculate score
            score = common_val + ((nbhd_size * nbhd_size) - water) + grass
            
            # add score to nbhds
            possible_nbhds[score] = [x, z]

        # choose neighbourhood with highest score
        high_score = 0
        best_nbhd = None
        for score, nbhd in possible_nbhds.items():
            if(score > high_score):
                high_score = score
                best_nbhd = nbhd

        # print score
    print("best score: ", high_score)
    # return
    print("best neighbourhood: ", best_nbhd)


    return best_nbhd

#######################################################################
###################### BUILDING CODE BELOW ############################
#######################################################################

# Plotting Dimensions
LARGE = (16, 16)
SMALL = (10, 10)
AREA = 256 # TODO: adjust to make dynamic with buildarea

# We want housing to occupy a set percentage of the village area
#   Small = 4%
#   Large = 6%
#   --------------
#   Total = 10%

num_large = math.floor(0.06 / ((LARGE[0]*LARGE[1]) / AREA**2))
num_small = math.floor(0.04 / ((SMALL[0]*SMALL[1]) / AREA**2))

# Next, we want to scan the heightmap across the size of each of the houses
# and create a plot_map.
# plot_map
#   * a 2d array of 1/0's representing whether that structure can be built there
#       * 1 = yes
#       * 0 = no

plot_map = {
    "LARGE": np.full((AREA-LARGE[0], AREA-LARGE[1]), 10000.0, dtype=np.half),
    "SMALL": np.full((AREA-SMALL[0], AREA-SMALL[1]), 10000.0, dtype=np.half)
}


def housingFitness(origin, size):
    """Function for determining the fitness of a plot for a housing settlement.

    Args:
        origin (tuple):     a tuple of 2 integer coordinates representing the upper left of the plot
        size (int):         the length and width of the plot

    Returns:
        float: the fitness evaluation of the plot
    """
    hmap = np.zeros((size, size))
    bmap = np.empty((size, size), dtype="object")
    for i,x in enumerate(range(origin[0], origin[0]+size)):
        for j,z in enumerate(range(origin[1], origin[1]+size)):
            c_y = heightAt(x,z)
            hmap[i][j] = c_y
            bmap[i][j] = worldSlice.getBlockAt((x, c_y - 1, z))
    b_unique, b_counts = np.unique(bmap, return_counts=True)
    block_counts = dict(zip(b_unique, b_counts))
    h_unique, h_counts = np.unique(hmap, return_counts=True)
    height_counts = dict(zip(h_unique, h_counts))
    # Determining the fitness 
    #   Water increases fitness
    #   Height differential increases fitness
    if 'minecraft:water' in block_counts:
        fitness = len(height_counts) + (block_counts['minecraft:water']*3.5)
    else:
        fitness = len(height_counts)
    return fitness

# finding small housing plot areas on a set overlap
# overlap currently => 50%
for x in range(area[0],  area[2] - SMALL[0], math.floor(SMALL[0] / 2)):
    for z in range(area[1], area[3] - SMALL[1], math.floor(SMALL[1] / 2)):
        plot_map["SMALL"][x][z] = housingFitness((x,z), SMALL[0])

########### OUTLINING SETTLEMENT AREA ##############
settling_area_size = 128
best_settling_area = getSettlingArea(settling_area_size, area)

# build a fence around the settlement area
for a in range(best_settling_area[0], best_settling_area[0] + settling_area_size):
    c = best_settling_area[1]
    b = heightAt(a, c)
    setBlock(a, b - 1, c, "mossy_cobblestone")
    setBlock(a, b,   c, "minecraft:red_mushroom")
for c in range(best_settling_area[1], best_settling_area[1] + settling_area_size):
    a = best_settling_area[0]
    b = heightAt(a, c)
    setBlock(a, b-1, c, "mossy_cobblestone")
    setBlock(a, b  , c, "minecraft:red_mushroom")
for a in range(best_settling_area[0], best_settling_area[0] + settling_area_size):
    c = best_settling_area[1] + settling_area_size - 1
    b = heightAt(a, c)
    setBlock(a, b-1, c, "mossy_cobblestone")
    setBlock(a, b, c, "minecraft:red_mushroom")
for c in range(best_settling_area[1], settling_area_size):
    a = best_settling_area[0] + settling_area_size - 1
    b = heightAt(a, c)
    setBlock(a, b-1, c, "mossy_cobblestone")
    setBlock(a, b, c, "minecraft:red_mushroom")

########### END OF OUTLINING SETTLEMENT AREA ##############

# https://stackoverflow.com/questions/34226400/find-the-index-of-the-k-smallest-values-of-a-numpy-array
# specific answer -> finding k-smallest value indexes for n-dimensional arrays
def get_indices_of_k_smallest(arr, k):
    idx = np.argpartition(arr.ravel(), k)
    return np.array(np.unravel_index(idx, arr.shape))[:, range(k)].transpose().tolist()
    
# reused function from GDMC example code
# determine if plot rectangles overlap
def rectanglesOverlap(r1, r2):
    if (r1[0]>=r2[0]+r2[2]) or (r1[0]+r1[2]<=r2[0]) or (r1[1]+r1[3]<=r2[1]) or (r1[1]>=r2[1]+r2[3]):
        return False
    else:
        return True

# creating a pool of potential plots for the small house
small_pool_size = num_small * 5 # TODO: fix magic number maybe?????
small_pool = get_indices_of_k_smallest(plot_map["SMALL"], small_pool_size)
# initializing an array for the selected plots we wish to establish on
small_selected = []

# selecting the plots based on criteria
while len(small_selected) < num_small:
    rand_idx = random.randrange(small_pool_size)
    while rand_idx in small_selected:
        rand_idx = random.randrange(small_pool_size)
    
    # create the plot outline for the current selected house
    houseRect = (small_pool[rand_idx][0], small_pool[rand_idx][1], SMALL[0], SMALL[1])    
    
    # use our helper function to determine if this plot overlaps with another house
    # that we have already selected
    overlaps = False
    for house in small_selected:
        tempRect = (house[0], house[1], SMALL[0], SMALL[1])
        if rectanglesOverlap(houseRect, tempRect):
            overlaps = True
            break
    
    # if we have overlaps, start from the beginning
    # otherwise add the house to our selected region
    if overlaps:
        continue
    else:
        small_selected.append(small_pool[rand_idx])

# build the small house plots that we have selected
for sm_house in small_selected:
    y = heightAt(sm_house[0], sm_house[1])
    for i in range(SMALL[0]):
        for j in range(SMALL[1]):
            y = heightAt(sm_house[0] + i, sm_house[1] + j)
            setBlock(sm_house[0] + i, y - 1, sm_house[1] + j, "lapis_block")

if USE_BATCHING:
    # we need to send remaining blocks in the buffer at the end of the program, when using batching
    interfaceUtils.sendBlocks()
