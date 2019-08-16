import traceback
from datetime import datetime
from functools import partial
from pos.point_of_sale.bep import bep
from pos.point_of_sale.config import config
from pos.point_of_sale.config.TransActionService import TransActionService
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.runners import test_methods
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web

db_agent = DBActions()
# start_time = datetime.now()
pricepoints_options = 'single'
start_time = datetime.now()
pricepoint_type = 0
merchantbillconfig = []
results = [1, 1]
config.test_data['eticket'] = ''
actions = {'singup': partial(test_methods.sign_up_trans_web1, config.test_data),
           'oneclick_pos': partial(test_methods.signup_oc, 'pos', config.test_data['eticket'], config.test_data),
		   'oneclick_pos_all': partial(test_methods.signup_oc_all, 'pos', config.test_data['eticket'], config.test_data), # iterrate all pricpoints in 1 click to all pricepoints
           'captures': partial(bep.process_captures),
           'check_captures': partial(db_agent.verify_captures, config.transids),
           'conversion': partial(bep.process_rebills, config.transids),
           'check_conversion_asset': partial(asset.asseets_check_rebills, config.results[0]),
           'check_conversion_mt': partial(mt.multitrans_check_conversion, config.results[1]),
           'refunds': partial(bep.process_refund, config.transids, 841),
           'check_refunds_mt': partial(mt.multitrans_check_refunds),  #, config.results[1]
           'check_refunds_asset': partial(asset.asseets_check_refunds),
           'reactivate': partial(web.reactivate, config.transids),
           'check_asset_reactivation': partial(asset.assets_check_reactivation),
           'check_mt_reactivation': partial(mt.mt_check_reactivation),
		   'check_refunds': partial(test_methods.verify_refunds)
           }
bep_basic1 = ['refunds','check_refunds']
bep_basic = ['refunds', 'check_refunds_mt', 'check_refunds_asset', 'reactivate', 'check_asset_reactivation', 'check_mt_reactivation']
bep_basic_with_capture = ['captures', 'refunds', 'check_refunds_mt', 'check_refunds_asset', 'reactivate', 'check_asset_reactivation', 'check_mt_reactivation']
# bep_basic = ['captures', 'check_captures', 'refunds', 'check_refunds_mt', 'check_refunds_asset']

# ==================================================================================================> Begining of the script
for merchantid in config.merchants:
	if pricepoints_options == 'type':
		pricepoints = db_agent.pricepoint_type(merchantid, [511, 501, 506])  # ,505
	elif pricepoints_options == 'list':
		pricepoints = db_agent.pricepoint_list(merchantid)
	else:
		pricepoints = config.pricepoints

	for pricepoint in pricepoints:

		try:
			config.test_data = TransActionService.prepare_data(pricepoint, 1)
			actions['singup']()
			config.logging.info('')
		except Exception as ex:
			traceback.print_exc()
			print(f"Exception {Exception} ")
			pass
	actions['oneclick_pos']()
	#actions['oneclick_pos_all']()

	for item in bep_basic1:
		try:
			config.results = actions[item]()
			z = 3
		except Exception as ex:
			traceback.print_exc()
			print(f"Exception {Exception} ")
			pass

web.browser_quit()
emails.check_email_status(config.transids)
end_time = datetime.now()
print('Full test Duration: {}'.format(end_time - start_time))
