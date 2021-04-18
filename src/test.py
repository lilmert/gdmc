import numpy as np
import random as r

def get_indices_of_k_smallest(arr, k):
    idx = np.argpartition(arr.ravel(), k)
    return tuple(np.array(np.unravel_index(idx, arr.shape))[:, range(min(k, 0), max(k, 0))])
    # if you want it in a list of indices . . . 
    # return np.array(np.unravel_index(idx, arr.shape))[:, range(k)].transpose().tolist()

r = np.random.RandomState(1234)
arr = r.randint(1, 1000, 2 * 4 * 6).reshape(2, 4, 6)

indices = get_indices_of_k_smallest(arr, 4)
print(indices)
# (array([1, 0, 0, 1], dtype=int64),
#  array([3, 2, 0, 1], dtype=int64),
#  array([3, 0, 3, 3], dtype=int64))

print(arr[indices])