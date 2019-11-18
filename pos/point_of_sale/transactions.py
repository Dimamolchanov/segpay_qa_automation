import random
import decimal
from datetime import datetime

from pos.point_of_sale.config import config
from pos.point_of_sale.utils import options
from pos.point_of_sale.verifications import asset, postback_service
from pos.point_of_sale.verifications import emails
from pos.point_of_sale.verifications import mts as mt
from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.web import web_module


db_agent = DBActions()
current_date = (datetime.now().date())
pricepoints = []
report = {}
# ==================================================================> Configuration
#config.enviroment = 'stage'
enviroment= config.enviroment
merchants = [27001]
packageid = 99
processors = [65]
pricepoints_options = 'single'
# ==================================================================> Options
refurl = options.refurl()
ref_variables = options.ref_variables()
template = ''  # '&template=defaultnopaypal'
url_options = ref_variables + refurl + template

available_currencies = ['USD', "AUD", "CHF",  "EUR", "GBP"]#, "HKD", "JPY", "NOK", "SEK"] # "DKK",
available_languages = ['EN']#, "PT", "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]

one_click_pos = True
one_click_ws = False
process_captures = False
process_rebills = False
process_refund = False
instant_coversion_pos = True
instant_coversion_ws = False
single_use_promo = False

# ==================================================================> for 511 and 510
pricingguid = {}
transids = []
rebills_pids = []

pricepoint_type = 0
dynamic_price = decimal.Decimal('%d.%d' % (random.randint(3, 19), random.randint(0, 99)))
merchantbillconfig = []








