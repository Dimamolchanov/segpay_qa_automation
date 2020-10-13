import traceback
from datetime import datetime
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions


db_agent = DBActions()
start_time = datetime.now()

config.test_data['packageid'] = [900,901,902]
config.test_data['MerchantID'] = 27001

# ==================================================================================================> Begining of the script






pricepoints = db_agent.get_all_pricepoints()
packageid = None
for packageid in config.test_data['packageid']:
    tmp = db_agent.deleteall_from_packagedetails(packageid)
for pricepoint in pricepoints:
    try:
        pp_type = pricepoint[1]
        if config.test_data['MerchantID'] == 27001:
            if pp_type == 510:
                packageid = 901
            elif pp_type == 511:
                packageid = 902
            else:
                packageid = 900
        elif config.test_data['MerchantID'] == 21621:
            if pp_type == 510:
                packageid = 801
            elif pp_type == 511:
                packageid = 802
            else:
                packageid = 800
        res = db_agent.fill_package_with_pricepoints(packageid,config.test_data['MerchantID'] ,pricepoint[0])
        z=3
    except Exception as ex:
        traceback.print_exc()
        print(f"Exception {Exception} ")
        pass

