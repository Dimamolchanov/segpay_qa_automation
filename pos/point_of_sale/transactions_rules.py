import pymssql



server = "STGDB1\STG3DB1"
user = "SPStaff"
password = 'Toccata200e'


def refund_task(tasktype,tid):
	taskid = "0"
	taskype = tasktype #"842"  # 843 refund only, 842 RC, 841 RE
	transid = tid
	reasonode = "825"
	enteredy = "automation"
	comment = "snowflakes"
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql = f"Exec CS_Refund_Tasks_Insert {taskid},{taskype} ,{transid},{reasonode},{enteredy},{comment}"
	#print(sql)
	cursor.execute(sql)
	conn.commit()
	conn.close()

tid = 1234634281
tasktype = 841
x = refund_task(tasktype,tid)
z=5






transaction_type = ''
transsource = ''
transtype = ''

#sql = f"select TransType, TransSource from multitrans where TransID ={transid}"

sql = "exec BEP_InsertFraudScrubCompletion 1,'07/11/2019','NotMe'"

conn = pymssql.connect(server, user, password, "SP_Data")
cursor = conn.cursor(as_dict=True)
#cursor.callproc('BEP_InsertFraudScrubCompletion', ('1','07-11-2019','automation',))
cursor.execute(sql)
conn.commit()
conn.close()



rows = cursor.fetchall()
for row in rows:
	transsource = row['TransSource']
	transtype = row['TransType']
conn.close()


if transtype == 101  and transsource == 121:
	transaction_type = 'SignUp'
elif transtype == 101 and transsource == 122:
	transaction_type = 'Conversion'
elif transtype == 108 and transsource == 122:
	transaction_type = 'InstantConversion'
elif transtype == 105 and transsource == 121:
	transaction_type = 'AuthDelayCaptureSignUp'
elif transtype == 105 and transsource == 122:
	transaction_type = 'DelayCaptureSignUp'
elif transtype == 101 and transsource == 123:
	transaction_type = 'Rebill'
elif (transtype == 1011 and transsource == 121) or (transtype == 1011 and transsource == 123):
	transaction_type = 'OneClick'
elif transtype == 102 and transsource == 125:
	transaction_type = 'Refund'
elif transtype == 103 and transsource == 125:
	transaction_type = 'ChargeBack'
elif transtype == 107 and transsource == 125:
	transaction_type = 'Void'
elif transtype == 104 and transsource == 125:
	transaction_type = 'Revoke'
elif transtype == 1012 and transsource == 121:
	transaction_type = 'AuthCardUpdater'
elif transtype == 1012 and transsource == 123:
	transaction_type = 'AuthCardUpdaterRebiller'
elif transtype == 1013 and transsource == 125:
	transaction_type = 'VoideCardUpdater'
elif transtype == 1014 and transsource == 126:
	transaction_type = 'PostPayAuth'
elif transtype == 1015 and transsource == 126:
	transaction_type = 'PostPayCapture'

print(transaction_type)



z=3
