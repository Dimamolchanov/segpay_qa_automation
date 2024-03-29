from datetime import datetime
import logging

start_time = datetime.now()
tmp = str(start_time).split(' ')
tmp = tmp[0] + tmp[1].replace(':', '_')
file_name = 'C:\segpay_qa_automation\\test_run_' + tmp + '.log'
# logging.basicConfig(filename=file_name, level=logging.INFO)

enviroment = 'stage'
url = ''
urlws = ''
urlic = ''
urlicws = ''
refund_url = ''
rebill_url = ''
captures_url = ''
server = ''
# test_data = {'eticket': 'test'}
# us merchant 21621   ppid 74 package 192060 pricepoints  27042,27041, 27064 - ic,27187 - recurring [27042,27041,27187]
# stage packages 192192,99,192195 eu


scenarios = []
test_case = {}
test_cases = {}
initial_data = {
	'traceback': True,
	'eu_processors': 65,
	'us_processors': 74,
	'us_available_currencies': ['USD'],
	'eu_available_currencies': ['USD'],#, 'CHF', 'AUD', 'CAD','EUR'],
	'processor': 0
}
test_data = {'eticket': ''}

packages = [99,901,902,903] # [900,901,902,903,800,801,802,803]#,192261,192195,192059,192204,192046,192048]#192060, 99,192059,192041,192046,192133]
pricepoints_options = 'single'
available_languages = ['EN']  # ,'ES']#,'ES', "PT"]#, "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]
template = ''  # '&template=defaultpsd2'  # '&template=defaultnopaypal'  default
report = {}

# Global Objects to transfer data from test to test
transaction_records = []
results = ['none', 'none']
refunds = []
tasks_type = {}
asset_reactivated = {}
mt_reactivated = {}
oc_tokens = {}
cnt = 0
sql_dict = {}

# random_cards = ['4000000000001083', '4000000000001083'
#                 , '4000000000001091']
random_cards = ['4000000000001018','4000000000001018']

# random_cards = ['4000000000001000', '4000000000001018', '4000000000001026', '4000000000001034', '4000000000001042', '4000000000001059', '4000000000001067',
#                 '4000000000001075', '4000000000001083', '4000000000001091', '4000000000001109', '4444333322221111', '5432768030017007', '4916280519180429', '4496046701292555']

