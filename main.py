from flask import Flask, request, jsonify
import requests
import logging
from functools import wraps
import time

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
CAFE_ID = '81809'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI1IiwianRpIjoiNTliNzBiNTdhYTJkMTJmNjk5OWVkMDdlYWNkMTkzMzM3NDJkYzAwMTBlOGNlNjY3NTJhODg3Mzg2YzM3MDJiZTkzZWE1MjMzNGRjZWMyN2YiLCJpYXQiOjE3NTYwNjM2NDYuOTEwOTQxLCJuYmYiOjE3NTYwNjM2NDYuOTEwOTQ0LCJleHAiOjE3ODc1OTk2NDYuOTA4MDY1LCJzdWIiOiIzODQxMTk0MjgzODE4MDkiLCJzY29wZXMiOltdfQ.Omv6u-S6viNp7JM4a_2HTtRb3ZRWxHavpVznxqwLSznK1BUdt1BPx7H-HOF4QcrcdPkpQq-MXCmzlyFdzvBuM5npnFUtsK1_a5lS61zkElh33GTJ3XYK4WniNdH24WNs96kyLBH-slccV51-Ef6bnBb2u0JYc1Kms4poQeFWE5FeU3jj8VLpnjDjA6kw0tD-jekq1V_s0WQfZQr7UcHKB0OnoYtLTByxZ2FsX-p4eip5yITTR_MJLkesxD6LUb48Ut5dtqZCMACkNOj30Dw7Ya6zOdq11Yk41d1NJ5nYbHWit2APVfQsOjVNQh4Xwh0Rz2y8TR081pyeH8nVBdDgGLnVb33koLOh9TaATlQPpgOtO1drntX5_JaAvmr2DFj75zKL7ap-EkvIs550RrnCKSJTMAgYhwe0ysVgcaYDjYrSB07wB-q5unqLpZQei6l2hAzy47rPU1FK8aVnAp7qmvUsCJKJO_JZeAZkTTRIMIbotsKdLSiItcnhqVcNlj6tlmx4Y5Tzr1vImZKy2VF7bhgBcT_HaLlsSZYlcrZdspXjWHB87Mgen0I6THYs2fwiTf9ms2tbimbncgN3n_k9BzV9e7xde7VJ3vHFtMoGm0XykGOYDQT38jXgaHqlK5UdiP05C0WdnvORap7egeYpwTRomVDWK17QhLdiSchXLXY'
BASE_URL = f'https://api.icafecloud.com/api/v2/cafe/{CAFE_ID}'
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def retry_request(max_retries=3, delay=1):
    """Декоратор для повторных попыток при неудачном запросе"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.RequestException as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        return None
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator


@retry_request(max_retries=3)
def make_api_request(method, url, **kwargs):
    """Универсальная функция для API запросов с обработкой ошибок"""
    kwargs.setdefault('timeout', 5)
    kwargs.setdefault('headers', {}).update(HEADERS)
    
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout on {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {url}, error: {e}")
    return None


def calc_coins(stats):
    """Расчет монет с защитой от None значений"""
    if not stats:
        return 0
        
    for_win = 3 if stats.get('win') else -2
    kills = stats.get('kills') or 0
    assists = stats.get('assists') or 0
    deaths = stats.get('deaths') or 0
    
    coins = (for_win +
             assists * 0.1 +
             kills * 0.5 -
             deaths * 0.3)
    
    return max(0, round(coins, 1))


def send_event_data(username, stats):
    """Отправка данных на несколько ивентов"""
    if not username or not stats:
        return False
        
    # Список активных ивентов
    event_ids = [
        '018f7984-74e7-11f0-9d62-16f956cef18b'
    ]
    
    data = {
        'action': 'custom-match-stats',
        'custom_member_account': username,
        'custom_wins': 1 if stats.get('win') else 0,
        'custom_kills': stats.get('kills', 0),
        'custom_assists': stats.get('assists', 0),
        'custom_deaths': stats.get('deaths', 0)
    }
    
    success_count = 0
    for event_id in event_ids:
        if not event_id:  # Пропускаем пустые ID
            continue
            
        url = f'{BASE_URL}/events/{event_id}/addCustomRecord'
        result = make_api_request('POST', url, json=data)
        if result:
            success_count += 1
            
    return success_count > 0


def get_user_by_ip(ip):
    """Получение пользователя по IP"""
    url = f'{BASE_URL}/base/query'
    result = make_api_request('GET', url)
    
    if not result:
        return None
        
    pc_list = result.get('data', {}).get('pcs_init', {}).get('pc_list', [])
    
    for pc in pc_list:
        if pc.get('pc_ip') == ip:
            return {
                'username': pc.get('member_account'),
                'user_id': pc.get('member_id')
            }
    
    return None


def topup_user(user_id, coins, comment):
    """Начисление монет пользователю"""
    if not user_id or coins <= 0:
        return None
        
    url = f'{BASE_URL}/members/action/topup'
    body = {
        'topup_ids': str(user_id),
        'topup_value': 0,
        'add_coin': coins,
        'comment': comment
    }
    
    return make_api_request('POST', url, json=body)


@app.route('/getuser', methods=['POST'])
def get_user():
    """Endpoint для получения пользователя"""
    try:
        data = request.get_json()
        if not data or not data.get('ip'):
            return jsonify({'error': 'IP address required'}), 400
            
        user_data = get_user_by_ip(data['ip'])
        if user_data:
            return jsonify(user_data)
        
        return jsonify({'error': 'User not found'}), 404
        
    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/topup', methods=['POST'])
def topup():
    """Endpoint для начисления монет"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        stats = data.get('stats', {})
        user_id = data.get('user_id')
        username = data.get('username')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Расчет монет
        coins = calc_coins(stats)
        
        # Отправка на ивенты (не блокирующая операция)
        send_event_data(username, stats)
        
        # Начисление монет
        kills = stats.get('kills', 0)
        deaths = stats.get('deaths', 0)
        assists = stats.get('assists', 0)
        comment = f'cs2({kills} kills, {deaths} deaths, {assists} assists)'
        
        result = topup_user(user_id, coins, comment)
        
        if result:
            return jsonify({
                'success': True,
                'coins': coins,
                'response': result
            })
        
        return jsonify({'error': 'Failed to topup coins'}), 500
        
    except Exception as e:
        logger.error(f"Error in topup: {e}")
        return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
