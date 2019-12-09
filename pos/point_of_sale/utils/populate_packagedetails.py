import traceback
from datetime import datetime
from pos.point_of_sale.config import config
from pos.point_of_sale.db_functions.dbactions import DBActions


db_agent = DBActions()
start_time = datetime.now()

config.test_data['packageid'] = 900
config.test_data['MerchantID'] = 27001

# ==================================================================================================> Begining of the script

pricepoints = db_agent.get_all_pricepoints()
tmp = db_agent.deleteall_from_packagedetails(config.test_data['packageid'] )
for pricepoint in pricepoints:
    try:
        res = db_agent.fill_package_with_pricepoints(config.test_data['packageid'],config.test_data['MerchantID'] ,pricepoint)
        z=3
    except Exception as ex:
        traceback.print_exc()
        print(f"Exception {Exception} ")
        pass

