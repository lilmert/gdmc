import structures
import buildUtils
import numpy as np
import math

def getFitnessMap(buildmap, plot_size, threshold, builder, fitnessFunction):
    f_map = np.full((buildmap.size - plot_size, buildmap.size - plot_size), 10000.0, dtype=np.half)
    for x in range(buildmap.origin_x, buildmap.size - plot_size, math.floor(plot_size * threshold)):
        for z in range(buildmap.origin_z, buildmap.size - plot_size, math.floor(plot_size * threshold)):
            x_idx = x - buildmap.origin_x
            z_idx = z - buildmap.origin_z
            if buildmap.plotPermit(x, z, plot_size):
                block_counts, height_counts, centrality = builder.getPlotStats(x,z,plot_size)
                f_map[x_idx][z_idx] = fitnessFunction(block_counts, height_counts, centrality)
    
    return f_map

# https://stackoverflow.com/questions/34226400/find-the-index-of-the-k-smallest-values-of-a-numpy-array
# specific answer -> finding k-smallest value indexes for n-dimensional arrays
def get_indices_of_k_smallest(arr, k):
    idx = np.argpartition(arr.ravel(), k)
    return np.array(np.unravel_index(idx, arr.shape))[:, range(k)].transpose().tolist() 
