from Traversals import bfs_path, dijkalgo
import heapq
from collections import deque, defaultdict, Counter
from Simulator import Simulator
from Revenue import Revenue
import sys
import collections

class Solution:
    def __init__(self, problem, isp, graph, info):
        self.problem = problem
        self.isp = isp
        self.graph = graph
        self.info = info

    def output_paths(self):
        clients = self.info["list_clients"]
        payments = self.info["payments"]
        alphas = self.info.get("alphas", {})
        bandwidths = self.info["bandwidths"]
        isp_neighbors = self.graph[self.isp]

        # 1. PRE-CALCULATE BFS from every ISP neighbor
        neighbor_maps = {}
        for n in isp_neighbors:
            neighbor_maps[n] = bfs_path(self.graph, n, clients)

        # 2. Urgency Sort (Prioritizing the 'impatient' high-payers)
        def get_priority(c):
            a = alphas.get(c, 1.0)
            return (payments[c] * 1000000) if a <= 1.0 else (payments[c] / a)
        
        sorted_clients = sorted(clients, key=get_priority, reverse=True)

        # 3. Smart Load Balancing
        # reservation[node][time] = load
        reservation = collections.defaultdict(lambda: collections.defaultdict(int))
        final_paths = {}

        for client_id in sorted_clients:
            best_path = None
            best_arrival_time = float('inf')
            
            # 4. Check every neighbor's map to find the FASTEST arrival
            for n in isp_neighbors:
                if client_id not in neighbor_maps[n] or not neighbor_maps[n][client_id]:
                    continue
                
                # Potential path: [ISP, Neighbor, ... Path to Client]
                potential_path = [self.isp] + neighbor_maps[n][client_id]
                
                # Calculate what the ACTUAL delay will be in the simulator
                # based on current reservations
                simulated_time = 0
                for i in range(len(potential_path) - 1):
                    u = potential_path[i]
                    # If this node is 'full' at this time, we wait (simulator logic)
                    while reservation[u][simulated_time] >= bandwidths[u]:
                        simulated_time += 1
                    simulated_time += 1
                
                # We want the path that gets us there the EARLIEST
                if simulated_time < best_arrival_time:
                    best_arrival_time = simulated_time
                    best_path = potential_path

            # 5. Lock in the best path and reserve the slots
            if best_path:
                final_paths[client_id] = best_path
                # Reserve the slots so the next client knows we're in the way
                t = 0
                for i in range(len(best_path) - 1):
                    u = best_path[i]
                    while reservation[u][t] >= bandwidths[u]:
                        t += 1
                    reservation[u][t] += 1
                    t += 1
            else:
                final_paths[client_id] = bfs_path(self.graph, self.isp, [client_id])[client_id]

        return (final_paths, {}, {})
    