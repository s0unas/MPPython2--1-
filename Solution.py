from Traversals import bfs_path
import heapq
from collections import deque, defaultdict, Counter
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

        #instead of us running a single BFS from the ISP, we run a seperate bfs, precomputed
        # from every single imm neighbor of the isp. we save it in a dic so now we have the paths already. we dont calc for each client
        neighbormap = {}
        for n in isp_neighbors:
            neighbormap[n] = bfs_path(self.graph, n, clients)

        # we need to sort the impatient clients to the top of the list, so if a <= 1.0 they are impatient and we give them
        #a 1m multiplier so they are automaticly at the top of list. if they are patient so a > 1,
        # we divive their payment by a.
        def get_priority(c):
            a = alphas.get(c, 1.0)
            if a <= 1.0:
                return (payments[c] * 1000000)
            else:
                return (payments[c] / a)
        
        sorted_clients = sorted(clients, key=get_priority, reverse=True)

        
        #reservation[node (router id)][time] = load (time is the tick 1,2,3....)
        # we create a timebased grip to see when a router is free. a router might be full at tick 1 but at tick 2 its empty
        # by tracking usage per sec we know if Client A is using Node 9 at Time 1, Client B should either wait 
        #or find a different neighbor to avoid a collision.
        # i used a nested dict to avoid checking everyime if a node exits or not.
        reservation = collections.defaultdict(lambda: collections.defaultdict(int))
        final_paths = {}

        # we go through each client and check which will be the fastest path, we need to set a standard (infinity)
        # any pth that will beat the bestarrival time that becomes the new best path.     
        for client_id in sorted_clients:
            bestpath = None
            bestarrivaltime = float('inf')
            
            #we check every neighbor's map to find the FASTEST arrival
            for n in isp_neighbors:
                if client_id not in neighbormap[n] or not neighbormap[n][client_id]:
                    continue
                
                potential_path = [self.isp] + neighbormap[n][client_id]
                
                # Calculate what the ACTUAL delay will be in the simulator
                # based on current reservations
                #we have to implement a queue sim, - check reserv grid for current node at simtime
                # - if the router is full of highprio packets, so > bandwiths[u] we have to wait for the next
                # - when we find a router that is not full, we step forw, +1 to sim and we get the next node.
                simtime = 0
                for i in range(len(potential_path) - 1):
                    u = potential_path[i]
                    #If this node isfull at this time, we wait 
                    while reservation[u][simtime] >= bandwidths[u]:
                        simtime += 1
                    simtime += 1
                
                if simtime < bestarrivaltime:
                    bestarrivaltime = simtime
                    bestpath = potential_path

            # we need to then finally chose the best path for each client.
            if bestpath:
                final_paths[client_id] = bestpath
                # thenreserve the slots so the next client knows we're in the way
                t = 0
                for i in range(len(bestpath) - 1):
                    u = bestpath[i]
                    while reservation[u][t] >= bandwidths[u]:
                        t += 1
                    reservation[u][t] += 1
                    t += 1
            else:
                final_paths[client_id] = bfs_path(self.graph, self.isp, [client_id])[client_id]

        return (final_paths, {}, {})
    