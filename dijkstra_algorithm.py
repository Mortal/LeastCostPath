# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LeastCostPath
                                 A QGIS plugin
 Find the least cost path with given cost raster and points
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-12-12
        copyright            : (C) 2018 by FlowMap Group@SESS.PKU
        email                : xurigong@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'FlowMap Group@SESS.PKU'
__date__ = '2018-12-12'
__copyright__ = '(C) 2018 by FlowMap Group@SESS.PKU'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from math import sqrt
from heapq import heappush, heappop
import collections

sqrt2 = sqrt(2)


def dijkstra(start_tuple, end_tuples, block, find_nearest, feedback=None):

    block_h = len(block)
    block_w = len(block[0])

    flags = [[0 for _ in line] for line in block]
    IS_END = 1
    IS_VISITED = 2

    end_dict = {}
    for end_tuple in end_tuples:
        end_dict.setdefault(end_tuple[0], []).append(end_tuple)
    end_row_col_list = list(end_dict.keys())
    for (end_x, end_y), *_ in end_tuples:
        flags[end_x][end_y] |= IS_END
    start_x, start_y = start_tuple[0]

    frontier = [(0.0, start_x, start_y)]
    came_from = [[None for _ in row] for row in block]
    cost_so_far = [[None for _ in row] for row in block]

    if not (0 <= start_x < block_h and 0 <= start_y < block_w and block[start_x][start_y] is not None):
        return []

    # init progress
    index = 0
    distance_dic = {
        (x2, y2): abs(start_x - x2) + abs(start_y - y2)
        for x2, y2 in end_row_col_list
    }
    if find_nearest:
        total_manhattan = min(distance_dic.values())
    else:
        total_manhattan = sum(distance_dic.values())

    total_manhattan = total_manhattan + 1
    bound = total_manhattan
    if feedback:
        feedback.setProgress(1 + 100 * (1 - bound / total_manhattan))

    came_from[start_x][start_y] = None
    cost_so_far[start_x][start_y] = 0.0

    update_every = len(block) * len(block[0]) // 10000
    next_update = update_every

    result = []
    ends_found = 0

    while frontier:
        its += 1
        _, cx, cy = heappop(frontier)
        if flags[cx][cy] & IS_VISITED:
            continue
        flags[cx][cy] |= IS_VISITED

        # update the progress bar
        next_update -= 1
        if feedback and next_update == 0:
            next_update = update_every
            if feedback.isCanceled():
                return None

            index = (index + 1) % len(end_row_col_list)
            target_node = end_row_col_list[index]
            new_manhattan = abs(cx - target_node[0]) + abs(cy - target_node[1])
            if new_manhattan < distance_dic[target_node]:
                if find_nearest:
                    curr_bound = new_manhattan
                else:
                    curr_bound = bound - (distance_dic[target_node] - new_manhattan)

                distance_dic[target_node] = new_manhattan

                if curr_bound < bound:
                    bound = curr_bound
                    if feedback:
                        feedback.setProgress(1 + 100 * (1 - bound / total_manhattan)*(1 - bound / total_manhattan))

        # reacn destination
        if flags[cx][cy] & IS_END:
            path = []
            costs = []
            traverse_node = (cx, cy)
            while traverse_node is not None:
                path.append(traverse_node)
                costs.append(cost_so_far[traverse_node[0]][traverse_node[1]])
                traverse_node = came_from[traverse_node[0]][traverse_node[1]]
            
            # start point and end point overlaps
            if len(path) == 1:
                path.append((start_x, start_y))
                costs.append(0.0)
            path.reverse()
            costs.reverse()
            result.append((path, costs, end_dict[cx, cy]))

            ends_found += 1
            if len(end_row_col_list) == ends_found or find_nearest:
                break

        # relax distance
        currV = block[cx][cy]

        # Test all 8 neighbors
        for nx, ny in [(cx + 1, cy), (cx, cy - 1), (cx - 1, cy), (cx, cy + 1),
                       (cx + 1, cy - 1), (cx + 1, cy + 1), (cx - 1, cy - 1), (cx - 1, cy + 1)]:
            if not (0 <= nx < block_h and 0 <= ny < block_w):
                # neighbor outside grid
                continue
            offsetV = block[nx][ny]
            if offsetV is None:
                # nodata neighbor
                continue

            # Cost evaluation
            if cx == nx or cy == ny:
                new_cost = cost_so_far[cx][cy] + (currV + offsetV) / 2
            else:
                new_cost = cost_so_far[cx][cy] + sqrt2 * (currV + offsetV) / 2

            if cost_so_far[nx][ny] is None or new_cost < cost_so_far[nx][ny]:
                cost_so_far[nx][ny] = new_cost
                heappush(frontier, (new_cost, nx, ny))
                came_from[nx][ny] = (cx, cy)

    return result
