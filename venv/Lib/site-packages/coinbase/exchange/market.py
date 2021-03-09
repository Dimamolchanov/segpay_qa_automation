import requests

from coinbase.exchange import API_HOST, coinbase_auth


class Products(object):
    @staticmethod
    def get_list():
        result = requests.get('{api_host}/products'.format(api_host=API_HOST), auth=coinbase_auth)

        return result.json()

    @staticmethod
    def get_order_book(product_id, level=1):
        params = {'level': level}
        result = requests.get(
            '{api_host}/products/{product_id}/book'.format(api_host=API_HOST, product_id=product_id),
            params, auth=coinbase_auth
        )

        return result.json()

    @staticmethod
    def get_ticker(product_id):
        result = requests.get(
            '{api_host}/products/{product_id}/ticker'.format(api_host=API_HOST, product_id=product_id),
            auth=coinbase_auth
        )

        return result.json()

    @staticmethod
    def get_trades(product_id, limit=100, before=None, after=None):
        params = {'limit': limit}

        if before:
            params['before'] = before
        elif after:
            params['after'] = after

        result = requests.get(
            '{api_host}/products/{product_id}/trades'.format(api_host=API_HOST, product_id=product_id),
            params, auth=coinbase_auth
        )

        return result.json()

    @staticmethod
    def get_historic_rates(product_id, start, end, granularity=3600):
        params = {
            'start': start.isoformat(),
            'end': end.isoformat(),
            'granularity': granularity
        }
        result = requests.get(
            '{api_host}/products/{product_id}/candles'.format(api_host=API_HOST, product_id=product_id),
            params, auth=coinbase_auth
        )

        return result.json()

    @staticmethod
    def get_24h_stats(product_id):
        result = requests.get('{api_host}/products/{product_id}/stats'.format(api_host=API_HOST, product_id=product_id),
                              auth=coinbase_auth)

        return result.json()


class Currencies(object):
    @staticmethod
    def get_list():
        result = requests.get('{api_host}/currencies'.format(api_host=API_HOST), auth=coinbase_auth)

        return result.json()


class Time(object):
    @staticmethod
    def get_item():
        result = requests.get('{api_host}/time'.format(api_host=API_HOST))

        return result.json()
