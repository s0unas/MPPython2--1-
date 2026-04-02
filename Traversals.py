from collections import deque
import heapq


def bfs_path(graph, isp, list_clients):
    paths = {}

    graph_size = len(graph)
    priors = [-1]*graph_size
    search_queue = deque()
    search_queue.append(isp)
    while search_queue:
        node = search_queue.popleft()
        for neighbor in graph[node]:
            if (priors[neighbor] == -1 and neighbor != isp):
                priors[neighbor] = node
                search_queue.append(neighbor)

    for client in list_clients:
        path = []
        current_node = client
        while (current_node != -1):
            path.append(current_node)
            current_node = priors[current_node]
        path = path[::-1]
        paths[client] = path

    return paths

def dijkalgo(graph, isp, client_list, bandwidths, pn_time):
    client = client_list[0] 
    
    # pq = (cost, current_time, current_node, path)
    pq = [(0, 0, isp, [isp])]
    visited = {}

    while pq:
        cost, time, u, path = heapq.heappop(pq)

        if u == client:
            return {client: path}

        # We allow visiting the same node at DIFFERENT times
        if (u, time) in visited and visited[(u, time)] <= cost:
            continue
        visited[(u, time)] = cost

        for neighbor in graph[u]:
            band = bandwidths[neighbor]
            
            # 1. Look at the load for the SPECIFIC time we will arrive
            # This is the "Time-Step" secret
            arrival_time = time + 1
            load_at_tick = pn_time[neighbor].get(arrival_time, 0)

            # 2. Calculate the queuing delay
            # If load is 10 and band is 5, we wait 2 ticks
            queuing_delay = int(load_at_tick // band)
            
            # 3. Penalty logic: (load / band)^2
            penalty = (load_at_tick / band)**2
            
            # Cost = Total Time taken + Penalty
            new_time = arrival_time + queuing_delay
            new_cost = new_time + penalty
            
            if new_time < 40: # Stay within a reasonable path length
                heapq.heappush(pq, (new_cost, new_time, neighbor, path + [neighbor]))

    return {client: []}