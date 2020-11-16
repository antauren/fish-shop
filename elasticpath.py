import requests


def get_access_token(client_id, client_secret):
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict['access_token']


def get_products(access_token):
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict


def get_cart(access_token: str, user: str) -> dict:
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get('https://api.moltin.com/v2/carts/{}'.format(user), headers=headers)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict


def add_product_to_cart(access_token: str, customer: str, product_id: str, quantity: int):
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json',
    }

    data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': quantity,
        }
    }

    response = requests.post('https://api.moltin.com/v2/carts/{}/items'.format(customer), headers=headers, json=data)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict
