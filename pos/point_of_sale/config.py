enviroment = 'qa'
url = ''
urlws = ''
urlic = ''
urlicws = ''
if enviroment == 'stage':
	url = 'https://stgs2.segpay.com/billing/poset.cgi?x-eticketid='
elif enviroment == 'qa':
	url = 'https://qas2.segpay.com/billing/poset.cgi?x-eticketid='
elif enviroment == 'stage2':
	url = 'https://stg2s2.segpay.com/billing/poset.cgi?x-eticketid='

if enviroment == 'stage':
	urlws = 'https://stgsvc.segpay.com/OneClickSales.asmx/SalesService?eticketid='
elif enviroment == 'qa':
	urlws = 'https://qasvc.segpay.com/OneClickSales.asmx/SalesService?eticketid='
elif enviroment == 'stage2':
	urlws = 'https://stg2svc.segpay.com/OneClickSales.asmx/SalesService?eticketid='


if enviroment == 'stage':
	urlic = 'https://stgs2.segpay.com/billing/InstantConv.aspx?ICToken='
elif enviroment == 'qa':
	urlic = 'https://qas2.segpay.com/billing/InstantConv.aspx?ICToken='
elif enviroment == 'stage2':
	urlic = 'https://stg2s2.segpay.com/billing/InstantConv.aspx?ICToken='




if enviroment == 'stage':
	urlicws = 'https://stgsvc.segpay.com/ICService.asmx/InstantConversionService?ICToken='
elif enviroment == 'qa':
	urlicws = 'https://qasvc.segpay.com/ICService.asmx/InstantConversionService?ICToken='
elif enviroment == 'stage2':
	urlicws = 'https://stg2svc.segpay.com/ICService.asmx/InstantConversionService?ICToken='






