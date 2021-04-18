import mapUtils
import interfaceUtils
from worldLoader import WorldSlice

# sentence information
SENTENCE = "COMP4303"
LETTER_SIZE = 5

# x pos, z pos, x size, z size
area = (0, 0, len(SENTENCE)* (LETTER_SIZE + 2), LETTER_SIZE + 2)

# create dictionary for building each letter / number
BUILDER = {}
BUILDER["C"] = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1]
]

BUILDER["O"] = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
]

BUILDER["M"] = [
    [1, 0, 0, 0, 1],
    [1, 1, 0, 1, 1],
    [1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1]
]

BUILDER["P"] = [
    [1, 1, 1, 1, 0],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0]
]

BUILDER["4"] = [
    [2, 0, 0, 2, 0],
    [2, 0, 0, 2, 0],
    [2, 2, 2, 2, 2],
    [0, 0, 0, 2, 0],
    [0, 0, 0, 2, 0],
]

BUILDER["3"] = [
    [2, 2, 2, 2, 2],
    [0, 0, 0, 0, 2],
    [0, 2, 2, 2, 2],
    [0, 0, 0, 0, 2],
    [2, 2, 2, 2, 2]
]

BUILDER["0"] = [
    [0, 2, 2, 2, 0],
    [2, 0, 0, 0, 2],
    [2, 0, 2, 0, 2],
    [2, 0, 0, 0, 2],
    [0, 2, 2, 2, 0]
]

# block coloring
ALPHA_BLOCK = "sea_lantern"
NUM_BLOCK = "jack_o_lantern"
BACKGROUND_BLOCK = "white_wool"

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

def buildSentence():
    # create pointer for top left of letter
    ptr = [1,1]
    for letter in SENTENCE:
        char_map = BUILDER[letter]
        for z, row in enumerate(char_map):
            for x, val in enumerate(row):
                if val == 0:
                    pass 
                else:
                    y = heightAt(x + ptr[0], z + ptr[1])
                    if val == 1:
                        setBlock(x + ptr[0], y, z + ptr[1], ALPHA_BLOCK)
                    else:
                        setBlock(x + ptr[0], y, z + ptr[1], NUM_BLOCK)
        ptr[0] += 6
                        
def setBackground():
    for x in range(area[0], area[0] + area[2]):
        for z in range(area[1], area[1] + area[3]):
            y = heightAt(x, z)
            setBlock(x, y-1, z, BACKGROUND_BLOCK)
            
def buildHouse(x1, y1, z1, x2, y2, z2):
    # floor
    for x in range(x1, x2):
        for z in range(z1, z2):
            setBlock(x, y1, z, "cobblestone");
    # walls
    for y in range(y1+1, y2):
        for x in range(x1 + 1, x2 - 1):
            setBlock(x, y, z1, "oak_planks")
            setBlock(x, y, z2 - 1, "oak_planks")
        for z in range(z1 + 1, z2 - 1):
            setBlock(x1, y, z, "oak_planks")
            setBlock(x2 - 1, y, z, "oak_planks")
    # corners
    for dx in range(2):
        for dz in range(2):
            x = x1 + dx * (x2 - x1 - 1)
            z = z1 + dz * (z2 - z1 - 1)
            for y in range(y1, y2):
                setBlock(x, y, z, "oak_log");
    # clear interior
    for y in range(y1 + 1, y2):
        for x in range(x1+1, x2-1):
            for z in range(z1+1, z2-1):
                setBlock(x, y, z, "air")
    # roof
    if x2-x1 < z2-z1:
        for i in range(0, x2-x1, 2):
            halfI = int(i/2)
            for x in range(x1 + halfI, x2 - halfI):
                for z in range(z1, z2):
                    setBlock(x, y2 + halfI, z, "bricks")
    else:
        # same as above but with x and z swapped
        for i in range(0, z2-z1, 2):
            halfI = int(i/2)
            for z in range(z1 + halfI, z2 - halfI):
                for x in range(x1, x2):
                    setBlock(x, y2 + halfI, z, "bricks")

setBackground()
buildSentence()

if USE_BATCHING:
    # we need to send remaining blocks in the buffer at the end of the program, when using batching
    interfaceUtils.sendBlocks()


