import requests
import json



postpay_auth_url = 'https://qatrans.segpay.com/PostPay/PostPayAuth/'
postpay_capt_url = 'https://qatrans.segpay.com/PostPay/PostPayCapture/'

#auth
amnt= 4.95
data = {'eticketid'  : '900:27004', 'purchaseid' : 200564381, 'amount' : amnt,  'userdata1': '','userdata2' : '','website': 'qatest'}
r = requests.post(postpay_auth_url, data)
str=r.text
d = json.loads(str)
transid =d['TransactionId']


print (r.text)

#capture

data = {'eticketid'  : '900:27004', 'purchaseid' : 200564381, 'transactionId' : transid, 'amount' : amnt,  'userdata1': '','userdata2' : '','website': 'qatest'}
r = requests.post(postpay_capt_url, data)
print (r.text)


#200564409

