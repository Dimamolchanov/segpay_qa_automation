import requests

from coinbase.exchange import API_HOST, coinbase_auth


class Accounts(object):
    @staticmethod
    def get_list():
        result = requests.get('{api_host}/accounts'.format(api_host=API_HOST), auth=coinbase_auth)

        return result.json()

    @staticmethod
    def get_item(account_id):
        result = requests.get('{api_host}/accounts/{account_id}'.format(api_host=API_HOST, account_id=account_id),
                              auth=coinbase_auth)

        return result.json()

    @staticmethod
    def get_history(account_id, limit=100, before=None, after=None):
        params = {'limit': limit}

        if before:
            params['before'] = before
        elif after:
            params['after'] = after

        result = requests.get(
            '{api_host}/accounts/{account_id}/ledger'.format(api_host=API_HOST, account_id=account_id),
            params, auth=coinbase_auth
        )

        return result.json()

    @staticmethod
    def get_holds(account_id, limit=100, before=None, after=None):
        params = {'limit': limit}

        if before:
            params['before'] = before.isoformat()
        elif after:
            params['after'] = after.isoformat()

        result = requests.get(
            '{api_host}/accounts/{account_id}/holds'.format(api_host=API_HOST, account_id=account_id),
            params, auth=coinbase_auth
        )

        return result.json()


class Orders(object):
    @staticmethod
    def create(side, product_id, price=None, size=None, _type='limit', client_oid=None, stp='dc', time_in_force='GTC',
               funds=None, post_only=None):
        params = {
            'side': side,
            'product_id': product_id,
            'type': _type,
            'stp': stp
        }

        if client_oid:
            params['client_oid'] = client_oid

        if _type == 'limit':
            params['price'] = str(price)
            params['size'] = str(size)
            params['time_in_force'] = time_in_force

            if time_in_force == 'GTC' and post_only is not None:
                params['post_only'] = 1
        elif _type == 'market':
            if funds:
                params['funds'] = str(funds)
            elif size:
                params['size'] = str(size)
            else:
                raise ValueError()
        else:
            raise ValueError()

        result = requests.post('{api_host}/orders'.format(api_host=API_HOST), json=params, auth=coinbase_auth)

        return result.json()

    @staticmethod
    def cancel(order_id):
        result = requests.delete('{api_host}/orders/{order_id}'.format(api_host=API_HOST, order_id=order_id),
                                 auth=coinbase_auth)

        return result.status_code == 200

    @staticmethod
    def get_list(statuses=None, limit=100, before=None, after=None):
        if not statuses:
            statuses = ['all']

        params = {
            'status': statuses,
            'limit': limit
        }

        if before:
            params['before'] = before.isoformat()
        elif after:
            params['after'] = after.isoformat()

        result = requests.get('{api_host}/orders'.format(api_host=API_HOST), params, auth=coinbase_auth)

        return result.json()

    @staticmethod
    def get_item(order_id):
        result = requests.get('{api_host}/orders/{order_id}'.format(api_host=API_HOST, order_id=order_id),
                              auth=coinbase_auth)

        return result.json()


class Fills(object):
    @staticmethod
    def get_list(order_id='all', product_id='all', limit=100, before=None, after=None):
        params = {
            'order_id': order_id,
            'product_id': product_id,
            'limit': limit
        }

        if before:
            params['before'] = before
        elif after:
            params['after'] = after

        result = requests.get('{api_host}/fills'.format(api_host=API_HOST), params, auth=coinbase_auth)

        return result.json()


class Transfers(object):
    @staticmethod
    def make_transfer(_type, amount, coinbase_account_id):
        params = {
            'type': _type,
            'amount': str(amount),
            'coinbase_account_id': coinbase_account_id
        }

        result = requests.post('{api_host}/transfers'.format(api_host=API_HOST), json=params, auth=coinbase_auth)

        return result.status_code == 200

    @staticmethod
    def deposit(amount, coinbase_account_id):
        return Transfers.make_transfer('deposit', amount, coinbase_account_id)

    @staticmethod
    def withdraw(amount, coinbase_account_id):
        return Transfers.make_transfer('withdraw', amount, coinbase_account_id)


class Reports(object):
    @staticmethod
    def create(start_date, end_date, _type='fills', format='pdf'):
        params = {
            'type': _type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'format': format
        }
        result = requests.post('{api_host}/reports'.format(api_host=API_HOST), json=params, auth=coinbase_auth)

        return result.status_code == 200

    @staticmethod
    def create_fills_report(start_date, end_date):
        return Reports.create(start_date, end_date, 'fills')

    @staticmethod
    def get_report_status(report_id):
        result = requests.get('{api_host}/reports/{report_id}'.format(api_host=API_HOST, report_id=report_id),
                              auth=coinbase_auth)

        return result.json()
