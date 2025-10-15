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


def main():
    USER_IDS = logins.USER_ID

    friends_structure = build_friends_structure(USER_IDS, limit_per_user=30)

    print("\n✅ Сбор данных завершён.")
    visualize_graph(friends_structure, limit=300)
    
    simplified = build_central_graph(friends_structure)
    print("Упрощённый граф:", simplified)
    
    print("Посредничество:", betweenness_centrality(simplified))
    print("Близость:", closeness_centrality(simplified))
    print("Собств. вектор:", eigenvector_centrality(simplified))


if __name__ == "__main__":
    main()
