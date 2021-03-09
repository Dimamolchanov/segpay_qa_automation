class Users(object):
    def get_item(self, user_id):
        pass

    def get_current_user(self):
        pass

    def get_current_user_auth_info(self):
        pass

    def update_current_user(self):
        pass


class Accounts(object):
    def get_list(self):
        pass

    def get_item(self, account_id):
        pass

    def create(self, name):
        pass

    def set_primary(self, account_id):
        pass

    def update(self, account_id, name):
        pass

    def delete(self, account_id):
        pass


class Addresses(object):
    def get_list(self, account_id):
        pass

    def get_item(self, account_id, address_id):
        pass

    def get_address_transactions(self, account_id, address_id):
        pass

    def create(self, account_id, name, callback_url=None):
        pass


class Transactions(object):
    def get_list(self, account_id):
        pass

    def get_item(self, account_id, transaction_id):
        pass

    @staticmethod
    def create(account_id, _type, to, amount, currency, description, skip_notifications=None, fee=None, idem=None):
        pass

    def send_money(self, account_id, to, amount, currency, description, skip_notifications, fee, idem):
        return self.create(account_id, 'send', to, amount, currency, description, skip_notifications, fee, idem)

    def transfer_money_between_accounts(self, account_id, to, amount, currency, description):
        return self.create(account_id, 'transfer', to, amount, currency, description)

    def request_money(self, account_id, to, amount, currency, description):
        return self.create(account_id, 'request', to, amount, currency, description)

    def complete_money_request(self, account_id, transaction_id):
        pass

    def resend_money_request(self, account_id, transaction_id):
        pass

    def cancel_money_request(self, account_id, transaction_id):
        pass
