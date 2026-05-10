import requests
import time
import json
import os

VK_TOKEN = "vk1.a.bkiAlUXAg3HGfxajEFUDzofLAdiNM6U9ITDbhBFAdjHSMP1oKXLFs7wDbZCnOZKxXULKgvoI50eOUm_6CrK7TN5A6P0fW0EIQeqOGJVFhXtfcWMQFlwfJ7sOGX1FKMyITjl2WCq-IaRm_Vq2pnR312GXYMEyHBDSUW1UTtknCYcKRJ0dDg95U4VI3nMc2gtT21g7qZAd8a5Q3tBD17s90w"
TG_BOT_TOKEN = "8658569719:AAFiz1x8onKgNFR9ZfRHifq2N4fFd22Dw3c"
TG_CHAT_ID = "404047781"
VK_GROUP = "blackrussiayakutsk"
CHECK_INTERVAL = 300
KEYWORDS = ["продам", "продаю", "куплю", "покупаю", "цена", "продаётся", "лот", "торг"]
LAST_POST_FILE = "last_post_id.json"

def load_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return json.load(f).get("last_id", 0)
    return 0

def save_last_post_id(post_id):
    with open(LAST_POST_FILE, "w") as f:
        json.dump({"last_id": post_id}, f)

def get_vk_posts():
    url = "https://api.vk.com/method/wall.get"
    params = {"domain": VK_GROUP, "count": 10, "access_token": VK_TOKEN, "v": "5.131"}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "response" in data:
            return data["response"]["items"]
        else:
            print(f"Ошибка VK API: {data}")
            return []
    except Exception as e:
        print(f"Ошибка: {e}")
        return []

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    params = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, params=params, timeout=10)
    except Exception as e:
        print(f"Ошибка Telegram: {e}")

def contains_keyword(text):
    return any(kw in text.lower() for kw in KEYWORDS)

def format_post(post):
    text = post.get("text", "")
    post_id = post.get("id", "")
    owner_id = abs(post.get("owner_id", 0))
    link = f"https://vk.com/{VK_GROUP}?w=wall-{owner_id}_{post_id}"
    message = f"🔔 <b>Новый пост в Black Russia Yakutsk</b>\n\n{text[:800]}"
    if len(text) > 800:
        message += "..."
    message += f"\n\n🔗 <a href='{link}'>Открыть пост</a>"
    return message

def main():
    print("✅ Монитор запущен!")
    send_telegram("✅ Монитор запущен! Буду присылать объявления о продаже.")
    last_id = load_last_post_id()
    if last_id == 0:
        posts = get_vk_posts()
        if posts:
            last_id = posts[0]["id"]
            save_last_post_id(last_id)
            print(f"Первый запуск, запомнили пост ID: {last_id}")
    while True:
        try:
            posts = get_vk_posts()
            new_posts = sorted([p for p in posts if p["id"] > last_id], key=lambda x: x["id"])
            for post in new_posts:
                if contains_keyword(post.get("text", "")):
                    send_telegram(format_post(post))
                    print(f"Отправлен пост ID: {post['id']}")
            if new_posts:
                last_id = new_posts[-1]["id"]
                save_last_post_id(last_id)
            print(f"Проверка выполнена. Жду 5 минут...")
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("Остановлено.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
