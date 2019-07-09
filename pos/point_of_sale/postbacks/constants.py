POST_BACK_TYPES_FROM_CONFIG = 'select * from PostbackConfigs where PBCID = (select PostBackID from package where PackageID = {}) and PostbackURL <>\'\''
POST_BACK_TYPES_FROM_NOTIFICATION = 'select * from PostBackNotifications where TransID = {}'
COLLECT_USER_INFO_BY_PACKAGE = 'select CollectUserInfo from MerchantBillConfig where BillConfigID = (select BillConfigID from PackageDetail where PackageID = {})'
POST_BACK_CINFIG_URL_BY_ID = 'select PostbackURL from PostbackConfigs where ID = {}'
POST_BACK_NOTIF_URL_BY_ID = 'select PostData from PostBackNotifications where TransID = {} and PostbackConfigID = {}'
POST_BACK_TYPE_BY_POSTBACK_ID = 'select PostbackType from PostBackNotifications where PostbackConfigID = {}'
PAYMENT_ACCT_ID = "select value from multitransvalues where transid = {} and name = 'PAYMENTACCOUNTID'"
POSTBACK_STATUS_BI_ID = 'select status from PostBackNotifications where PostbackConfigID = {}'