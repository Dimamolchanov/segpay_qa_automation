from pos.point_of_sale.verifications import postback_service

#from pos.point_of_sale import transactions

merchant_id = 20004
package_id = 192304
trans_id = 1234636864
#1234634800
postback_service.verify_postback_url("SignUp", package_id, trans_id)
some_changes = 'test repo'

#service.parse_post_back_url(constants.POST_BACK_URL)
#logging.basicConfig(level=logging.INFO)
#logging.info('dasda')

