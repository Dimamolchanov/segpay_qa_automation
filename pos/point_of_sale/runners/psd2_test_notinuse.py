import random
import decimal
from datetime import datetime
import traceback
from pos.point_of_sale.config import config
from pos.point_of_sale.verifications import postback_service
from pos.point_of_sale.utils import options
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web_module
from pos.point_of_sale.bep import bep
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.runners import test_methods
from pos.point_of_sale.config.TransActionService import TransActionService
db_agent = DBActions()
start_time = datetime.now()
pricepoints_options = 'single'
#url_options = config.template # options.ref_variables() + options.refurl() + config.template
# ==================================================================> for 511 and 510
#transguids = []
pricingguid = {}
#transids = []
rebills_pids = []
pricepoint_type = 0
dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
merchantbillconfig = []

# ==================================================================================================> Begining of the script
for merchantid in config.merchants:
	try:
		if pricepoints_options == 'type':
			pricepoints = db_agent.pricepoint_type(merchantid, [511, 501, 506])  # ,505
		elif pricepoints_options == 'list':
			pricepoints = db_agent.pricepoint_list(merchantid)
		else:
			pricepoints = config.pricepoints
		for pricepoint in pricepoints:
			try:

				for card in config.cards_3ds:
					config.test_data = TransActionService.prepare_data(pricepoint, 1)
					eticket = config.test_data['eticket']
					config.test_data['cc3ds'] = card
					config.test_data['cc'] = card['card']
					create_transaction = test_methods.sign_up_trans_web1(config.test_data)
				print()
				#one_click_record_ws = test_methods.signup_oc('ws', eticket, config.test_data)
				#one_click_record = test_methods.signup_oc('pos', eticket,  config.test_data)
			except Exception as ex:
				traceback.print_exc()
				print(f"Exception {Exception} ")
				pass
		# --------------------------------------------------------------------------------------------------------------BEP
		# captures = bep.process_captures()
		# if captures == 'Captured':
		# 	check_captures = db_agent.verify_captures(config.transids)

		# conversion = bep.process_rebills(config.transids)  # bep.process_rebills(rebills_pids)
		# if conversion:
		# 	check_rebills_asset = asset.asseets_check_rebills(conversion[0])
		# 	check_rebills_mt = mt.multitrans_check_conversion(conversion[1])

		# refunds = bep.process_refund(config.transids, 841)  # 841 refund expire  842 refund and cancel  0 for random choices
		# if refunds:
		# 	check_refunds_mt = mt.multitrans_check_refunds(refunds[1])
		# 	check_refunds_asset = asset.asseets_check_refunds(refunds[0])
		#
		# reactivate = web.reactivate(config.transids) #   (conversion[1])
		# check_asset_after_reactivation = asset.assets_check_reactivation(reactivate[0])
		# check_mt_after_reactivation = mt.mt_check_reactivation(reactivate[1])

	# --------------------------------------------------------------------------------------------------------------BEP

	except Exception as ex:
		traceback.print_exc()
		print(f"Exception {Exception} ")
		pass
web_module.browser_quit()
emails.check_email_status(config.transids)
end_time = datetime.now()
print('Full test Duration: {}'.format(end_time - start_time))
