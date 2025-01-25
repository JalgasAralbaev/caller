import json

import requests
from flask import Flask, request, jsonify
from zadarma import api

app = Flask(__name__)
api_key = '3cc11c71f64e67825f44'
api_secret = '6058e62a617695dc0f25'
z_api = api.ZadarmaAPI(key=api_key, secret=api_secret)

TELEGRAM_BOT_TOKEN = '7612310969:AAE_7B1EoAp5ovBftV9uNboQlYI2eMN3T7Y'
CHAT_IDS = ['1128232668', '1214180501']


def send_telegram_message(message, chat_ids):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    for chat_id in chat_ids:
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Ошибка при отправке в чат {chat_id}: {response.status_code} - {response.text}")
        else:
            print(f"Сообщение успешно отправлено в чат {chat_id}")

@app.route('/', methods=['POST'])
def get_webhook():
    try:
        data = request.json  # Получаем данные из запроса
        if not data:
            return jsonify({"error": "Empty JSON received"}), 400
        
        # Форматируем данные в строку JSON
        message = json.dumps(data, indent=4, ensure_ascii=False)
        
        # Отправляем сообщение в Telegram
        send_telegram_message(message, CHAT_IDS)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return jsonify({"error": str(e)}), 500

# @app.route('/', methods=['POST'])
# def get_webhook():
#     res = ''
#     data = request.json  # Получаем данные из запроса
#     message = json.dumps(data, indent=4, ensure_ascii=False)  # Форматируем данные в JSON-строку
#     send_telegram_message(message, CHAT_IDS)  # Отправляем сообщение в Telegram
#     return 'OK', 200  # Возвращаем успешный ответ
    # if request.method == 'POST':
    #     data = request.json

    #     phone_number = data['lead']['customer']['phone_number']

    #     from_number = '14693939998'
    #     to_number = f"1{phone_number}"

    #     try:
    #         response = z_api.call('/v1/request/callback/', {
    #             'from': from_number,
    #             'to': to_number,
    #             'sip': 582947
    #         })
    #         res = response
    #         message = f"Новые данные:\n{json.dumps(data, indent=4)}"
    #         send_telegram_message(message, CHAT_IDS)

    #     except Exception as e:
    #         print(f'Error: {e}')

    #     return res, 200


if __name__ == '__main__':
    app.run(debug=True)
