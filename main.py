from flask import Flask, request, jsonify
from zadarma import api

app = Flask(__name__)
api_key = '3cc11c71f64e67825f44'
api_secret = '6058e62a617695dc0f25'
z_api = api.ZadarmaAPI(key=api_key, secret=api_secret)


@app.route('/', methods=['POST'])
def get_webhook():
    if request.method == 'POST':
        data = request.json

        phone_number = data['lead']['customer']['phone_number']
        return jsonify({
            'status': 'success',
            'phone_number': phone_number
        }), 200
    # from_number = '13239436353'
    # to_number = '14693939998'
    #
    # try:
    #     response = z_api.call('/v1/request/callback/', {
    #         'from': from_number,
    #         'to': to_number,
    #         'predicted': True
    #     })
    #
    #     print(response)
    #
    # except Exception as e:
    #     print(f'Error: {e}')


if __name__ == '__main__':
    app.run(debug=True)
