from collections import deque, defaultdict
import sys, time

def build_central_graph(structure):
    """
    structure: {
        root_user: {
            friend_id: [foaf1, foaf2, ...],
            ...
        },
        ...
    }
    → возвращает обычный неориентированный граф в виде {node: [neighbors...]}
    """
    graph = defaultdict(set)

    for root, friends_dict in structure.items():
        # корень тоже вершина
        graph[root]  # просто чтобы создать

        for friend, foaf_list in friends_dict.items():
            # связь root ↔ friend
            graph[root].add(friend)
            graph[friend].add(root)

            # связь friend ↔ каждый его друг (2-й уровень)
            for foaf in foaf_list:
                graph[friend].add(foaf)
                graph[foaf].add(friend)

        # ДОПОЛНИТЕЛЬНО: связи между друзьями одного root,
        # если один встречается в списке друзей другого
        friends_list = list(friends_dict.keys())
        for i in range(len(friends_list)):
            f1 = friends_list[i]
            foaf1 = set(friends_dict[f1])
            for j in range(i + 1, len(friends_list)):
                f2 = friends_list[j]
                # если f2 упомянут как друг у f1 — соединим
                if f2 in foaf1:
                    graph[f1].add(f2)
                    graph[f2].add(f1)

        # ЕЩЁ ОДИН ДОП. ШАГ (можно убрать, если не нужно):
        # свяжем всех "вторых" друзей внутри одного друга 1-го уровня.
        # то есть если у friend есть [10, 11, 12], то соединим 10-11, 10-12, 11-12
        for friend, foaf_list in friends_dict.items():
            foaf_list = list(foaf_list)
            for i in range(len(foaf_list)):
                for j in range(i + 1, len(foaf_list)):
                    a = foaf_list[i]
                    b = foaf_list[j]
                    graph[a].add(b)
                    graph[b].add(a)

    # вернём в том же формате, как у тебя в конце было
    return {node: list(neighs) for node, neighs in graph.items()}



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
    """
    Вычисляет посредническую центральность (алгоритм Брандеса)
    с отображением прогресса в консоли.
    Возвращает словарь {вершина: значение}.
    """
    start_time = time.time()
    centrality = {v: 0.0 for v in graph}
    nodes = list(graph.keys())
    total = len(nodes)

    for idx, s in enumerate(nodes, 1):
        stack = []
        pred = {w: [] for w in graph}
        sigma = {w: 0.0 for w in graph}
        dist = {w: -1 for w in graph}

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

        delta = {w: 0.0 for w in graph}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                centrality[w] += delta[w]

        # --- прогресс ---
        if idx % 10 == 0 or idx == total:
            elapsed = time.time() - start_time
            percent = idx * 100 // total
            sys.stdout.write(f"\r▶ Расчёт посредничества: {idx}/{total} ({percent}%) — прошло {elapsed:.1f} сек")
            sys.stdout.flush()

    print()  # чтобы не залипла строка прогресса
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