# ==================================================================================================> Begining of the script
for merchantid in merchants:
	try:
		if pricepoints_options == 'single':
			pricepoints = [27005]
		elif pricepoints_options == 'type':
			pricepoints = db_agent.pricepoint_type(merchantid, [501, 502, 503, 504, 505, 506, 510, 511])
		elif pricepoints_options == 'list':
			pricepoints = db_agent.pricepoint_list(merchantid)
		for pricepoint in pricepoints:
			selected_currency = random.choice(available_currencies)
			selected_language = random.choice(available_languages)
			selected_options = [selected_currency, selected_language]
			try:

				eticket = str(packageid) + ':' + str(pricepoint)
				# ========================================================================> preparing package processor
				merchantbillconfig = db_agent.merchantbillconfig(pricepoint)
				if one_click_pos or one_click_ws:
					db_agent.update_merchantbillconfig_oneclick(pricepoint, 1)  # enabling 1click if its not enabled

				if single_use_promo:
					db_agent.update_pp_singleuse_promo(pricepoint, 1, 1)
				else:
					db_agent.update_pp_singleuse_promo(pricepoint, 1, 0)  # feature 1 is single use promo
				pricepoint_type = merchantbillconfig[0]['Type']
				package = db_agent.package(packageid)
				db_agent.update_processor(processors[0], packageid)
				db_agent.update_package(packageid, merchantid, pricepoint)

				transaction_record = web_module.create_transaction(pricepoint_type, eticket, selected_options, enviroment,
                                                                   merchantid, url_options, processors[0])
				multitrans_base_record = mt.build_multitrans(merchantbillconfig[0], package[0], transaction_record,
				                                             url_options)
				differences_multitrans = mt.multitrans_compare(multitrans_base_record,
				                                               transaction_record['full_record'])

				asset_base_record = asset.build_asset_signup(merchantbillconfig[0], multitrans_base_record,
				                                             transaction_record)
				differences_asset = asset.asset_compare(asset_base_record)

				check_email_differences = emails.check_email_que(pricepoint_type, multitrans_base_record, 'signup')

				postback_service.verify_postback_url("SignUp", packageid, transaction_record['TransID'])

				transids.append(transaction_record['TransID'])
				if pricepoint_type in [501,505,506,511]:
					rebills_pids.append(transaction_record['PurchaseID'])

				print('*********************SignUp Transaction Verification Complete*********************')
				print()


				if pricepoint_type in [501, 502, 503, 504, 506, 510, 511] and one_click_pos:
					one_click_pos_record = web_module.one_click('pos', eticket, pricepoint_type, multitrans_base_record,
                                                                transaction_record['email'], url_options, selected_options)
					differences_oneclick_pos = mt.multitrans_compare(one_click_pos_record[0], one_click_pos_record[1])
					asset_base_record_onelick = asset.asset_oneclick(merchantbillconfig[0], asset_base_record,
					                                                 one_click_pos_record[1])
					differences_asset = asset.asset_compare(asset_base_record_onelick)
					check_email = emails.check_email_que(pricepoint_type, multitrans_base_record, 'signup')
					report['pos' + str(eticket)] = [differences_multitrans, differences_asset, check_email]
					postback_service.verify_postback_url("SignUp", packageid, one_click_pos_record[1][0]['TransID'])
					transids.append(one_click_pos_record[1][0]['TransID'])
					if pricepoint_type in [501, 505, 506, 511]:
						rebills_pids.append(one_click_pos_record[1][0]['PurchaseID'])
					print('*********************OneClick POS Transaction Verification Complete*********************')
					print()
				if pricepoint_type in [501, 502, 503, 504, 506, 510, 511] and one_click_ws:
					one_click_ws_record = web_module.one_click('ws', eticket, pricepoint_type, multitrans_base_record,
                                                               transaction_record['email'], url_options, selected_options)
					differences_oneclick_ws = mt.multitrans_compare(one_click_ws_record[0], one_click_ws_record[1])
					asset_base_record_onelick = asset.asset_oneclick(merchantbillconfig[0], asset_base_record,
					                                                 one_click_ws_record[1])
					differences_asset = asset.asset_compare(asset_base_record_onelick)
					check_email = emails.check_email_que(pricepoint_type, one_click_ws_record[0], 'signup')
					postback_service.verify_postback_url("SignUp", packageid, one_click_ws_record[1][0]['TransID'])
					report['ws' + str(eticket)] = [differences_multitrans, differences_asset, check_email]
					transids.append(one_click_ws_record[1][0]['TransID'])
					if pricepoint_type in [501, 505, 506, 511]:
						rebills_pids.append(one_click_ws_record[1][0]['PurchaseID'])
					print('*********************OneClick WS Transaction Verification Complete*********************')
					print()
				report[eticket] = [differences_multitrans, differences_asset, check_email_differences]

				if pricepoint_type == 506 and instant_coversion_pos:
					ic_pos_record = web_module.instant_conversion('pos', eticket, pricepoint_type, multitrans_base_record,
                                                                  transaction_record['email'], url_options,
                                                                  merchantbillconfig[0])
					differences_ic_pos = mt.multitrans_compare(ic_pos_record[0], ic_pos_record[1])
					asset_ic_record = asset.asset_instant_conversion(merchantbillconfig[0], asset_base_record,
					                                                 ic_pos_record[1])
					differences_asset = asset.asset_compare(asset_ic_record)
					check_email = emails.check_email_que(pricepoint_type, ic_pos_record[1][0], 'signup')
					#postback_service.verify_postback_url("SignUp", packageid, ic_pos_record[1]['TransID'])
					transids.append(ic_pos_record[1][0]['TransID'])
					rebills_pids.append(ic_pos_record[1][0]['PurchaseID'])
					report['pos' + str(eticket)] = [differences_ic_pos, differences_asset, check_email]
					print('*********************Instant Conversion Transaction Verification Complete*********************')
					print()

			except Exception as ex:
				print(ex)
		# --------------------------------------------------------------------------------------------------------------BEP
		# x = bep.process_captures()
		# d = bep.process_refund(transids)
		# f = bep.process_rebills(rebills_pids)


		# --------------------------------------------------------------------------------------------------------------BEP

	except Exception as ex:
		print(ex)
web_module.browser_quit()
