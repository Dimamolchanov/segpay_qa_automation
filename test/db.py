import pymssql
from splinter import Browser
browser = Browser()


# server ="STGDB1"
# # # user = "SPStaff"
# # # password = "Toccata200e"
# # # conn = pymssql.connect(server, user, password, "SP_Data")
# # # cursor = conn.cursor()
# # #
# # # cursor.execute("select * from PostbackConfigs where merchantid = 27001")
# # #
# # #
# # # print ( cursor)
# # #
# # # for row in cursor:
# # #     print('row = %r' % (row,))
# # #
# # # conn.close()

browser.visit('http://google.com')
browser.fill('q', 'splinter - python acceptance testing for web applications')