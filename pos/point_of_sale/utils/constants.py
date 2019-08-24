#----------------------------------------Postbacks---------------------------------------
POST_BACK_TYPES_FROM_CONFIG = 'select * from PostbackConfigs where PBCID = (select PostBackID from package where PackageID = {}) and PostbackURL <>\'\''
POST_BACK_TYPES_FROM_NOTIFICATION = 'select * from PostBackNotifications where TransID = {}'
#COLLECT_USER_INFO_BY_PACKAGE = 'select CollectUserInfo from MerchantBillConfig where BillConfigID = (select BillConfigID from PackageDetail where PackageID = {})'
COLLECT_USER_INFO_BILLCONFIG_ID = 'select CollectUserInfo from MerchantBillConfig where BillConfigID = {})'
POST_BACK_CINFIG_URL_BY_ID = 'select PostbackURL from PostbackConfigs where ID = {}'
POST_BACK_NOTIF_URL_BY_ID = 'select PostData from PostBackNotifications where TransID = {} and PostbackConfigID = {}'
POST_BACK_TYPE_BY_POSTBACK_ID = 'select PostbackType from PostBackNotifications where PostbackConfigID = {}'
PAYMENT_ACCT_ID = "select value from multitransvalues where transid = {} and name = 'PAYMENTACCOUNTID'"
POSTBACK_STATUS_BI_ID = 'select status from PostBackNotifications where PostbackConfigID = {} and transID = {}'
POS_OR_SERVICE_TRANS_SOURCE = "select * from MultiTransValues where transid = {} and name = 'POSSOURCE'"
FRAUD_CARD_CHECK = "select * from Fraud_TestCards where TestCard = '{}'"
FRAUD_CARD_INSERT = "insert into Fraud_TestCards values ('{}', 'card inserted with auto script', 'auto', '2018-07-01 13:16:12.063')"
GET_PAYMENTACCT_FROM_ASSET = 'select dbo.DecryptCard(PaymentAcct)  as cc from Assets where PurchaseID = {} '

#----------------------------------------Multitrans---------------------------------------
GET_DATA_FROM_MULTITRANS_BY_TRANS_ID = 'select * from multitrans where TransID = {}'
GET_DATA_FROM_ASSETS_BY_TRANS_ID = 'select * from Assets where PurchaseID = (select PurchaseID from multitrans where TransID = {})'
GET_DATA_FROM_ASSETS_BY_PURCHASE_ID = 'select * from Assets where PurchaseID = (select PurchaseID {})'
GET_DATA_FROM_MULTITRANS_BY_RELATED_TRANS_ID = 'select * from multitrans where TransID = (select RelatedTransID from multitrans where transId = {})'
GET_DATA_FROM_TASKS = 'select * from tasks where TransID = {}'
GET_COUNT_OF_REBILLS_FROM_MULTITRANS = 'select count(txstatus) as txstatus  from multitrans where transID ={} and txstatus = 6'
IS_3DSAUTHENTICATED = "select * from Cardinal3dsRequests where TransGuid = '{}'"
#GET_DATA_FROM_3D_SECURE_CONFIG = 'select top 1 * from [MerchantCC3DSecureConfig] where merchantid = {} and segpayprocessorid = (select top 1 ProcessorID from ProcessorPoolsDetail where  ppid = ( select  PrefProcessorID from package where packageid = {}))'
GET_DATA_FROM_3D_SECURE_CONFIG = 'select top 1 * from [CardinalMerchantConfigurations] where merchantid = {} and ProcessorId = (select top 1 ProcessorID from ProcessorPoolsDetail where  ppid = ( select  PrefProcessorID from package where packageid = {}))'
GET_DATA_FROM_GLOBALBINDETAILS = "select * from Globalbindatabasedetail where bin9 = '{}'"
GET_DATA_FROM_MERCHANT_EXTENSION = 'select VISARegion from Merchants_Extension where merchantid = {}'
