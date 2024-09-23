from flask import Flask, request, jsonify
from zadarma import api

app = Flask(__name__)
api_key = '3cc11c71f64e67825f44'
api_secret = '6058e62a617695dc0f25'
z_api = api.ZadarmaAPI(key=api_key, secret=api_secret)


@app.route('/webhook', methods=['POST'])
def get_webhook():
    res = ''
    if request.method == 'POST':
        data = request.json

        phone_number = data['lead']['customer']['phone_number']

        from_number = '14693939998'
        to_number = f"1{phone_number}"

        try:
            response = z_api.call('/v1/request/callback/', {
                'from': from_number,
                'to': to_number,
            })
            res = response

        except Exception as e:
            print(f'Error: {e}')

        return res, 200


if __name__ == '__main__':
    app.run(debug=True)
