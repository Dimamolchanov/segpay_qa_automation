enviroment = 'stage'
url = ''
urlws = ''
urlic = ''
urlicws = ''
refund_url = ''
rebill_url = ''
captures_url = ''
server = ''
# provide merchant ID
merchants = [20004]
# type - for type select on run, list - for all PPs, billConfig ID(e.g. 100140) - for single PP type
pricepoints = [27165]
#Processeor ID
processors = [26]
#PAckage ID
packageid = 192303
template = ''  # '&template=defaultnopaypal'
report = {}
available_currencies = ['USD']#,"AUD"]#,"CHF",  "EUR", "GBP", "HKD",]# "JPY", "NOK", "SEK","DKK"] # "DKK",
available_languages = ['EN']#,'ES', "PT", "IT", "FR", "DE", "NL", "EL", "RU", "SK", "SL", "JA", "ZS", "ZH"]
oc_list = [501, 502, 503, 504, 506, 510, 511]
#Global Objects to transfer data from test to test
transaction_records = []
test_data = {}
transids = []
cc_number=''

one_click_pos = False
one_click_ws = True
instant_coversion_pos = False
instant_coversion_ws = False
#1 - TRUE, 0 - FALSE - to DO refactor
single_use_promo = 0




if enviroment == 'stage':
   server = "STGDB1"
   url = 'https://stgs2.segpay.com/billing/poset.cgi?x-eticketid=' # POS and 1 Click
   urlws = 'https://stgsvc.segpay.com/OneClickSales.asmx/SalesService?eticketid=' # 1 click service
   urlic = 'https://stgs2.segpay.com/billing/InstantConv.aspx?ICToken='   # Instant Conversion POS
   urlicws = 'https://stgsvc.segpay.com/ICService.asmx/InstantConversionService?ICToken=' # Instant Conversion service
   refund_url = 'http://stgbep1:54908/jobs/execute/tasks'
   rebill_url = 'http://stgbep1:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
   captures_url = 'http://stgbep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates=' # 2019-07-07
elif enviroment == 'qa':
   server = "QADB1"
   url = 'https://qas2.segpay.com/billing/poset.cgi?x-eticketid=' # POS and 1 Click
   urlws = 'https://qasvc.segpay.com/OneClickSales.asmx/SalesService?eticketid=' # 1 click service
   urlic = 'https://qas2.segpay.com/billing/InstantConv.aspx?ICToken='   # Instant Conversion POS
   urlicws = 'https://qasvc.segpay.com/ICService.asmx/InstantConversionService?ICToken=' # Instant Conversion service
   refund_url = 'http://qabep1:54908/jobs/execute/tasks'
   rebill_url = 'http://qabep1p:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
   captures_url = 'http://qabep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates=' # 2019-07-07
elif enviroment == 'stage2':
   server = "DEVSQL2\stg2db1"
   url = 'https://stg2s2.segpay.com/billing/poset.cgi?x-eticketid=' # POS and 1 Click
   urlws = 'https://stg2svc.segpay.com/OneClickSales.asmx/SalesService?eticketid=' # 1 click service
   urlic = 'https://stg2s2.segpay.com/billing/InstantConv.aspx?ICToken='   # Instant Conversion POS
   urlicws = 'https://stg2svc.segpay.com/ICService.asmx/InstantConversionService?ICToken=' # Instant Conversion service
   refund_url = 'http://stg2bep:54908/jobs/execute/tasks'
   rebill_url = 'http://stg2bep:54908/jobs/execute/rebills?Time='  # time format 2019-07-10%2023:59:59
   captures_url = 'http://stg2bep1:54908/jobs/execute/captures?SkipTimeValidation=true&IgnoreFraudScrub=true&Dates=' # 2019-07-07
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
