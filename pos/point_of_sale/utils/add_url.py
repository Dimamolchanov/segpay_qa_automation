import requests
from xml.etree.ElementTree import fromstring


add_merchant_url = 'https://qasrs.segpay.com/MerchantServices/merchant-urls'#?test=true'
# m 21621 user qa pass qateam    27001 yan , yan
login = 'yan'
password = 'yan3sdfsdfsdfsdfsdfsdfsdf'
authentication = (login, password)

data = {
    "BaseApprovedId": "20000095",
    "Url"         : "https://somedomainname.com",
    "UserName"    : "yan232",
    "Password"    : "yan123",
    "AccessNotes" : "Some text",
    "SupportEmail": "yan@segpay.com",
    "TechEmail"   : "yan@segpay.com",
    "FaqLink"     : "https://really.com",
    "HelpLink"    : "",
}



for i in range(6):
    #data['Url'] = f"https://testingdomains{i}.us"
    data['Url'] = f"https://workfromhome.ru/test{i+1}"
    response = requests.post(add_merchant_url, data, auth=authentication)
    print(response.text)





