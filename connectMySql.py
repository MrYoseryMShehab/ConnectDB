import mysql.connector as sql
from mysql.connector import Error
import pandas as pd
# import pyodbc

try:
    #    connection = sql.connect(host='10.10.12.116',
    connection = sql.connect(host='ipForServerIConnect',
                                         database='PI',
                                         user='Myuser',
                                         password='MyPasword')


    mycursor = connection.cursor()
#         cursorsql = conn.cursor()

        #factureالربط مع فاتورة البيع
    db_connection_sql_facture = """select bill_no,bill_value from PIBill
                                            where BranchID = 1 and bill_no <= 290565"""

#          db_connection_sql_server = """select bill_no,bill_value from Bill
#                                             where bill_no <= 290565"""

    mycursor.execute(db_connection_sql_facture)
    myresult = mycursor.fetchall()
    df_all = pd.DataFrame(myresult)
#         max_of_no = df_all
        #rename columnens
    df_all.rename({0: 'bill_no', 1: 'bill_value'}, axis=1, inplace=True)


#         cursorsql.execute(db_connection_sql_server)
#         myresult_sql = cursorsql.fetchall()
#         df_all_sql = pd.DataFrame(myresult_sql)


except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
            mycursor.close()
            connection.close()
            print("MySQL connection is closed")
# print(max_of_no)

#     bar_data.sort_values(by=['multicurrency_total_ttc'])
#      all_data =     df_all.groupBy().sum().collect()
#     all_count = df_fourn['multicurrency_total_ttc'].count()
# print(df_all)
# print(df_all.info(verbose=True))
# all_data_sum = df_all.sum()
all_data_sum = df_all['bill_value'].sum()
# f['Score'].sum()
# .collect()[0][0]
# all_data =     df_all.max(bill_value).collect()
print(all_data_sum.head(10))
