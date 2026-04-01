from Traversals import bfs_path
import heapq
from collections import deque
from Simulator import Simulator
import sys
import heapq

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

        # we sort clients by payment hhigh to Low
        sorted_clients = sorted(clients, key=lambda c: payments[c], reverse=True)
        
        # usage[node][time_tick] = how many packets are using this node's bandwidth
        usage = {node: {} for node in self.graph}
        final_paths = {}

        for client_id in sorted_clients:
            path = self.find_path(client_id, usage, bandwidths)
            final_paths[client_id] = path
            
            # 2. Update our internal traffic map
            if path:
                for t, node in enumerate(path):
                    # In the simulator, the node at path[t] forwards the packet at time t
                    usage[node][t] = usage[node].get(t, 0) + 1
            else:
                final_paths[client_id] = []

        # Return format required by Driver.py
        return (final_paths, {}, {})


        paths, bandwidths, priorities = {}, {}, {}
        # Note: You do not need to modify all of the above. For Problem 1, only the paths variable needs to be modified. If you do modify a variable you are not supposed to, you might notice different revenues outputted by the Driver locally since the autograder will ignore the variables not relevant for the problem.
        # WARNING: DO NOT MODIFY THE LINE BELOW, OR BAD THINGS WILL HAPPEN
        return (paths, bandwidths, priorities)

    def find_path(self, goal, usage, bandwidths):
        # pq stores (total_delay, current_time, current_node, path_list)
        pq = [(0, 0, self.isp, [self.isp])]
        visited = {} # in here should be (node, time)

        while pq:
            delay, time, u, path = heapq.heappop(pq)

            if u == goal:
                return path

            # check visited
            if (u, time) in visited and visited[(u, time)] <= delay:
                continue
            visited[(u, time)] = delay

            for v in self.graph[u]:
                # How many packets are already at node 'u' at time 'time'?
                # If we exceed bandwidth, the simulator makes us wait.
                current_load = usage[u].get(time, 0)
                
                # Calculate expected delay at this node
                # If bandwidth is 2 and we are the 5th packet, we wait 2 extra ticks
                queuing_delay = current_load // bandwidths[u]
                arrival_time_at_v = time + 1 + queuing_delay
                
                # Total delay experienced by the packet
                total_delay = delay + 1 + queuing_delay

                heapq.heappush(pq, (total_delay, arrival_time_at_v, v, path + [v]))

        return []