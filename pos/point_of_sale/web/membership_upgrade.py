import requests
import json

upgrade_api = 'https://qa-api.segpay.com/purchases/200733466/upgrade'

data = {'newRecurringAmount' : '6.99',  'newRecurringDurationInDays': '30'}
r = requests.post(upgrade_api, data)
str_upgrade=r.text
print(str_upgrade)
#d = json.loads(str_upgrade)
z=3