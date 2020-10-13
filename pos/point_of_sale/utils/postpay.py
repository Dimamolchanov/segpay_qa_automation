import requests
import json



postpay_auth_url = 'https://qatrans.segpay.com/PostPay/PostPayAuth/'
postpay_capt_url = 'https://qatrans.segpay.com/PostPay/PostPayCapture/'

#auth
amnt= 2.95
data = {'eticketid'  : '800:100161', 'purchaseid' : 200518860, 'amount' : amnt,  'userdata1': '','userdata2' : '','website': 'qatest'}
r = requests.post(postpay_auth_url, data)
str=r.text
d = json.loads(str)
transid =d['TransactionId']


print (r.text)

#capture

data = {'eticketid'  : '800:100161', 'purchaseid' : 200518860, 'transactionId' : transid, 'amount' : amnt,  'userdata1': '','userdata2' : '','website': 'qatest'}
r = requests.post(postpay_capt_url, data)
print (r.text)

