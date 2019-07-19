from pos.point_of_sale.postbacks import postback_service

#from pos.point_of_sale import transactions

merchant_id = 20004
package_id = 192304
trans_id = 1234636864
#1234634800
postback_service.verify_postback_url("SignUp", package_id, trans_id)

#service.parse_post_back_url(constants.POST_BACK_URL)
#logging.basicConfig(level=logging.INFO)
#logging.info('dasda')

