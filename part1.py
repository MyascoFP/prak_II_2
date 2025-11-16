import requests
import time
import logins
from visualize import visualize_graph
from part2 import betweenness_centrality, closeness_centrality, eigenvector_centrality, build_central_graph


#Получение списка друзей пользователя
def get_friends(user_id):
    url = "https://api.vk.com/method/friends.get"
    params = {
        "user_id": user_id,
        "access_token": logins.ACCESS_TOKEN,
        "v": "5.199"
    }
    response = requests.get(url, params=params).json()
    if "response" in response:
        return response["response"]["items"]
    else:
        print(f"Ошибка для user_id={user_id}: {response.get('error', {}).get('error_msg')}")
        return []


#Постоение словаря друзей с глубиной 2
def build_friends_structure(user_ids, limit_per_user=30):
    friends_structure = {}

    for user_id in user_ids:
        print(f"\n🔹 Обрабатываю пользователя {user_id}")
        friends = get_friends(user_id)
        friends_structure[user_id] = {}

        for friend_id in friends[:limit_per_user]:
            time.sleep(0.4)
            friends_of_friend = get_friends(friend_id)
            friends_structure[user_id][friend_id] = friends_of_friend
            print(f"Добавлены друзья для {friend_id}: {len(friends_of_friend)}")

    return friends_structure


def build_full_graph(friends_structure):
    """
    friends_structure: {main_user: {friend: [friends_of_friend]}}
    -> возвращает граф вида {node: set(neighbors)}
    """
    graph = {}

    for main_user, friends_dict in friends_structure.items():
        # убедимся, что вершина есть
        graph.setdefault(main_user, set())

        # 1. связь главный -> друг
        for friend, foaf_list in friends_dict.items():
            graph.setdefault(friend, set())
            graph[main_user].add(friend)
            graph[friend].add(main_user)

            # 2. связь друг -> его друзья (2-й уровень)
            for foaf in foaf_list:
                graph.setdefault(foaf, set())
                graph[friend].add(foaf)
                graph[foaf].add(friend)

        # 3. связи между друзьями 1-го уровня,
        #    если один из них встречается в списке друзей другого
        friends_list = list(friends_dict.keys())
        for i in range(len(friends_list)):
            f1 = friends_list[i]
            foaf1 = set(friends_dict[f1])
            for j in range(i + 1, len(friends_list)):
                f2 = friends_list[j]
                # если f2 есть среди друзей f1 — свяжем их
                if f2 in foaf1:
                    graph[f1].add(f2)
                    graph[f2].add(f1)

        # 4. связи между друзьями 2-го уровня внутри ОДНОГО друга 1-го уровня
        #    т.е. если у friend есть [a, b, c], то a-b, a-c, b-c
        for friend, foaf_list in friends_dict.items():
            foaf_list = list(foaf_list)
            for i in range(len(foaf_list)):
                for j in range(i + 1, len(foaf_list)):
                    a = foaf_list[i]
                    b = foaf_list[j]
                    graph.setdefault(a, set())
                    graph.setdefault(b, set())
                    graph[a].add(b)
                    graph[b].add(a)

    return graph


def main():
    USER_IDS = logins.USER_ID  # у тебя тут, судя по коду, один id

    friends_structure = build_friends_structure(USER_IDS, limit_per_user=30)

    print("\n✅ Сбор данных завершён.")

    # если твой visualize_graph умеет работать со старым форматом — ок
    visualize_graph(friends_structure, limit=300)

    # строим настоящий граф
    full_graph = build_full_graph(friends_structure)
    print("Размер графа:", len(full_graph))

    print("\n▶ Начинаю расчёт центральностей...")
    bc = betweenness_centrality(full_graph)
    cc = closeness_centrality(full_graph)
    ec = eigenvector_centrality(full_graph)

    print("\n📊 Результаты:")
    print("Посредничество:", bc)
    print("Близость:", cc)
    print("Собств. вектор:", ec)



if __name__ == "__main__":
    main()
