from pos.point_of_sale import config
from os import getenv
import pymssql
import time
from datetime import datetime

server = ''
if config.enviroment == 'stage':
	server = "STGDB1"
elif config.enviroment == 'qa':
	server = "QADB1"
elif config.enviroment == 'stage2':
	server = "DEVSQL2\stg2db1"

user = "SPStaff"
password = 'Toccata200e'


def db_cursor():
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	return cursor


def update_processor(processor, package):
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = f'UPDATE Package set PrefProcessorID = {processor} where PackageID = {package}'
	cursor.execute(sql)
	conn.commit()
	conn.close()

def update_merchantbillconfig_oneclick(pricepointid, enabled):
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = f'UPDATE MerchantBillConfig set OneClickEnabled = {enabled} where billconfigid = {pricepointid}'
	cursor.execute(sql)
	conn.commit()
	conn.close()



def update_pp_singleuse_promo(pricepointid, featureid, enabled):
	sql = f"Select * from pricepointfeaturedetail where pricepointid = {pricepointid} and featureid = {featureid} "

	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	while retry_flag and retry_count < 3:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				sql = f"UPDATE pricepointfeaturedetail set enabled = {enabled} where pricepointid = {pricepointid} and featureid = {featureid}"
				# print(sql)
				cursor.execute(sql)
				conn.commit()
				retry_flag = False
				conn.close()

			else:
				retry_count = retry_count + 1

		# rows = cursor.fetchall()
		except Exception  as ex:
			print(ex)
			print("Module dbs function update_pp_singleuse_promo")
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def update_package(package, merchantid, billconfigid):
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = f'Delete from PackageDetail where packageid = {package}'
	cursor.execute(sql)
	conn.commit()
	cursor.callproc('MP_PackageDetail_Update', (package, merchantid, billconfigid, '2018-06-04 17:39:45.887', 'autotester', 1))
	conn.commit()
	sql = f"Update package set MerchantID = {merchantid} where PackageID = {package}"
	cursor.execute(sql)
	conn.commit()
	conn.close()


def multitrans_val(transguid):
	transid = 0;
	purchaseid = 0
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = "select PurchaseID,TransID from multitrans where transguid ='" + transguid + "'"
	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				row = ''
				for row in rows:
					transid = row['TransID']
					purchaseid = row['PurchaseID']
				conn.close()
				return [transid, purchaseid]
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def multitrans_full_record(transid, transguid, purchaseid):
	sql = ''
	if transid != '':
		sql = f"select * from multitrans where TransID ={transid}"
	elif transguid != '':
		sql = f"select * from multitrans where TransGuid ='{transguid}'"
	else:
		sql = f"select * from multitrans where PurchaseID ={purchaseid}"

	retry_flag = True
	retry_count = 0

	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False

				conn.close()
				return rows
			else:
				retry_count = retry_count + 1
				time.sleep(1)
		except Exception as ex:
			print(ex)
			print("Module DBS => Function: multitrans_full_record(transid, transguid, purchaseid)")
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def asset_full_record(purchaseid):
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = "select * from Assets where PurchaseID ='" + str(purchaseid) + "'"
	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False

				conn.close()
				return rows
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def merchantbillconfig(billconfigid):
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = f"select * from merchantbillconfig where billconfigid = {billconfigid}"
	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				# row = ''
				# for row in rows:
				#     for key,value in row.items():
				#         print (key , ":" , value)
				conn.close()
				return rows
		except Exception as ex:
			print(ex)
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def package(package):
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = "select * from package where packageid = '" + str(package) + "'"
	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				# row = ''
				# for row in rows:
				#     for key,value in row.items():
				#         print (key , ":" , value)
				conn.close()
				return rows
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def exc_rate(currency, billconfig_currency):
	exchange_rate = ''
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = (
		f"SELECT TOP 1 [Rate] FROM [sp_data].[dbo].[ExchangeRates] where ConsumerIso = '{currency}' and   MerchantIso = '{billconfig_currency}' order by importdatetime desc")

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				row = ''
				for row in rows:
					exchange_rate = row['Rate']

				conn.close()
				return exchange_rate
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def url(urlid):
	domain = ''
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = (f"select Domain from Merchant_URL where urlid ={urlid}")

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				row = ''
				for row in rows:
					domain = row['Domain']

				conn.close()
				return domain
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def encrypt_email(email):
	email_encrypted = ''
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = (f"select dbo.EncryptEMail('{email}') as email")

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				row = ''
				for row in rows:
					email_encrypted = row['email']

				conn.close()
				return email_encrypted
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def encrypt_card(cc):
	card_encrypted = ''
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = (f"select dbo.EncryptCard('{cc}') as card")

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				row = ''
				for row in rows:
					card_encrypted = row['card']

				conn.close()
				return card_encrypted
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def encrypt_string(str):
	string_encrypted = ''
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = (f"select dbo.EncryptString('{str}') as string_encrypted")

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				row = ''
				for row in rows:
					string_encrypted = row['string_encrypted']

				conn.close()
				return string_encrypted
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def check_email_que(transid):
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = (f"SELECT * FROM [sp_data].[dbo].[PointOfSaleEmailQueue] where [DateQueued] > '{datetime.now().date()}' and EmailParameters like '%{str(transid)}%'")

	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			# retry_count = retry_count + 1
			# time.sleep(1)
			if len(rows) > 0:
				retry_flag = False
				# row = ''
				# for row in rows:
				#     email_que = row['Domain']
				conn.close()
				return rows
			else:
				retry_count = retry_count + 1
				time.sleep(1)



		except Exception as ex:

			print(ex)
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)
	return 'noemail'


