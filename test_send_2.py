from datetime import datetime
import time
import RPi.GPIO as GPIO
import psycopg2

conn = psycopg2.connect(\
    "host=XXXXX \
    port=XXXX \
    dbname=test_db \
    user=XXXX \
    password=XXXX"\
        )

# cur = conn.cursor()
# cur.execute("SELECT id from test_table_2 order by id desc limit 1")
# before_id = cur.fetchall()[0][0]

rasp_id = 2

INTERVAL = 1
SLEEPTIME = 2
GPIO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)
#cur = conn.cursor()

if __name__ == '__main__':
    try:
        #cnt = 1
        while True:
            # センサー感知
            cur = conn.cursor()
            cur.execute("SELECT id from test_table_2 order by id desc limit 1")
            before_id = cur.fetchall()[0][0]
            if(GPIO.input(GPIO_PIN) == GPIO.HIGH):
                #print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                before_id += 1
                y = datetime.now().strftime("%Y")
                m = datetime.now().strftime("%m")
                d = datetime.now().strftime("%d")
                h = datetime.now().strftime("%H")
                min = datetime.now().strftime("%M")
                print(before_id,"rasp_id is",rasp_id,"/",y,"/",m,"/",d,"/",h,"/",min)
                cur.execute("INSERT INTO test_table_2 \
                    VALUES (" + str(before_id) + "," + str(rasp_id) + "," + str(y) + "," + str(m) + "," + str(d) + "," + str(h) + "," + str(min) + ")")
                #DBに送るやつとデバイス箱設計
                #ymdが一致するものを抜き出し、24hで分割、miniの15区切りでカウント
                #keyが時間と何クォーターか：valueがカウント数
                #cnt = cnt + 1
                time.sleep(SLEEPTIME)
            else:
                print("None")
                time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("finish")
    finally:
        GPIO.cleanup()

cur.close()
conn.commit()
conn.close()
