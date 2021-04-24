import numpy as np
import buildUtils
import queue

def _buildPath(node, path, build_map, builder):
    for move in path:
        if move == "U":
            node[0] += 1
        elif move == "D":
            node[0] -= 1
        elif move == "L":
            node[1] -= 1
        elif move == "R":
            node[1] += 1
        
        build_map.area_map[node[0]][node[1]] = 2
        builder.setBlockAt(
            builder._x + node[0],
            -1,
            builder._z + node[1],
            "grass_path"
        )
        for i in range(10):
            builder.setBlockAt(
                builder._x + node[0],
                i,
                builder._z + node[1],
                "air"
            )
        
def _pathfind(start, build_map):
    fringe = []
    explored = []    
    fringe.append(["", start[0], start[1]])
    explored.append([start[0], start[1]])
    while len(fringe) > 0:
        cur = fringe.pop(0)
        cur_x = cur[1]
        cur_z = cur[2]
        if isGoal(cur_x, cur_z, build_map):
            return cur[0]
        else:
            for move in ["U", "D", "L", "R"]:
                new_x, new_z = playMove(move, cur_x, cur_z)
                if not(isOOB(new_x, new_z, build_map)):
                    if not([new_x, new_z] in explored):
                        if isPermitted(new_x, new_z, build_map):
                            fringe.append([cur[0]+move, new_x, new_z])
                            explored.append([new_x, new_z])

def playMove(move, x, z):
    if move == "U":
        return x + 1, z
    if move == "D":
        return x - 1, z
    if move == "R":
        return x, z + 1
    if move == "L":
        return x, z - 1

def isOOB(x, z, build_map):
    return x < 0 or z < 0 or x > build_map.size-1 or z > build_map.size-1

def isPermitted(x , z, build_map):
    return build_map.area_map[x][z] != 1

def isGoal(x , z, build_map):
    return build_map.area_map[x][z] == 2
    
def createPaths(build_map, builder):
    start_nodes = np.argwhere(build_map.area_map > 2)
    for node in start_nodes:
        path = _pathfind(node, build_map)
        _buildPath(node, path, build_map, builder)