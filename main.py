from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CAFE_ID = '81809'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiNTliNzBiNTdhYTJkMTJmNjk5OWVkMDdlYWNkMTkzMzM3NDJkYzAwMTBlOGNlNjY3NTJhODg3Mzg2YzM3MDJiZTkzZWE1MjMzNGRjZWMyN2YiLCJpYXQiOjE3NTYwNjM2NDYuOTEwOTQxLCJuYmYiOjE3NTYwNjM2NDYuOTEwOTQ0LCJleHAiOjE3ODc1OTk2NDYuOTA4MDY1LCJzdWIiOiIzODQxMTk0MjgzODE4MDkiLCJzY29wZXMiOltdfQ.Omv6u-S6viNp7JM4a_2HTtRb3ZRWxHavpVznxqwLSznK1BUdt1BPx7H-HOF4QcrcdPkpQq-MXCmzlyFdzvBuM5npnFUtsK1_a5lS61zkElh33GTJ3XYK4WniNdH24WNs96kyLBH-slccV51-Ef6bnBb2u0JYc1Kms4poQeFWE5FeU3jj8VLpnjDjA6kw0tD-jekq1V_s0WQfZQr7UcHKB0OnoYtLTByxZ2FsX-p4eip5yITTR_MJLkesxD6LUb48Ut5dtqZCMACkNOj30Dw7Ya6zOdq11Yk41d1NJ5nYbHWit2APVfQsOjVNQh4Xwh0Rz2y8TR081pyeH8nVBdDgGLnVb33koLOh9TaATlQPpgOtO1drntX5_JaAvmr2DFj75zKL7ap-EkvIs550RrnCKSJTMAgYhwe0ysVgcaYDjYrSB07wB-q5unqLpZQei6l2hAzy47rPU1FK8aVnAp7qmvUsCJKJO_JZeAZkTTRIMIbotsKdLSiItcnhqVcNlj6tlmx4Y5Tzr1vImZKy2VF7bhgBcT_HaLlsSZYlcrZdspXjWHB87Mgen0I6THYs2fwiTf9ms2tbimbncgN3n_k9BzV9e7xde7VJ3vHFtMoGm0XykGOYDQT38jXgaHqlK5UdiP05C0WdnvORap7egeYpwTRomVDWK17QhLdiSchXLXY'
BASE_URL = f'https://api.icafecloud.com/api/v2/cafe/{CAFE_ID}'

def calc_coins(stats):
    for_win = 3 if stats.get('win') else -2
    coins = (for_win +
             stats.get('assists', 0) * 0.1 +
             stats.get('kills', 0) * 0.5 -
             stats.get('deaths', 0) * 0.3)
    return max(0, round(coins, 1))

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
    stats = data.get('stats', {})
    user_id = data.get('user_id')
    coins = calc_coins(stats)
    kills = stats.get('kills')
    deaths = stats.get('deaths')
    assists = stats.get('assists')

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
