from termcolor import colored

from pos.point_of_sale.db_functions.dbactions import DBActions
from pos.point_of_sale.utils import options

db_agent = DBActions()

def check_email_status(transids):
	for transid in transids:
		check_email = db_agent.check_email_que(transid)
		if check_email:
			if check_email == 'noemail':
				return "Could not find the email or error"
			else:
				if check_email[0]['Status'] != 863 :
					print(colored(f"Warning - Email is in que but status is not completed (861) => Recheck for Status | TransID: {transid}", 'blue'))
					return "Warning - Email is in que but status is not completed (861) => Recheck for Status"



def check_email_que(pricepoint_type, multitrans_base_record, action):
	transid = 0
	check_email = 99
	if pricepoint_type == 505:
		transid = multitrans_base_record['RelatedTransID']
	else:
		transid = multitrans_base_record['TransID']

	check_email = db_agent.check_email_que(transid)
	if check_email == 'noemail':
		return "Could not find the email or error"
	else:
		check_email = check_email[0]
	if action == 'signup':
		if check_email['EmailTypeID'] == 981:
			options.append_list('Email      is in que       =>  Pass')
			print(colored(f"Email      is in que       =>  Pass", 'green'))
		else:
			options.append_list("Could not find the email or error")
			return "Could not find the email or error"
