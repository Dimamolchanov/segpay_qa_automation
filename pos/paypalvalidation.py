import splinter
import random
import dbs
from splinter import Browser
from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-position=-1400,0")
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-position=-1400,0")

br = Browser(driver_name='chrome', options=chrome_options)

url = 'https://stgs2.segpay.com/billing/poset.cgi?x-eticketid=55:27003'

# url all , package all , paypal enabled
sql = "update MerchantCardTypeConfigurations set UrlId = 0,PackageId = 0 ,CardTypeCodeId = 1704, IsEnabled = 1 where merchantid = 27001"
dbs.sql(sql)







br.visit(url)
val = br.find_by_name('paymentoption').last.value
if val == str(1301):
    print ("URL = 0 , Package = 0 Enabled =>  paypal visible => ok")

sql = "update MerchantCardTypeConfigurations set UrlId = 0,PackageId = 55 ,CardTypeCodeId = 1704, IsEnabled = 1 where merchantid = 27001"
dbs.sql(sql)
br.reload()
val = br.find_by_name('paymentoption').last.value
if val == str(1301):
    print ("URL = 0 , Package = 55  Enabled =>  paypal visible => ok")

sql = "update MerchantCardTypeConfigurations set UrlId = 1,PackageId = 55 ,CardTypeCodeId = 1704, IsEnabled = 1 where merchantid = 27001"
dbs.sql(sql)
br.reload()
val = br.find_by_name('paymentoption').last.value
if val == str(1301):
    print ("URL = 1 , Package = 55  Enabled =>  paypal visible => wrong")
else:
    print("URL = 1 , Package = 55  Enabled =>  paypal not visible => correct")

sql = "update MerchantCardTypeConfigurations set UrlId = 26625,PackageId = 55 ,CardTypeCodeId = 1704, IsEnabled = 1 where merchantid = 27001"
dbs.sql(sql)
br.reload()
val = br.find_by_name('paymentoption').last.value
if val == str(1301):
    print ("URL = 26625 , Package = 55  Enabled =>  paypal visible => correct")
else:
    print("URL = 1 , Package = 55  Enabled =>  paypal not visible => wrong")

sql = "update MerchantCardTypeConfigurations set UrlId = 26625,PackageId = 123 ,CardTypeCodeId = 1704, IsEnabled = 1 where merchantid = 27001"
dbs.sql(sql)
br.reload()
val = br.find_by_name('paymentoption').last.value
if val == str(1301):
    print ("URL = 26625 , Package = 1232  Enabled =>  paypal visible => wrong")
else:
    print("URL = 1 , Package = 55  Enabled =>  paypal not visible => correct")



url = 'https://stgs2.segpay.com/billing/poset.cgi?x-eticketid=55:26625'
sql = "update MerchantCardTypeConfigurations set UrlId = 26625,PackageId = 123 ,CardTypeCodeId = 1704, IsEnabled = 1 where merchantid = 27001"
dbs.sql(sql)
br.reload()
val = br.find_by_name('paymentoption').last.value
if val == str(1301):
    print ("URL = 26864 , Package = 191959  Enabled =>  paypal visible => wrong")
else:
    print("URL = 1 , Package = 55  Enabled =>  paypal not visible => correct")




z= 9
br.quit()