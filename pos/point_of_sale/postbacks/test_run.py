import unittest

from pos.point_of_sale.postbacks import test_methods
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.config import config


class RunTests(unittest.TestCase):

    def setUp(self):
        self.pricepoints = TransActionService.load_data()

    def step_1_test_sign_up_trans_web(self):
        for pricepoint in self.pricepoints:
            config.test_data = TransActionService.prepare_data(pricepoint)
            self.assertTrue(test_methods.sign_up_trans_web(config.test_data), "Sign Up WEB failed!!!")

    def step_2_test_sign_up_trans_oc_pos(self):
        for pricepoint in self.pricepoints:
            config.test_data = TransActionService.prepare_data(pricepoint)
            self.assertTrue(test_methods.sign_up_trans_oc_pos(config.test_data), "Sign Up oc POS failed!!!")

    def _steps(self):
        for name in dir(self):  # dir() result is implicitly sorted
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        for name, step in self._steps():
            try:
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))

    def tearDown(self):
        TransActionService.close_brawser()




