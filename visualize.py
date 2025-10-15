import networkx as nx
import matplotlib.pyplot as plt


def visualize_graph(structure, limit=None):
    """
    Визуализирует структуру друзей VK в виде радиального графа (из центра).
    Поддерживает несколько центральных пользователей.
    
    :param structure: dict — {user_id: {friend_id: [friends_of_friend_ids]}}
    :param limit: int — ограничение числа узлов (для читаемости)
    """

    G = nx.Graph()

    # --- Формируем связи для всех пользователей ---
    for main_user, friends_dict in structure.items():
        G.add_node(main_user)
        for friend, friends_of_friend in friends_dict.items():
            G.add_edge(main_user, friend)
            for ff in friends_of_friend:
                G.add_edge(friend, ff)

    # --- Ограничиваем количество вершин (если нужно) ---
    if limit:
        nodes = list(G.nodes)[:limit]
        G = G.subgraph(nodes)

    # --- Определяем уровни (кольца) ---
    main_users = list(structure.keys())  # центральные пользователи
    first_level = []
    second_level = []

    for user_id, friends_dict in structure.items():
        first_level.extend(list(friends_dict.keys()))
        for friend_id in friends_dict.values():
            second_level.extend(friend_id)

    # --- Удаляем дубликаты ---
    first_level = list(set(first_level) - set(main_users))
    second_level = list(set(second_level) - set(main_users) - set(first_level))

    # --- Определяем круги для shell_layout ---
    shells = [main_users, first_level, second_level]

    # --- Радиальное расположение (shell_layout, а не kamada_kawai) ---
    pos = nx.shell_layout(G, nlist=shells)

    # --- Цвета и размеры ---
    colors, sizes = [], []
    for node in G.nodes():
        if node in main_users:
            colors.append("red")        # центральные пользователи
            sizes.append(600)
        elif node in first_level:
            colors.append("skyblue")    # друзья
            sizes.append(250)
        else:
            colors.append("lightgray")  # друзья друзей
            sizes.append(80)

    # --- Отрисовка ---
    plt.figure(figsize=(14, 12))
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=sizes, alpha=0.9, linewidths=1.5)
    nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color="gray", width=0.5)
    nx.draw_networkx_labels(G, pos, font_size=8)

    plt.title("Радиальный граф друзей и друзей друзей VK (несколько пользователей)", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

