import unittest

from pos.point_of_sale.postbacks import test_methods
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.config import config
from pos.point_of_sale.bep import bep
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web

db_agent = DBActions()


class RunTests(unittest.TestCase):

    def setUp(self):
        self.pricepoints = TransActionService.load_data()

    def step_1_test_sign_up_trans_web(self):
        for pricepoint in self.pricepoints:
            config.test_data = TransActionService.prepare_data(pricepoint, 1)
            self.assertTrue(test_methods.sign_up_trans_web(config.test_data), "Sign Up WEB failed!!!")

    def step_2_test_sign_up_trans_oc_pos(self):
        for pricepoint in self.pricepoints:
            config.test_data = TransActionService.prepare_data(pricepoint, 1)
            if config.test_data['pricepoint_type'] not in config.oc_list:
                print("{} price point is not eligible for OC")
                return False
            self.assertTrue(test_methods.sign_up_trans_oc('pos', config.test_data), "Sign Up oc POS failed!!!")

    def step_3_test_sign_up_trans_oc_ws(self):
        for pricepoint in self.pricepoints:
            config.test_data = TransActionService.prepare_data(pricepoint, 1)
            if config.test_data['pricepoint_type'] not in config.oc_list:
                print("{} price point is not eligible for OC")
                return False
            self.assertTrue(test_methods.sign_up_trans_oc('ws', config.test_data), "Sign Up oc WS failed!!!")

    def step_4_test_sign_up_ic_pos(self):
        for pricepoint in self.pricepoints:
            config.test_data = TransActionService.prepare_data(pricepoint, 1)
            if config.test_data['pricepoint_type'] not in config.oc_list:
                print("{} price point is not eligible for OC")
                return False
            self.assertTrue(test_methods.sign_up_trans_oc('ic', config.test_data), "Sign Up oc WS failed!!!")

    def step_5_process_captures(self):
        captures = bep.process_captures()
        if captures == 'Captured':
            check_captures = db_agent.verify_captures(config.transids)

    def step_6_process_rebills(self):
        conversion = bep.process_rebills(config.transids)
        if conversion:
            check_rebills_asset = asset.asseets_check_rebills(conversion[0])
            check_rebills_mt = mt.multitrans_check_conversion(conversion[1])

    def step_7_process_rebills(self):
        conversion = bep.process_rebills(config.transids)
        if conversion:
            check_rebills_asset = asset.asseets_check_rebills(conversion[0])
            check_rebills_mt = mt.multitrans_check_conversion(conversion[1])

    def step_8_process_refunds(self):
        refunds = bep.process_refund(config.transids, 841)
        if refunds:
            check_refunds_mt = mt.multitrans_check_refunds(refunds[1])
            check_refunds_asset = asset.asseets_check_refunds(refunds[0])

    def step_9_process_reactivation(self):
        reactivate = web.reactivate(config.transids)  # (conversion[1])
        check_asset_after_reactivation = asset.assets_check_reactivation(reactivate[0])
        check_mt_after_reactivation = mt.mt_check_reactivation(reactivate[1])

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
        TransActionService.close_browser()




