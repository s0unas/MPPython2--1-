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
        clients = self.info["list_clients"]
        payments = self.info["payments"]
        
        #we ruun bfs to get the shortest path for everyone at once
        shortestpath = bfs_path(self.graph, self.isp, clients)
        
        #I then sorted the clients by highest payments.
        sortedclients = sorted(clients, key=lambda c: payments[c], reverse=True)
        
        final_paths = {}
        for client_id in sortedclients:
            if client_id in shortestpath:
                final_paths[client_id] = shortestpath[client_id]
            else:
                final_paths[client_id] = []

        return (final_paths, {}, {})