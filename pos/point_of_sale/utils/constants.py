#----------------------------------------Postbacks---------------------------------------
POST_BACK_TYPES_FROM_CONFIG = 'select * from PostbackConfigs where PBCID = (select PostBackID from package where PackageID = {}) and PostbackURL <>\'\''
POST_BACK_TYPES_FROM_NOTIFICATION = 'select * from PostBackNotifications where TransID = {}'
COLLECT_USER_INFO_BY_PACKAGE = 'select CollectUserInfo from MerchantBillConfig where BillConfigID = (select BillConfigID from PackageDetail where PackageID = {})'
POST_BACK_CINFIG_URL_BY_ID = 'select PostbackURL from PostbackConfigs where ID = {}'
POST_BACK_NOTIF_URL_BY_ID = 'select PostData from PostBackNotifications where TransID = {} and PostbackConfigID = {}'
POST_BACK_TYPE_BY_POSTBACK_ID = 'select PostbackType from PostBackNotifications where PostbackConfigID = {}'
PAYMENT_ACCT_ID = "select value from multitransvalues where transid = {} and name = 'PAYMENTACCOUNTID'"
POSTBACK_STATUS_BI_ID = 'select status from PostBackNotifications where PostbackConfigID = {} and transID = {}'
POS_OR_SERVICE_TRANS_SOURCE = "select * from MultiTransValues where transid = {} and name = 'POSSOURCE'"
FRAUD_CARD_CHECK = "select * from Fraud_TestCards where TestCard = '{}'"
FRAUD_CARD_INSERT = "insert into Fraud_TestCards values ('{}', 'card inserted with auto script', 'auto', '2018-07-01 13:16:12.063')"

#----------------------------------------Multitrans---------------------------------------
GET_DATA_FROM_MULTITRANS_BY_TRANS_ID = 'select * from multitrans where TransID = {}'
GET_DATA_FROM_ASSETS_BY_TRANS_ID = 'select * from Assets where PurchaseID = (select PurchaseID from multitrans where TransID = {})'