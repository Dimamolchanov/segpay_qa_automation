class Currencies(object):
    def get_list(self):
        pass


class ExchangeRates(object):
    def get_list(self):
        pass


class Price(object):
    def get_buy_price(self, currency):
        pass

    def get_sell_price(self, currency):
        pass

    def get_spot_price(self, currency, date):
        pass


class Time(object):
    def get_item(self):
        pass
