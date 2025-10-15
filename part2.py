from collections import deque

#Построение упрощенного графа
def build_central_graph(graph):
    central_nodes = list(graph.keys())
    simplified = {node: set() for node in central_nodes}

    for i, a in enumerate(central_nodes):
        friends_a = set(graph[a].keys())
        for b in central_nodes[i+1:]:
            friends_b = set(graph[b].keys())
            if friends_a & friends_b:
                simplified[a].add(b)
                simplified[b].add(a)
    return {k: list(v) for k, v in simplified.items()}


#
def bfs_distance(graph, start):
    dist = {v: float('inf') for v in graph}
    dist[start] = 0
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for w in graph[v]:
            if dist[w] == float('inf'):
                dist[w] = dist[v] + 1
                queue.append(w)
    return dist


#
def closeness_centrality(graph):
    centrality = {}
    n = len(graph)
    for v in graph:
        dist = bfs_distance(graph, v)
        total_dist = sum(d for d in dist.values() if d < float('inf') and d > 0)
        centrality[v] = (n - 1) / total_dist if total_dist > 0 else 0
    return centrality


#
def betweenness_centrality(graph):
    centrality = {v: 0 for v in graph}
    for s in graph:
        stack = []
        pred = {w: [] for w in graph}
        sigma = dict.fromkeys(graph, 0.0)
        dist = dict.fromkeys(graph, -1)
        sigma[s] = 1.0
        dist[s] = 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in graph[v]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = dict.fromkeys(graph, 0)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                centrality[w] += delta[w]
    return centrality


#
def eigenvector_centrality(graph, max_iter=100, tol=1.0e-6):
    n = len(graph)
    x = {v: 1.0 / n for v in graph}
    for _ in range(max_iter):
        x_new = {}
        norm = 0.0
        for v in graph:
            x_new[v] = sum(x[w] for w in graph[v])
            norm += x_new[v] ** 2
        norm = norm ** 0.5
        for v in graph:
            x_new[v] /= norm
        diff = sum(abs(x_new[v] - x[v]) for v in graph)
        x = x_new
        if diff < tol:
            break
    return x
