# logo_gen.py

import os
from dotenv import load_dotenv
import requests
import random
import time
import base64

# Загружаем переменные из .env (если запускаем локально)
load_dotenv()

def get_fresh_iam_token():
    oauth_token = os.getenv("YANDEX_OAUTH_TOKEN")
    if not oauth_token:
        raise RuntimeError("Переменная YANDEX_OAUTH_TOKEN не задана в .env")

    url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
    payload = {"yandexPassportOauthToken": oauth_token}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["iamToken"]
    except Exception as e:
        raise RuntimeError(f"Не удалось получить IAM-токен: {e}")

def generate_logo(forma, style, description):
    try:
        iam_token = get_fresh_iam_token()
        catalog_id = os.getenv("YANDEX_CATALOG_ID")
        if not catalog_id:
            return "Ошибка: YANDEX_CATALOG_ID не задан в .env"

        headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json"
        }

        data = {
            "modelUri": f"art://{catalog_id}/yandex-art/latest",
            "generationOptions": {
                "seed": str(random.randint(0, 1000000)),
                "aspectRatio": {"widthRatio": "1", "heightRatio": "1"}
            },
            "messages": [{
                "weight": "1",
                "text": f"Нарисуй логотип в форме {forma} под описание: {description}, в стиле: {style}"
            }]
        }

        # URL можно оставить хардкодом — они публичные
        url_1 = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
        url_2 = "https://llm.api.cloud.yandex.net/operations"

        # ... остальной код без изменений ...
        response = requests.post(url_1, headers=headers, json=data, timeout=15)
        if response.status_code != 200:
            return f"Ошибка запроса: {response.status_code} – {response.text}"

        request_id = response.json().get("id")
        if not request_id:
            return "Не получен ID задачи"

        time.sleep(20)

        headers.pop("Content-Type", None)
        response = requests.get(f"{url_2}/{request_id}", headers=headers, timeout=15)
        if response.status_code != 200:
            return f"Ошибка ответа: {response.status_code} – {response.text}"

        result = response.json()
        if not result.get("done"):
            return "Задача ещё не завершена"

        image_base64 = result.get("response", {}).get("image")
        if not image_base64:
            return "Изображение не найдено"

        # Сохраняем
        os.makedirs("static", exist_ok=True)
        image_path = os.path.join("static", "generated_logo.jpeg")
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        return "/static/generated_logo.jpeg"

    except Exception as e:
        return f"Ошибка: {str(e)}"
