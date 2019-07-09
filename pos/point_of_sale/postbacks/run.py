from pos.point_of_sale.postbacks import postback_service
from pos.point_of_sale.postbacks import constants
import logging

merchant_id = 20004
package_id = 270109
trans_id = 1534615290

postback_service.verify_postback_url("SignUp")
#service.parse_post_back_url(constants.POST_BACK_URL)
#service.get_post_back_config_url()
#service.get_post_back_notif_url()
#postbacks = service.find_post_backs_received(package_id, trans_id)
#logging.basicConfig(level=logging.INFO)
#logging.info('dasda')
#service.get_collect_user_info(package_id)
