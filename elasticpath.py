# https://documentation.elasticpath.com/commerce-cloud/docs/api/

import datetime as dt

import requests

_access_token = ''
_datetime = dt.datetime.now() - dt.timedelta(hours=1)
_token_expires_in = 0


def get_access_token(client_id: str, client_secret: str) -> str:
    global _access_token
    global _token_expires_in
    global _datetime

    if dt.datetime.now() - _datetime > dt.timedelta(seconds=_token_expires_in):
        access_token_dict = _get_access_token(client_id, client_secret)

        _access_token = access_token_dict['access_token']
        _token_expires_in = access_token_dict['expires_in']

        _datetime = dt.datetime.now()

    return _access_token


def _get_access_token(client_id: str, client_secret: str) -> dict:
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    response.raise_for_status()

    return response.json()


def get_products(access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/products', headers=headers)
    response.raise_for_status()

    return response.json()


def get_cart(access_token: str, user: str) -> dict:
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/carts/{}'.format(user), headers=headers)
    response.raise_for_status()

    return response.json()


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

    return response.json()


def get_product(product_id: str, access_token: str) -> dict:
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/products/{}'.format(product_id), headers=headers)
    response.raise_for_status()

    return response.json()


def get_file(file_id: str, access_token: str) -> dict:
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/files/{}'.format(file_id), headers=headers)
    response.raise_for_status()

    return response.json()


def get_product_variation(variation_id: str, access_token: str) -> dict:
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/variations/{}'.format(variation_id), headers=headers)
    response.raise_for_status()

    return response.json()


def get_cart_items(user, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/carts/{}/items'.format(user), headers=headers)
    response.raise_for_status()

    return response.json()


def remove_cart_item(user: str, product_id: str, access_token: str) -> dict:
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.delete('https://api.moltin.com/v2/carts/{}/items/{}'.format(user, product_id), headers=headers)
    response.raise_for_status()

    return response.json()


def create_customer(username: str, email: str, access_token: str) -> dict:
    headers = {'Authorization': 'Bearer {}'.format(access_token),
               'Content-Type': 'application/json',
               }

    data = {'data': {'type': 'customer',
                     'name': username,
                     'email': email,
                     }
            }

    response = requests.post('https://api.moltin.com/v2/customers', headers=headers, json=data)
    response.raise_for_status()

    return response.json()


def get_customer(username: str, access_token: str):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}

    response = requests.get('https://api.moltin.com/v2/customers/{}'.format(username), headers=headers)
    response.raise_for_status()

    return response.json()


def filter_customers_by_email(email: str, access_token: str):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    params = {'filter': 'eq(email,{})'.format(email)}

    response = requests.get('https://api.moltin.com/v2/customers', headers=headers, params=params)
    response.raise_for_status()

    return response.json()


def get_product_display_price(product: dict) -> dict:
    return product['meta']['display_price']['with_tax']