transids = []
#cc_number = '4000000000001091'  # '4000000000001109' # '4444333322221111' prepaid 5432768030017007
transids_for_oc = [1234643195]
cards_3ds = {
	"4000000000001000": {"card": "4000000000001000", 'Enrolled': 'Y', 'PAResStatus': 'Y', 'SignatureVerification': 'Y', 'Cavv': '<Cavv value>', 'EciFlag': '05', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001018": {"card": "4000000000001018", 'Enrolled': 'Y', 'PAResStatus': 'N', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001026": {"card": "4000000000001026", 'Enrolled': 'Y', 'PAResStatus': 'A', 'SignatureVerification': 'Y', 'Cavv': '<value>', 'EciFlag': '06', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001034": {"card": "4000000000001034", 'Enrolled': 'Y', 'PAResStatus': 'U', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001042": {"card": "4000000000001042", 'Enrolled': 'Y', 'PAResStatus': 'R', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001059": {"card": "4000000000001059", 'Enrolled': 'U', 'PAResStatus': '', 'SignatureVerification': '', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001067": {"card": "4000000000001067", 'Enrolled': 'U', 'PAResStatus': '', 'SignatureVerification': '', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '1001', 'ErrorDesc': 'Error Processing Message Request', 'cmpi_authenticate response': 'NO'},
	"4000000000001075": {"card": "4000000000001075", 'Enrolled': 'U', 'PAResStatus': '', 'SignatureVerification': '', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': {}, 'cmpi_authenticate response': 'NO'},
	"4000000000001083": {"card": "4000000000001083", 'Enrolled': 'B', 'PAResStatus': '', 'SignatureVerification': '', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '', 'Payload': '', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'NO'},
	"4000000000001091": {"card": "4000000000001091", 'Enrolled': 'Y', 'PAResStatus': 'C', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': '<value>', 'Payload': '<value>', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'YES', 'cPAResStatus': 'Y',
	                     'cSignatureVerification': 'Y', 'cCavv': '<value>', 'cEciFlag': '05', 'cErrorNo': 0, 'cErrorDesc': ''},
	"4000000000001109": {"card": "4000000000001109", 'Enrolled': 'Y', 'PAResStatus': 'C', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '<value>', 'ACSUrl': '<value>', 'Payload': '<value>', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'YES', 'cPAResStatus': 'N',
	                     'cSignatureVerification': 'Y', 'cCavv': '', 'cEciFlag': '07', 'cErrorNo': 0, 'cErrorDesc': ''},
	"4000000000001117": {"card": "4000000000001117", 'Enrolled': 'Y', 'PAResStatus': 'C', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '<value>', 'ACSUrl': '<value>', 'Payload': '<value>', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'YES', 'cPAResStatus': 'U',
	                     'cSignatureVerification': 'Y', 'cCavv': '', 'cEciFlag': '07', 'cErrorNo': 0, 'cErrorDesc': ''},
	"4000000000001125": {"card": "4000000000001125", 'Enrolled': 'Y', 'PAResStatus': 'C', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '<value>', 'ACSUrl': '<value>', 'Payload': '<value>', 'ErrorNo': '0', 'ErrorDesc': '', 'cmpi_authenticate response': 'YES', 'cPAResStatus': 'U',
	                     'cSignatureVerification': 'Y', 'cCavv': '', 'cEciFlag': '', 'cErrorNo': '<value>', 'cErrorDesc': '<value>'},
	"4000000000001133": {"card": "4000000000001133", 'Enrolled': 'Y', 'PAResStatus': 'C', 'SignatureVerification': 'Y', 'Cavv': '', 'EciFlag': '07', 'ACSUrl': 'https://0merchantacsstag.cardinalcommerce.com/MerchantACSWeb/creq.jsp', 'Payload': '<value>', 'ErrorNo': '0', 'ErrorDesc': '',
	                     'cmpi_authenticate response': 'YES', 'cPAResStatus': 'B', 'cSignatureVerification': 'Y', 'cCavv': '', 'cEciFlag': '<value>', 'cErrorNo': 0, 'cErrorDesc': ''},
	# "4000000000001141":{"card": "4000000000001141",'Enrolled' : 'Y','PAResStatus' : 'Y','SignatureVerification' : 'Y','Cavv' : '<value>','EciFlag' : '07','ACSUrl' : '','Payload' : '', 'ErrorNo' : '0', 'ErrorDesc' : '','cmpi_authenticate response' : 'NO'},
	# "4000000000002008":{"card": "4000000000002008",'Enrolled' : 'Y','PAResStatus' : 'C','SignatureVerification' : 'Y','Cavv' : '','EciFlag' : '07','ACSUrl' : 'https://0merchantacsstag.cardinalcommerce.com/MerchantACSWeb/creq.jsp','Payload' : '<value>', 'ErrorNo' : '0', 'ErrorDesc' : '','cmpi_authenticate response' : 'YES','cPAResStatus' : 'Y','cSignatureVerification' : 'Y','whiteListStatus':'Y','whiteListStatusSource' : '<value>','cCavv' : '<value>','cEciFlag' : '<value>','cErrorNo' : 0, 'cErrorDesc' : ''},
	# "4000000000002016":{"card": "4000000000002016",'Enrolled' : 'Y','PAResStatus' : 'Y','SignatureVerification' : 'Y','WhiteListStatus':'Y','Cavv' : '<value>','EciFlag' : '05','WhiteListStatusSource' : '03','ACSUrl' : '','Payload' : '', 'ErrorNo' : '0', 'ErrorDesc' : '','cmpi_authenticate response' : 'NO'},
	# "4000000000002024":{"card": "4000000000002024",'Enrolled' : 'Y','PAResStatus' : 'I','SignatureVerification' : 'Y','Cavv' : '<value>','EciFlag' : '07','ACSUrl' : '','Payload' : '', 'ErrorNo' : '0', 'ErrorDesc' : '','cmpi_authenticate response' : 'NO'}
}

one_click_pos = False
one_click_ws = False
instant_coversion_pos = False
instant_coversion_ws = False
# 1 - TRUE, 0 - FALSE - to DO refactor
single_use_promo = 1
# visa_secure = True


if enviroment == 'stage':
	server = "STGDB1"
	url = 'https://stgs2.segpay.com/billing/poset.cgi?x-eticketid='  # POS and 1 Click
	urlws = 'https://stgsvc.segpay.com/OneClickSales.asmx/SalesService?eticketid='  # 1 click service
	urlic = 'https://stgs2.segpay.com/billing/InstantConv.aspx?ICToken='  # Instant Conversion POS
	urlicws = 'https://stgsvc.segpay.com/ICService.asmx/InstantConversionService?ICToken='  # Instant Conversion service
	refund_url = 'http://stgbep1:54908/jobs/execute/tasks'
	rebill = 'http://stgbep1:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
	captures_url = 'http://stgbep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates='  # 2019-07-07
	reactivation_url = 'https://stgs2.segpay.com/reactivation?tguid='
elif enviroment == 'qa':
	server = "QADB1"
	url = 'https://qas2.segpay.com/billing/poset.cgi?x-eticketid='  # POS and 1 Click
	urlws = 'https://qasvc.segpay.com/OneClickSales.asmx/SalesService?eticketid='  # 1 click service
	urlic = 'https://qas2.segpay.com/billing/InstantConv.aspx?ICToken='  # Instant Conversion POS
	urlicws = 'https://qasvc.segpay.com/ICService.asmx/InstantConversionService?ICToken='  # Instant Conversion service
	refund_url = 'http://qabep1:54908/jobs/execute/tasks'
	rebill_url = 'http://qabep1:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
	captures_url = 'http://qabep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates='  # 2019
	reactivation_url = 'https://qas2.segpay.com/reactivation?tguid='  # -07-07
elif enviroment == 'stage2':
	server = "DEVSQL2\stg2db1"
	url = 'https://stg2s2.segpay.com/billing/poset.cgi?x-eticketid='  # POS and 1 Click
	urlws = 'https://stg2svc.segpay.com/OneClickSales.asmx/SalesService?eticketid='  # 1 click service
	urlic = 'https://stg2s2.segpay.com/billing/InstantConv.aspx?ICToken='  # Instant Conversion POS
	urlicws = 'https://stg2svc.segpay.com/ICService.asmx/InstantConversionService?ICToken='  # Instant Conversion service
	refund_url = 'http://stg2bep1:54908/jobs/execute/tasks'
	rebill_url = 'http://stg2bep1:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
	captures_url = 'http://stg2bep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates='  # 2019-07-07
	reactivation_url = 'https://stg2s2.segpay.com/reactivation?tguid='
elif enviroment == 'stage3':
	server = "STGDB1\STG3DB1"
	reactivation_url = 'https://stg3s2.segpay.com/reactivation?tguid='
	url = 'https://stg3s2.segpay.com/billing/poset.cgi?x-eticketid='  # POS and 1 Click
	urlws = 'https://stg3svc.segpay.com/OneClickSales.asmx/SalesService?eticketid='  # 1 click service
	urlic = 'https://stg3s2.segpay.com/billing/InstantConv.aspx?ICToken='  # Instant Conversion POS
	urlicws = 'https://stg3svc.segpay.com/ICService.asmx/InstantConversionService?ICToken='  # Instant Conversion service
	refund_url = 'http://stg3bep1:54908/jobs/execute/tasks'
	rebill_url = 'http://stg3bep1:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
	captures_url = 'http://stg3bep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates='  # 2019-07-07
