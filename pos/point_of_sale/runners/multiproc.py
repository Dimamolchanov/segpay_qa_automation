import multiprocessing
from pos.point_of_sale.config import config
from  pos.point_of_sale.runners import runner
import threading







if __name__ == "__main__":


	config.merchant = 'EU'
	eu_merchant = threading.Thread(target=runner.start_test )
	config.merchant = 'EU'
	us_merchant = threading.Thread(target=runner.start_test )
