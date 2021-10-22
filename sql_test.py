from datetime import datetime
import time
import psycopg2

conn = psycopg2.connect(\
    "host=192.168.10.100 \
    port=5432 \
    dbname=test_db \
    user=pi \
    password=dbpasswd"\
        )

year = input("年：")
month = input("月：")
date = input("日：")

cur = conn.cursor()
cur.execute("SELECT h,min from test_table WHERE \
    y = " + year + "AND m = " + month + "AND d = " + date)
n = cur.fetchall()
#print(n)

#0~14,15~29,30~44,45~59
list_quarter = []
ti = list(range(0,24))
for i in ti:
    list_zantei = []
    for k in n:
        if i == k[0]:
            list_zantei.append(k)
    list_quarter.append(list_zantei)

dict_quarter = {}
list_count = []
for k in ti:
    q_1 = 0
    q_2 = 0
    q_3 = 0
    q_4 = 0
    for i in list_quarter[k]:
        if 0 <= i[1] <= 14:
            q_1 += 1
        elif 15 <= i[1] <= 29:
            q_2 += 1
        elif 30 <= i[1] <= 44:
            q_3 += 1
        elif 45 <= i[1] <= 59:
            q_4 += 1
    if k < 10:
        time_k = "0" + str(k)
    else:
        time_k = str(k)
    dict_quarter[time_k] = [q_1,q_2,q_3,q_4]
    list_count += [q_1,q_2,q_3,q_4]
print(dict_quarter)
print(list_count)
    

cur.close()
conn.commit()
conn.close()
