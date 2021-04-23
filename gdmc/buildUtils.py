import numpy as np
import interfaceUtils

class Builder:
    def __init__(self, height_map, area, batching=True):
        self._height_map = height_map
        self._x = area[0]
        self._z = area[1]
        self._size = area[2]
        self._batching = batching
        self._block_map = np.empty((area[2], area[2]), dtype="object")

    def getHeightAt(self, x, z):
        x_fix = x-self._x
        z_fix = z-self._z
        if(x_fix < self._size and z_fix < self._size):
            return self._height_map[x_fix , z_fix]
        else:
            return None

    def setBlockAt(self, x, y_incr, z, block):
        y = y_incr + self.getHeightAt(x,z)
        if self._batching:
            interfaceUtils.placeBlockBatched(x, y, z, block, 100)
        else:
            interfaceUtils.setBlock(x, y, z, block)
    
    def getBlockAt(self, x, y_incr, z):
        y = y_incr + self.getHeightAt(x,z)
        return interfaceUtils.getBlock(x, y, z)

    def setHeightMap(self, new_height_map):
        if new_height_map.shape != self._height_map.shape:
            print("New Height Map Shape: ", new_height_map.shape)
            print("Old Height Map Shape: ", self._height_map.shape)
            print("Height maps are not similar in size, exiting")
            exit()
        else:
            self._height_map = new_height_map
    
    def generateBlockMap(self):
        for i in range(self._size):
            for j in range(self._size):
                self._block_map[i][j] = self.getBlockAt(self._x + i, -1, self._z + j)

    def getPlotStats(self, x, z, size):
        if self._block_map[0][0] == None:
            print("Trying to access block map without it set, exiting")
            exit()
        else:
            # centrality
            x_diff = abs((x - self._x) - ((self._size + self._x) - (x + size)))
            z_diff = abs((z - self._z) - ((self._size + self._z) - (z + size)))
            centrality = x_diff + z_diff
            # block differentials
            idx_x = x - self._x
            idx_z = z - self._z
            b_unique, b_counts = np.unique(self._block_map[idx_x:idx_x+size, idx_z:idx_z+size], return_counts=True)
            block_counts = dict(zip(b_unique, b_counts))
            # height differentials
            h_unique, h_counts = np.unique(self._height_map[idx_x:idx_x+size, idx_z:idx_z+size], return_counts=True)
            height_counts = dict(zip(h_unique, h_counts))
            return block_counts, height_counts, centrality

    def generatePlotFence(self):
        for x in range(self._x, self._x + self._size):
            z = self._z
            self.setBlockAt(x, 0, z, "cobblestone")
            self.setBlockAt(x, 1, z, "oak_fence")
        for z in range(self._z, self._z + self._size):
            x = self._x
            self.setBlockAt(x, 0, z, "cobblestone")
            self.setBlockAt(x, 1, z, "oak_fence")
        for x in range(self._x, self._x + self._size):
            z = self._z + self._size - 1
            self.setBlockAt(x, 0, z, "cobblestone")
            self.setBlockAt(x, 1, z, "oak_fence")
        for z in range(self._z, self._z + self._size):
            x = self._x + self._size - 1
            self.setBlockAt(x, 0, z, "cobblestone")
            self.setBlockAt(x, 1, z, "oak_fence")
    
    def _findEdges(self, x, z):
        hEdges = []
        if(self.getHeightAt(x, z) != self.getHeightAt(x - 1, z)):
            hEdges.append([x, z])
            if(self.getHeightAt(x, z) == self.getHeightAt(x + 1, z)):
                hEdges.append([x + 1, z])
                if(self.getHeightAt(x, z) == self.getHeightAt(x + 2, z)):
                    hEdges.append([x + 2, z])
                    if(self.getHeightAt(x, z) == self.getHeightAt(x + 3, z)):
                        hEdges = []
        vEdges = []
        if(self.getHeightAt(x, z) != self.getHeightAt(x, z - 1)):
            vEdges.append([x, z])
            if(self.getHeightAt(x, z) == self.getHeightAt(x, z + 1)):
                vEdges.append([x, z + 1])
                if(self.getHeightAt(x, z) == self.getHeightAt(x, z + 2)):
                    vEdges.append([x, z + 2])
                    if(self.getHeightAt(x, z) == self.getHeightAt(x, z + 3)):
                        vEdges = []
        return hEdges + vEdges

    def flattenArea(self):
        edgeMap = np.zeros((self._size, self._size))
        for i in range(self._x, self._x + self._size):
            for j in range(self._z, self._z + self._size):
                edges = self._findEdges(i, j)
                for edge in edges:
                    edgeMap[edge[0]][edge[1]] = 1
        for i in range(self._size):
            for j in range(self._size):
                if(edgeMap[i][j] == 1):
                    x = i + self._x
                    z = j + self._z
                    neighbour = self.getBlockAt(x, 0, z)
                    if(self.getHeightAt(x, z) < self.getHeightAt(x - 1, z)):
                        self.setBlockAt(x, 0, z, neighbour)
                    else:
                        interfaceUtils.setBlock(x, self.getHeightAt(x - 1, z), z, neighbour)


class BuildMap:
    def __init__(self, size, origin):
        self.area_map = np.zeros((size,size))
        self.size = size
        self.origin_x = origin[0]
        self.origin_z = origin[1]
    
    def getBuildAt(self, x, z):
        return self.area_map[x - self.origin_x][z - self.origin_z]
    
    def setBuildAt(self, x, z, value):
        self.area_map[x - self.origin_x][z - self.origin_z] = value
    
    def getBuildSize(self):
        return self.size
    
    def addStructure(self, x, z, size):
        for i in range(size):
            for j in range(size):
                self.setBuildAt(x+i, z+j, 1)
    
    def plotPermit(self, x, z, size):
        idx_x = x - self.origin_x
        idx_z = x - self.origin_z
        temp_plot = self.area_map[idx_x:idx_x+size, idx_z:idx_z+size]
        return not(np.any(np.in1d([1,2], temp_plot)))

class BuildArea:
    def __init__(self, buildArea):
        self.x = buildArea[0]
        self.z = buildArea[1]
        self.size = buildArea[2]
    
    def get(self):
        """Provides the build area information in a tuple format.

        Returns:
            tuple: (x, z, x size, z size)
        """
        return (self.x, self.z, self.size, self.size)

def getBuildArea(size=128):
    buildArea = interfaceUtils.requestBuildArea()
    area = (0, 0, size, size)
    if buildArea != -1:
        x1 = buildArea["xFrom"]
        z1 = buildArea["zFrom"]
        x2 = buildArea["xTo"]
        z2 = buildArea["zTo"]
        area = (x1, z1, x2-x1 + 1, z2-z1 + 1)
    return area # (x pos, z pos, x size, z size)


    
def areaOverlap(r1, r2):
    if (r1[0]>=r2[0]+r2[2]) or (r1[0]+r1[2]<=r2[0]) or (r1[1]+r1[3]<=r2[1]) or (r1[1]>=r2[1]+r2[3]):
        return False
    else:
        return True

