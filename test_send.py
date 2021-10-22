from datetime import datetime
import time
import RPi.GPIO as GPIO
import psycopg2

conn = psycopg2.connect(\
    "host=192.168.10.111 \
    port=5432 \
    dbname=test_db \
    user=pi \
    password=dbpasswd"\
        )

cur = conn.cursor()
cur.execute("SELECT id from test_table order by id desc limit 1")
before_id = cur.fetchall()[0][0]

INTERVAL = 1
SLEEPTIME = 2
GPIO_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

if __name__ == '__main__':
    try:
        #cnt = 1
        while True:
            # センサー感知
            if(GPIO.input(GPIO_PIN) == GPIO.HIGH):
                #print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                before_id += 1
                y = datetime.now().strftime("%Y")
                m = datetime.now().strftime("%m")
                d = datetime.now().strftime("%d")
                h = datetime.now().strftime("%H")
                min = datetime.now().strftime("%M")
                print(before_id,"/",y,"/",m,"/",d,"/",h,"/",min)
                cur.execute("INSERT INTO test_table \
                    VALUES (" + str(before_id) + "," + str(y) + "," + str(m) + "," + str(d) + "," + str(h) + "," + str(min) + ")")
                
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