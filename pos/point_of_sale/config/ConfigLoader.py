from pos.point_of_sale.config import config
from pos.point_of_sale.utils import options
from pos.point_of_sale.web import web
from pos.point_of_sale.db_functions.dbactions import DBActions


db_agent = DBActions()


class ConfigLoader:
    @staticmethod
    def load_data():
        if config.pricepoints[0] == 'type':
            pricepoints = db_agent.pricepoint_type(config.merchants[0], [511, 501, 506])
        elif config.pricepoints[0] == 'list':
             pricepoints = db_agent.pricepoint_list(config.merchants[0])
        else:
            pricepoints = config.pricepoints
        return pricepoints

    @staticmethod
    def prepare_data(pricepoint):
        test_data = {}
        merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
        if config.one_click_pos or config.one_click_ws:
            db_agent.update_merchantbillconfig_oneclick(pricepoint, 1)
        db_agent.update_pp_singleuse_promo(pricepoint, 1, config.single_use_promo)
        pricepoint_type = merchantbillconfig[0]['Type']
        package = db_agent.package(config.packageid)
        db_agent.update_processor(config.processors[0], config.packageid)
        db_agent.update_package(config.packageid, config.merchants[0], pricepoint)
        eticket = str(config.packageid) + ':' + str(pricepoint)
        url_options = options.ref_variables() + options.refurl() + config.template
        test_data['pricepoint_type'] = pricepoint_type
        test_data['package'] = package
        test_data['eticket'] = eticket
        test_data['url_options'] = url_options
        test_data['merchantbillconfig'] = merchantbillconfig
        return test_data

    @staticmethod
    def close_brawser():
        try:
            web.browser_quit()
            print("Webdriver closed")
        except Exception as ex:
            print(ex)
