import time
import mapUtils
import buildUtils
import generation
import structures
import interfaceUtils
import random
import numpy as np
import pathfinding
import sys
from worldLoader import WorldSlice

######################## GLOBAL VARIABLES ########################

AREA            = buildUtils.BuildArea(buildUtils.getBuildArea())

if len(sys.argv) < 2:
    pass
elif len(sys.argv) == 4:
    AREA.x = int(sys.argv[1])
    AREA.z = int(sys.argv[2])
    AREA.size = int(sys.argv[3])

MAP_SIZE        = AREA.size
WORLD_SLICE     = WorldSlice(AREA.get())
HEIGHT_MAP      = mapUtils.calcGoodHeightmap(WORLD_SLICE)
USE_BATCHING    = True
BUILD_MAP       = buildUtils.BuildMap(MAP_SIZE, (AREA.x, AREA.z))
BUILDER         = buildUtils.Builder(HEIGHT_MAP, AREA.get(), USE_BATCHING)

##################################################################
########################### WORLD SETUP  #########################
##################################################################

# plot fence
perimeter_area  = (AREA.x-1, AREA.z-1, AREA.size + 2, AREA.size + 2)
perimeter_h_map = mapUtils.calcGoodHeightmap(WorldSlice(perimeter_area))
area_builder = buildUtils.Builder(perimeter_h_map, perimeter_area, USE_BATCHING)
area_builder.generatePlotFence()

# terraforming
start_timer = time.process_time()
print("Starting Terraforming")
BUILDER.flattenArea()
print("Time ", time.process_time() - start_timer)

#update globals to reflect terraforming
WORLD_SLICE     = WorldSlice(AREA.get())
HEIGHT_MAP      = mapUtils.calcGoodHeightmap(WORLD_SLICE)
BUILDER         = buildUtils.Builder(HEIGHT_MAP, AREA.get(), USE_BATCHING)

# Set blockmap of the terrain for the builder once the terraforming is done
start_timer = time.process_time()
print("Starting Block Map Processing")
BUILDER.generateBlockMap()
print("Time ", time.process_time() - start_timer)

##################################################################
########################## TOWN SQUARE ###########################
##################################################################

start_timer = time.process_time()
print("Starting town square generation")
town_square_size = 25
town_square_pool_size = 1
town_square_f_map = generation.getFitnessMap(BUILD_MAP, town_square_size, 1, BUILDER, structures.townCentreFitness)
town_centre_plots = generation.get_indices_of_k_smallest(town_square_f_map, town_square_pool_size)
town_centre = structures.TownCentre(town_centre_plots[0], town_square_size, BUILDER)
BUILD_MAP.addStructure(town_centre._x, town_centre._z, town_square_size)
print("Time ", time.process_time() - start_timer)

start_timer = time.process_time()
print("Starting Central Roadway Generation")
town_centre.buildPaths(BUILD_MAP)
print("Time ", time.process_time() - start_timer)

##################################################################
######################## HOUSING #################################
##################################################################

start_timer = time.process_time()
print("Starting housing generation")

house_plot_size = 11
housing_pool_size = 35
housing_f_map = generation.getFitnessMap(BUILD_MAP, house_plot_size, 1.2, BUILDER, structures.housingFitness)
housing_plots = generation.get_indices_of_k_smallest(housing_f_map, housing_pool_size)
i = 0
placed = 0
while placed < 10:
    if(BUILD_MAP.plotPermit(housing_plots[i][0], housing_plots[i][1], housing_pool_size)):
        BUILD_MAP.addStructure(housing_plots[i][0], housing_plots[i][1], house_plot_size)
        house = structures.House(housing_plots[i], house_plot_size, BUILDER, BUILD_MAP)
        placed += 1
    i += 1

print("Time ", time.process_time() - start_timer)

# placing block at start node of path finding (visual aid)
indices = np.argwhere(BUILD_MAP.area_map > 2)
for idx in indices:
    BUILDER.setBlockAt(idx[0], -1, idx[1], "iron_block")

start_timer = time.process_time()
print("Starting path finding for houses")
pathfinding.createPaths(BUILD_MAP, BUILDER)
print("Time ", time.process_time() - start_timer)

# Order of generation and settlement

# * 1. Terraform the land (regenerate heightmap after)
# * 2. Establish & Generate town square
# * 3. Establish & Generate cardinal roadways from the centre
# * 4. Establish & Generate Housing across the land
# * 5. Use pathfinding to connect housing to roads 
# * 6. Add any decorations we can / want

##################################################################

if USE_BATCHING:
    # we need to send remaining blocks in the buffer at the end of the program, when using batching
    interfaceUtils.sendBlocks()
