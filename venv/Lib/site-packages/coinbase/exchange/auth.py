import base64
import hashlib
import hmac
import time

from requests.auth import AuthBase

from coinbase.conf import settings


class CoinbaseExchangeAuth(AuthBase):
    def __init__(self):
        self.api_key = settings.EXCHANGE_API_KEY
        self.secret_key = settings.EXCHANGE_SECRET_KEY
        self.passphrase = settings.EXCHANGE_PASSPHRASE

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })

        return request
