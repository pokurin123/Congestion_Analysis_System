from datetime import datetime
import time
import RPi.GPIO as GPIO
import psycopg2

conn = psycopg2.connect(\
    "host=ホスト名 \
    port=ポート番号(pgsqlなら5432とか) \
    dbname=db名 \
    user=ユーザ名(権限周り確認) \
    password=パス"\
        )

#DBレコード最後尾のIDを取得
cur = conn.cursor()
cur.execute("SELECT id from test_table order by id desc limit 1")
before_id = cur.fetchall()[0][0]

#インターバルだったりスリープ時間を記録
#使用するGPI0ピンを選択
INTERVAL = 1
SLEEPTIME = 2
GPIO_PIN = 18

#GPI0のセットアップ
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.IN)

if __name__ == '__main__':
    try:
        while True:
            # センサー感知
            if(GPIO.input(GPIO_PIN) == GPIO.HIGH):
                before_id += 1
                y = datetime.now().strftime("%Y")
                m = datetime.now().strftime("%m")
                d = datetime.now().strftime("%d")
                h = datetime.now().strftime("%H")
                min = datetime.now().strftime("%M")
                print(before_id,"/",y,"/",m,"/",d,"/",h,"/",min)
                #id/y/m/d/h/minをinsert
                cur.execute("INSERT INTO test_table \
                    VALUES (" + \
                        str(before_id) + "," + \
                        str(y) + "," + \
                        str(m) + "," + \
                        str(d) + "," + \
                        str(h) + "," + \
                        str(min) + ")")
                #反応後即動作だと反応感知が重複するので適切なスリープを挟む
                time.sleep(SLEEPTIME)
            else:
                print("None")
                time.sleep(INTERVAL)
    except KeyboardInterrupt:
        #Ctrl + C => 終了
        print("finish")
    finally:
        #GPI0周りをリセット
        GPIO.cleanup()

cur.close()
conn.commit()
conn.close()