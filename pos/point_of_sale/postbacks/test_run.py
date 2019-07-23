import unittest

from pos.point_of_sale.postbacks import test_methods
from pos.point_of_sale.config.ConfigLoader import ConfigLoader
from pos.point_of_sale.config import config


class RunTests(unittest.TestCase):

    def setUp(self):
        self.pricepoints = ConfigLoader.load_data()

    def test_sign_up_trans(self):
        for pricepoint in self.pricepoints:
            config.test_data = ConfigLoader.prepare_data(pricepoint)
            config.transaction_record.append(test_methods.sign_up_trans_create(config.test_data))


    def tearDown(self):
        ConfigLoader.close_brawser()




