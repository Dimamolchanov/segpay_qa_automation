import os
import importlib


class Settings(object):
    def __init__(self):
        self.EXCHANGE_API_KEY = None
        self.EXCHANGE_SECRET_KEY = None
        self.EXCHANGE_PASSPHRASE = None

        settings_module = os.environ.get('COINBASE_CONFIG')

        if settings_module:
            mod = importlib.import_module(settings_module)

            for setting in dir(mod):
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)

settings = Settings()
