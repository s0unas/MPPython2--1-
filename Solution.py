from Traversals import bfs_path
import heapq
from collections import deque
from Simulator import Simulator
import sys


class Solution:

    def __init__(self, problem, isp, graph, info):
        self.problem = problem
        self.isp = isp
        self.graph = graph
        self.info = info

    def output_paths(self):
        """
        This method must be filled in by you. You may add other methods and subclasses as you see fit,
        but they must remain within the Solution class.
        """

        clients = self.info["list_clients"]
        payments = self.info["payments"]
        bandwidths = self.info["bandwidths"]
        alphas = self.info.get("alphas", {})

        shortpath = bfs_path(self.graph, self.isp, clients)
        # we sort clients by payment hhigh to Low
        sorted_clients = sorted(clients, key=lambda c: payments[c], reverse=True)
        
        # usage[node][time_tick] = how many packets are using this node's bandwidth
        usage = {node: {} for node in self.graph}
        final_paths = {}

        for client_id in sorted_clients:
            if client_id in shortpath:
                shortestdist = len(shortpath[client_id]) - 1
            else:
                shortestdist = 100

            clientalpha = alphas.get(client_id, 1.0)    
            deadline = clientalpha * shortestdist

            path = self.find_path(client_id, usage, bandwidths, deadline)
            
            # 2. Update our internal traffic map
            if path:
                final_paths[client_id] = path
                # Update usage tracker for each hop in the chosen path
                for t, node in enumerate(path):
                    if t not in usage[node]:
                        usage[node][t] = 1
                    else:
                        usage[node][t] += 1
            else:
                # Fallback to shortest path if no smart path is found within deadline
                if client_id in shortpath:
                    final_paths[client_id] = shortpath[client_id]
                else:
                    final_paths[client_id] = []

        return (final_paths, {}, {})


    def find_path(self, goal, usage, bandwidths, deadline):
        # pq stores (total_delay, current_time, current_node, path_list)
        pq = [(0, 0, self.isp, [self.isp])]
        visited = {} # in here should be (node, time)

        while pq:
            delay, time, u, path = heapq.heappop(pq)

            if u == goal:
                return path

            # check visited
            if u in visited:
                if visited[u] <= delay:
                    continue
            visited[u] = delay

            if delay > deadline:
                continue

            for v in self.graph[u]:
                #Calculate simulator queuing based on current traffic at time 'time'
                if time in usage[u]:
                    current_load = usage[u][time]
                else:
                    current_load = 0
                
                
                # Each 'bandwidth' chunk of packets adds 1 tick of delay
                queuing_delay = int(current_load // bandwidths[u])
                
                new_delay = delay + 1 + queuing_delay
                arrival_time_at_v = time + 1 + queuing_delay
                
                # Only explore the neighbor if we stay within the deadline
                if new_delay <= deadline:
                    heapq.heappush(pq, (new_delay, arrival_time_at_v, v, path + [v]))

        return []