import random
import decimal
from datetime import datetime

from pos.point_of_sale.config import config
from pos.point_of_sale.verifications import postback_service
from pos.point_of_sale.utils import options
from pos.point_of_sale.verifications import asset
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.web import web
from pos.point_of_sale.bep import bep
from pos.point_of_sale.db_functions.dbactions import DBActions

db_agent = DBActions()
start_time = datetime.now()
pricepoints_options = 'single'
url_options = options.ref_variables() + options.refurl() + config.template
# ==================================================================> for 511 and 510
pricingguid = {}
transids = []
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
			# selected_language = random.choice(config.available_languages)
			try:
				merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
				if config.one_click_pos or config.one_click_ws:
					db_agent.update_merchantbillconfig_oneclick(pricepoint, 1)  # enabling 1click if its not enabled
				if config.single_use_promo:
					db_agent.update_pp_singleuse_promo(pricepoint, 1, 1)
				else:
					db_agent.update_pp_singleuse_promo(pricepoint, 1, 0)  # feature 1 is single use promo
				pricepoint_type = merchantbillconfig[0]['Type']
				package = db_agent.package(config.packageid)
				db_agent.update_processor(config.processors[0], config.packageid)
				db_agent.update_package(config.packageid, merchantid, pricepoint)
				for selected_language in config.available_languages:
					for dmc in config.available_currencies:

						eticket = str(config.packageid) + ':' + str(pricepoint)
						# ========================================================================> preparing package processor
						selected_options = [dmc, selected_language]

						# =======================================================================================================Starting Transactions
						transaction_record = web.create_transaction(pricepoint_type, eticket, selected_options,
						                                            merchantid, url_options, config.processors[0])

						multitrans_base_record = mt.build_multitrans(merchantbillconfig[0], package[0], transaction_record,
						                                             url_options)
						differences_multitrans = mt.multitrans_compare(multitrans_base_record,
						                                               transaction_record['full_record'])

						asset_base_record = asset.build_asset_signup(merchantbillconfig[0], multitrans_base_record,
						                                             transaction_record)
						differences_asset = asset.asset_compare(asset_base_record)
						check_email_differences = emails.check_email_que(pricepoint_type, multitrans_base_record, 'signup')
						postback_service.verify_postback_url("SignUp", config.packageid, transaction_record['TransID'])
						transids.append(transaction_record['TransID'])
						print('*********************SignUp Transaction Verification Complete*********************')
						print()







						if pricepoint_type in [501, 502, 503, 504, 506, 510, 511] and config.one_click_pos:
							one_click_pos_record = web.one_click('pos', eticket, pricepoint_type, multitrans_base_record,
							                                     transaction_record['email'], url_options, selected_options)
							differences_oneclick_pos = mt.multitrans_compare(one_click_pos_record[0], one_click_pos_record[1])
							asset_base_record_onelick = asset.asset_oneclick(merchantbillconfig[0], asset_base_record,
							                                                 one_click_pos_record[1])
							differences_asset = asset.asset_compare(asset_base_record_onelick)
							check_email = emails.check_email_que(pricepoint_type, multitrans_base_record, 'signup')
							config.report['pos' + str(eticket)] = [differences_multitrans, differences_asset, check_email]
							postback_service.verify_postback_url("SignUp", config.packageid, one_click_pos_record[1][0]['TransID'])
							transids.append(one_click_pos_record[1][0]['TransID'])
							print('*********************OneClick POS Transaction Verification Complete*********************')
							print()
						if pricepoint_type in [501, 502, 503, 504, 506, 510, 511] and config.one_click_ws:
							one_click_ws_record = web.one_click('ws', eticket, pricepoint_type, multitrans_base_record,
							                                    transaction_record['email'], url_options, selected_options)
							differences_oneclick_ws = mt.multitrans_compare(one_click_ws_record[0], one_click_ws_record[1])
							asset_base_record_onelick = asset.asset_oneclick(merchantbillconfig[0], asset_base_record,
							                                                 one_click_ws_record[1])
							differences_asset = asset.asset_compare(asset_base_record_onelick)
							check_email = emails.check_email_que(pricepoint_type, one_click_ws_record[0], 'signup')
							postback_service.verify_postback_url("SignUp", config.packageid, one_click_ws_record[1][0]['TransID'])
							config.report['ws' + str(eticket)] = [differences_multitrans, differences_asset, check_email]
							transids.append(one_click_ws_record[1][0]['TransID'])
							print('*********************OneClick WS Transaction Verification Complete*********************')
							print()
						config.report[eticket] = [differences_multitrans, differences_asset, check_email_differences]
						if pricepoint_type == 506 and config.instant_coversion_pos:
							ic_pos_record = web.instant_conversion('pos', eticket, pricepoint_type, multitrans_base_record,
							                                       transaction_record['email'], url_options,
							                                       merchantbillconfig[0])
							differences_ic_pos = mt.multitrans_compare(ic_pos_record[0], ic_pos_record[1])
							asset_ic_record = asset.asset_instant_conversion(merchantbillconfig[0], asset_base_record,
							                                                 ic_pos_record[1])
							differences_asset = asset.asset_compare(asset_ic_record)
							check_email = emails.check_email_que(pricepoint_type, ic_pos_record[1][0], 'signup')
							# postback_service.verify_postback_url("SignUp", config.packageid, ic_pos_record[1]['TransID'])
							transids.append(ic_pos_record[1][0]['TransID'])
							config.report['pos' + str(eticket)] = [differences_ic_pos, differences_asset, check_email]
							print('*********************Instant Conversion Transaction Verification Complete*********************')
							print()

			except Exception as ex:
				print(ex)
		# --------------------------------------------------------------------------------------------------------------BEP
		captures = bep.process_captures()
		if captures == 'Captured':
			check_captures = db_agent.verify_captures(transids)

		conversion = bep.process_rebills(transids)
		if conversion:
			check_rebills_asset = asset.asseets_check_rebills(conversion[0])
			check_rebills_mt = mt.multitrans_check_conversion(conversion[1])

		refunds = bep.process_refund(transids, 841)  # 841 refund expire  842 refund and cancel
		if refunds:
			check_refunds_mt = mt.multitrans_check_refunds(refunds[1])
			check_refunds_asset = asset.asseets_check_refunds(refunds[0])

		reactivate = web.reactivate(transids) #   (conversion[1])
		check_asset_after_reactivation = asset.assets_check_reactivation(reactivate[0])
		check_mt_after_reactivation = mt.mt_check_reactivation(reactivate[1])

	# --------------------------------------------------------------------------------------------------------------BEP

	except Exception as ex:
		print(ex)
web.browser_quit()
end_time = datetime.now()
print('Full test Duration: {}'.format(end_time - start_time))
