import time
import mapUtils
import buildUtils
import generation
import structures
import interfaceUtils
import random
from worldLoader import WorldSlice

######################## GLOBAL VARIABLES ########################

AREA            = buildUtils.BuildArea(buildUtils.getBuildArea())
MAP_SIZE        = AREA.size
WORLD_SLICE     = WorldSlice(AREA.get())
HEIGHT_MAP      = mapUtils.calcGoodHeightmap(WORLD_SLICE)
USE_BATCHING    = True
BUILD_MAP       = buildUtils.BuildMap(MAP_SIZE, (AREA.x, AREA.z))
BUILDER         = buildUtils.Builder(HEIGHT_MAP, AREA.get(), USE_BATCHING)

##################################################################
##################### PLOT FENCE GENERATION  #####################
##################################################################

perimeter_area  = (AREA.x-1, AREA.z-1, AREA.size + 2, AREA.size + 2)
perimeter_h_map = mapUtils.calcGoodHeightmap(WorldSlice(perimeter_area))

area_builder = buildUtils.Builder(perimeter_h_map, perimeter_area, USE_BATCHING)
area_builder.generatePlotFence()

##################################################################
########################## TERRAFORMING ##########################
##################################################################

area_builder.flattenArea()

# Set heightmap of the updated terrain

# Set blockmap of the terrain for the builder once the terraforming is done
start_timer = time.process_time()
print("Starting Block Map Processing")
BUILDER.generateBlockMap()
print(time.process_time() - start_timer)
print("Done Block Map Processing")

##################################################################
########################## TOWN SQUARE ###########################
##################################################################

start_timer = time.process_time()
print("Starting town square generation")
town_square_size = 25
town_square_pool_size = 13
town_square_f_map = generation.getFitnessMap(BUILD_MAP, town_square_size, 0.2, BUILDER, structures.townCentreFitness)
town_centre_plots = generation.get_indices_of_k_smallest(town_square_f_map, town_square_pool_size)
town_centre = structures.Structure(town_centre_plots[random.randint(0, town_square_pool_size-1)], town_square_size, "N")
town_centre.build(BUILDER)
print(time.process_time() - start_timer)
print("Ending town square generation")

##################################################################
######################## HOUSING #################################
##################################################################

start_timer = time.process_time()
print("Starting housing generation")

house_plot_size = 13
housing_pool_size = 13
housing_f_map = generation.getFitnessMap(BUILD_MAP, house_plot_size, 1.2, BUILDER, structures.housingFitness)
housing_plots = generation.get_indices_of_k_smallest(housing_f_map, housing_pool_size)
house = structures.House(housing_plots[0], house_plot_size, "N", BUILDER)
house = structures.House(housing_plots[1], house_plot_size, "N", BUILDER)
house = structures.House(housing_plots[2], house_plot_size, "N", BUILDER)
house = structures.House(housing_plots[3], house_plot_size, "N", BUILDER)
house = structures.House(housing_plots[4], house_plot_size, "N", BUILDER)
print(time.process_time() - start_timer)

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
