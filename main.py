from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CAFE_ID = '81809'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiMjE1MzJlYmUxYTYwMzIyMDhiYTU3NjE0MWE3MTAxODYxYzVlOWRkZWZlMWVlYTZiN2RlZGY1ODFiYzUwMTZkZWYxNjVjMTI4OGRhMmQ0YWEiLCJpYXQiOjE3NTI4NzM0NTIuOTk0MDQzLCJuYmYiOjE3NTI4NzM0NTIuOTk0MDQ1LCJleHAiOjE3ODQ0MDk0NTIuOTkxOTI4LCJzdWIiOiIzODQxMTk0MjgzODE4MDkiLCJzY29wZXMiOltdfQ.oYCtcn89euTbVpY4fUYZmaeEGv5URLzlieJlDcEU27krCZabd2uVsCTzRaG-z6i0jfzf8Wnq89CT4oBht6ROpM-AEr5r3M4PnJqm5gculN6XFxXBOBs3K4kijtS8kO26im77F778ROXd9XJ_KTU_dlhKmGjYhK9c8a0SzIG2pbIebQz7pyGAYTbQyg6PPmC6WoD2CPRbd-lvPyDsQ45rGgfu99sXrxHefXDacd-Nb0dRhwiDfv0WAPkPEA8wvn9JSRTFYneGLw7yFvoE-l207Aw-aLHguM3l-Q-VU6ohRFC4wGFk230m5-Hwj-RGNhs9Tjz02AJjkFjnNX6__bpwkQkDhWI9H0J5yngNfIP8-lRtG3jhk7y4c4MS3FH4t1SEVfC4LxWhrFnQ_sxgDBzCQmIkB5svkoVep7Xz9jjlMwkjyY1WGTk1mFG6HLYgOm_0Oltni7iXGUclIDqeeT0RewEN7w8u8O0GDowcN-BOmrSW_ugiGpSmfmnSQdYtjk4fOD2vpgTMfAbWWo_7tZGK74AVobUEbwDPrX1-8dcWmpEWaXo7W--BZjciCqr7qVpC0rH2Z25i85NypvmNza3L7lUknvDnYPQrla6aJ01uRa2wfyyn1oV_kkbB7u-Qx7pjuuCrODTri3JpG09JwWeyOADpOwVpx7rF4N-z1UGNJlo'
BASE_URL = f'https://api.icafecloud.com/api/v2/cafe/{CAFE_ID}'


@app.route('/getuser', methods=['POST'])
def get_user():
    data = request.get_json()
    ip = data.get('ip')
    url = f'{BASE_URL}/base/query'

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.ok:
        json_data = response.json()
        pc_list = json_data.get('data', {}).get('pcs_init', {}).get('pc_list', [])

        for pc in pc_list:
            if pc.get('pc_ip') == ip:
                user_name = pc.get('member_account')
                user_id = pc.get('member_id')

                return jsonify({
                    'username': user_name,
                    'user_id': user_id
                })

    return None


@app.route('/topup', methods=['POST'])
def topup():
    data = request.get_json()
    user_id = data.get('user_id')
    coins = data.get('coins')
    kills = data.get('kills')
    deaths = data.get('deaths')
    assists = data.get('assists')

    url = f'{BASE_URL}/members/action/topup'
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    body = {
        'topup_ids': str(user_id),
        'topup_value': 0,
        'add_coin': coins,
        'comment': f'wincoin cs2({kills} kills, {deaths} deaths, {assists} assists)'
    }

    response = requests.post(url, headers=headers, json=body)
    if response.ok:
        json_data = response.json()
        # return jsonify({
        #     "login": user_name,
        #     "coins": coins
        # })
        return json_data
    return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
