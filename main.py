from zadarma import api

api_key = '3cc11c71f64e67825f44'
api_secret = '6058e62a617695dc0f25'

if __name__ == '__main__':

    z_api = api.ZadarmaAPI(key=api_key, secret=api_secret)

    from_number = '13239436353'
    to_number = '14693939998'

    try:
        response = z_api.call('/v1/request/callback/', {
            'from': from_number,
            'to': to_number,
            'predicted': True
        })

        print(response)

    except Exception as e:
        print(f'Error: {e}')

