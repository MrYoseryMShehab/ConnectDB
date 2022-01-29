# from pyspark.sql.functions import max
import numpy as np
import pyodbc
import pandas as pd
max_bill = 290565
try:
        cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=DESKTOP-M5UNLTB\SQLEXPRESS;"
                      "Database=Damanhor;"
                      "Trusted_Connection=yes;")
# cursor = cnxn.cursor()
# db_connection_sql_server = 'select bill_no,bill_value from Bill where bill_no <= 290565'
        query_Bill = """ select bill_no,bill_value from Bill where  BDeleted = 0 and bill_no <= """
        query_Requests = """ select bill_no,Request_id,reque_value from Requests where   RDeleted = 0 and bill_no <= """
# BDeleted = 0 and
        df_Bill = pd.read_sql(query_Bill+ str(max_bill), cnxn)
        df_Bill.rename({0: 'bill_no', 1: 'bill_value'}, axis=1, inplace=True)

        df_Req = pd.read_sql(query_Requests+ str(max_bill), cnxn)

        df_Req.rename({0: 'bill_no',1: 'Request_id', 2: 'reque_value'}, axis=1, inplace=True)

except Error as e:
    print("Error while connecting to Sql Server", e)
finally:
    cnxn.close()
    print("===========================SQL Server connection is closed===========================")
try:
    print("BIll Number I used in DB: ", max_bill)
    print('---------------------------Bill with Zero value and Null-----------------------------')
    df_Bill_null = df_Bill[df_Bill["bill_value"].isna()]
    df_Bill_null_count = df_Bill_null.count()[0]
    df_Bill_Zero =  df_Bill[df_Bill["bill_value"]==0]
    df_Bill_Zero_count = df_Bill_Zero.count()[0]
    print('Bill value with value Null have count : ', df_Bill_null_count)
    print('Bill value with value Zero have count : ', df_Bill_Zero_count)
    print("--------------------------------------")
    df_Req_null = df_Req[df_Req["reque_value"].isna()]
    df_Req_null_count = df_Req_null.count()[0]
    df_Req_Zero =  df_Req[df_Req["reque_value"]==0]
    df_Req_Zero_count = df_Req_Zero.count()[0]
    print('Request value with value Null have count : ', df_Bill_null_count)
    print('Request value with value Zero have count : ', df_Bill_Zero_count)
    print("++++++++++++++++++++++++++++++Sum of all Bill value and Reques value +++++++++++++++++++")
#     print(df_Bill.head(3))
    all_data_Bill_sum = df_Bill['bill_value'].sum()
    all_data_Req_sum = df_Req['reque_value'].sum()
    Subtract_Req_Bill = all_data_Req_sum - all_data_Bill_sum
#     ####----------------------
    print('Sum of all Bill value From Sql Server of Branch 1: ',"{:,}".format(all_data_Bill_sum))
    print('sum of all Requ value From Sql Server of Branch 1: ',"{:,}".format(all_data_Req_sum))
#     print("-----------------------------------------")
# #     print('\n')
    print('Subtract Bill value From Request value in Sql Server of Branch 1: ',"{:,}".format(Subtract_Req_Bill))
    print('++++++++++++++++++++++++++++++++++Bill without Request are  or [Bill not deleted with Request deleted]++++++++++++++++++++++++++')
    Bill_without_Reques = df_Bill[~df_Bill['bill_no'].isin(df_Req['bill_no'])]
    Bill_count_not_in = Bill_without_Reques.count()[0]
    print(Bill_without_Reques.head(10))
    Bill_sum_not_in = Bill_without_Reques['bill_value'].sum()
    print("-------------------")
#     ,str(Bill_count_not_in
    print('count of them are :',Bill_count_not_in,'   With sum of Bill value : ',Bill_sum_not_in)
    print('++++++++++++++++++++++++++++++++++Bill Deleted and Request Not Deleted +++++++++++++++')
    Bill_Deleted_and_Request_Not_Deleted = df_Req[~df_Req['bill_no'].isin(df_Bill['bill_no'])]
    print(Bill_Deleted_and_Request_Not_Deleted.head(10))
    Bill_Deleted_and_Request_Not_Deleted_count = Bill_Deleted_and_Request_Not_Deleted.count()[0]
    Bill_Deleted_and_Request_Not_Deleted_sum = Bill_Deleted_and_Request_Not_Deleted['reque_value'].sum()
    print('count of Bill Deleted and Request Not Deleted :',Bill_Deleted_and_Request_Not_Deleted_count,'   With sum of Request value : ',Bill_Deleted_and_Request_Not_Deleted_sum)



    print('++++++++++++++++++++++++++++++++++pure +++++++++++++++++++++++++++++++++++++++++++++++++++++')
    df_Bill_pure_1 = df_Bill[~df_Bill['bill_no'].isin(Bill_Deleted_and_Request_Not_Deleted['bill_no'])]
    df_Bill_pure_2 = df_Bill_pure_1[~df_Bill_pure_1['bill_no'].isin(Bill_without_Reques['bill_no'])]

    df_Req_pure_1 = df_Req[~df_Req['bill_no'].isin(Bill_Deleted_and_Request_Not_Deleted['bill_no'])]
    df_Req_pure_2 = df_Req_pure_1[~df_Req_pure_1['bill_no'].isin(Bill_without_Reques['bill_no'])]

    df_Bill_pure_2_sum = df_Bill_pure_2['bill_value'].sum()
    df_Req_pure_2_sum = df_Req_pure_2['reque_value'].sum()
    Subtract_Req_Bill_pur = df_Req_pure_2_sum - df_Bill_pure_2_sum
    ####----------------------
    print('Sum pure of all Bill value From Sql Server of Branch 1: ',"{:,}".format(df_Bill_pure_2_sum))
    print('sum pure of all Requ value From Sql Server of Branch 1: ',"{:,}".format(df_Req_pure_2_sum))
    print("-----------------------------------------")
#     print('\n')
    print('Subtract pur Bill value From puer Request value in Sql Server of Branch 1: ',"{:,}".format(Subtract_Req_Bill_pur))
    print("-----------------------------------------")
#     ['bill_value']
    df_Req_pure_2_3 = df_Req_pure_2.groupby("bill_no", as_index=False).agg({"reque_value":np.sum})
    print(df_Req_pure_2_3.head(10))
# #     pd.merge(df1, df2, on="key").head(10))
    print("-----------------------------------------")
#     df_Bill_pure_1_3 = df_Bill_pure_2.groupby("bill_no").agg({"bill_value":np.sum})
#     df_Bill_pure_1_3.rename({0: 'bill_no', 1: 'reque_value'}, axis=1, inplace=True)
#     df_Bill_pure_2.pop(df_Bill_pure_2.index)
    print(df_Bill_pure_2.head(10))
#     df_subtract =  df_Bill_pure_1_3[~df_Req['bill_no'].isin(df_Req_pure_2_3['bill_no'])]
#     Bill_Deleted_and_Request_Not_Deleted = df_Req[~df_Req['bill_no'].isin(df_Bill['bill_no'])]
#     print(df_Bill_pure_2.info())

    print("----------------------------------------Bill not equel Request------------------------------------------------------")
    merge_bill_Request = pd.merge(df_Req_pure_2_3,df_Bill_pure_2,on='bill_no')
    Bill_not_equel_Request = merge_bill_Request[merge_bill_Request['reque_value'] != merge_bill_Request['bill_value']]
    print(Bill_not_equel_Request)
#     print(xxx.head(10))
#     print(xxx.info())

except Error as e:
    print("Error while calculation", e)
finally:
    print("===========================Calculation Sql Server is End===============================")
