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


def get_product(product_id: str, access_token: str) -> dict:
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get('https://api.moltin.com/v2/products/{}'.format(product_id), headers=headers)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict


def get_file(file_id: str, access_token: str) -> dict:
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get('https://api.moltin.com/v2/files/{}'.format(file_id), headers=headers)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict


def get_product_variation(variation_id: str, access_token: str) -> dict:
    # https://documentation.elasticpath.com/commerce-cloud/docs/api/catalog/product-variations/get-a-product-variation.html

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get('https://api.moltin.com/v2/variations/{}'.format(variation_id), headers=headers)
    response.raise_for_status()

    response_dict = response.json()
    return response_dict


def get_cart_items(user, access_token):
    # https://documentation.elasticpath.com/commerce-cloud/docs/api/carts-and-checkout/carts/cart-items/get-cart-items.html

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.get('https://api.moltin.com/v2/carts/{}/items'.format(user), headers=headers)
    response.raise_for_status()

    return response.json()


def remove_cart_item(user: str, product_id: str, access_token: str) -> dict:
    # https://documentation.elasticpath.com/commerce-cloud/docs/api/carts-and-checkout/carts/cart-items/remove-cart-item.html

    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
    }

    response = requests.delete('https://api.moltin.com/v2/carts/{}/items/{}'.format(user, product_id), headers=headers)
    response.raise_for_status()

    return response.json()


def create_customer(username: str, email: str, access_token: str) -> dict:
    # https://documentation.elasticpath.com/commerce-cloud/docs/api/orders-and-customers/customers/create-a-customer.html

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
    # https://documentation.elasticpath.com/commerce-cloud/docs/api/orders-and-customers/customers/get-a-customer.html

    headers = {'Authorization': 'Bearer {}'.format(access_token),
               }

    response = requests.get('https://api.moltin.com/v2/customers/{}'.format(username), headers=headers)
    response.raise_for_status()

    return response.json()


def filter_customers_by_email(email: str, access_token: str):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    params = {'filter': 'eq(email,{})'.format(email)}

    response = requests.get('https://api.moltin.com/v2/customers', headers=headers, params=params)
    response.raise_for_status()

    return response.json()