def sql(sql):
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	try:
		cursor.execute(sql)
		rows = cursor.fetchall()
		if len(rows) > 0:
			retry_flag = False
			conn.close()
			return rows
		else:
			retry_count = retry_count + 1
			time.sleep(1)
	except Exception as ex:

		print(ex)
		print("Retry after 1 sec")
		retry_count = retry_count + 1
		time.sleep(2)


def get_pricingguid(merchantid, type):
	pricingguid = ''
	initial_price = ''
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = f"select top 1 * from PricingGuids where MerchantID ={merchantid} and pricepointtype = {type} "  # PricingGuid, InitialPrice
	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				# row = ''
				# for row in rows:
				#     pricingguid = row['PricingGuid']
				#     initial_price = row ['InitialPrice']
				conn.close()
				return rows
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def pricepoint_list(merchantid):
	pp_list = []
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = "select billconfigid from merchantbillconfig where merchantid = '" + str(merchantid) + "'"
	while retry_flag and retry_count < 30:
		try:
			cursor.execute(sql)
			rows = cursor.fetchall()
			if len(rows) > 0:
				retry_flag = False
				for pp in rows:
					pp_list.append(pp['billconfigid'])

				# row = ''
				# for row in rows:
				#     for key,value in row.items():
				#         print (key , ":" , value)
				conn.close()
				return pp_list
		except:
			print("Retry after 1 sec")
			retry_count = retry_count + 1
			time.sleep(2)


def pricepoint_type(merchantid, type):
	retry_flag = True
	retry_count = 0
	pricepoint_type_list = []
	rows = ''
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)

	while retry_flag and retry_count < 30:
		for pricepoint_type in type:
			# sql = "select billconfigid from merchantbillconfig where merchantid = '" + str(merchantid) + "'"
			sql = f"select top 1 BillConfigID  from MerchantBillConfig where merchantid ={merchantid} and type = {pricepoint_type}  "
			try:
				cursor.execute(sql)
				rows = cursor.fetchall()
				if len(rows) > 0:
					retry_flag = False
					pp_type = rows[0]['BillConfigID']
					pricepoint_type_list.append(pp_type)
			except:
				print("Retry after 1 sec")
				retry_count = retry_count + 1
				time.sleep(2)
		conn.close()
		return pricepoint_type_list
