import config
from os import getenv
import pymssql
import time
from datetime import datetime

server = 'stage2'
if config.enviroment == 'stage':
	server = "STGDB1"
elif config.enviroment == 'qa':
	server = "QADB1"
elif config.enviroment == 'stage2':
	server = "DEVSQL2\stg2db1"

user = "SPStaff"
password = 'Toccata200e'


def incert_merchant(merchantid):
	retry_flag = True
	retry_count = 0
	conn = pymssql.connect(server, user, password, "SP_Data")
	cursor = conn.cursor(as_dict=True)
	sql     = "SET IDENTITY_INSERT [dbo].[Merchants] ON "
	cursor.execute(sql)
	try:
		sql = "INSERT [dbo].[Merchants] ([MerchantID], [ContactEmail], [ContactFax], [ContactName], [ContactPhone], [ID1], [ID1Type], [ID2], [ID2Type], [IntecaMemberID], [MerchantAddress], [MerchantCity], [MerchantCountry], [MerchantName], [MerchantStateProv], [MerchantZipPostalCode], [ModBy], [OriginalDate], [PrincipalAddress], [PrincipalCity], [PrincipalCountry], [PrincipalEmail], [PrincipalName], [PrincipalPhone], [PrincipalStateProv], [PrincipalZipPostalCode], [ProcessingSince], [RateID], [Ref_ID], [SalesRepName], [Status], [StatusDate], [Type]) VALUES (#{merchantid}, N'qateam@segpay.com', N'8139447400', N'QA SegPay Automation', N'12312312313333333', N'123', 162, N'None', 161, 0, N'123 Main Lane SegPay', N'London ', N'GB', N'SegPayEU QA Automation ', N'--', N'12345678965676', N'qateam@segpay.com', CAST(N'2017-05-09 04:00:00.000' AS DateTime), N'123 Main Ln', N'London ', N'GB', N'test12@gmail.com', N'QA Team SegPay 999', N'8139447400', N'--', N'123456789', CAST(N'2017-05-09 00:00:00.000' AS DateTime), 301, N'SegPayEUMerchant', N'QAteam', 151, CAST(N'2018-01-17 15:26:04.687' AS DateTime), 143)"
		cursor.execute(sql)
		conn.commit()
		sql = "SET IDENTITY_INSERT [dbo].[Merchants] OFF "
		cursor.execute(sql)
	except Exception as ex:
		print(ex)






merchant = incert_merchant(3000)

z=z