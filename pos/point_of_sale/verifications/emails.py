from db_functions import dbs
from termcolor import colored


def check_email_que(pricepoint_type, multitrans_base_record, action):
	transid = 0
	check_email = 99
	if pricepoint_type == 505:
		transid = multitrans_base_record['RelatedTransID']
	else:
		transid = multitrans_base_record['TransID']

	check_email = dbs.check_email_que(transid)
	if check_email == 'noemail':
		return "Could not find the email or error"
	else:
		check_email = check_email[0]
	if action == 'signup':
		if check_email['Status'] == 863 and check_email['EmailTypeID'] == 981:
			print(colored(f"Email is in que => Correct", 'green'))
			return "Email is in que => Correct"
		elif check_email['Status'] == 861 and check_email['EmailTypeID'] == 981:
			print(colored(f"Warning - Email is in que but status is not completed (861) => Recheck for Status", 'blue'))
			return "Warning - Email is in que but status is not completed (861) => Recheck for Status"
		else:
			return "Could not find the email or error"

# multitrans_base_record['RelatedTransID']


# if check_email == 1:
#     print(colored(f"Email is in que => Correct", 'green'))
# elif check_email == 2:
#     print(colored(f"Warning - Email is in que but status not completed => Need longer time", 'blue'))
# else:
#     print(colored(f"Email is not in the que or something wrong  => Check Data mannualy", 'red'))
# print('**************************************************************************************')
