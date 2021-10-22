# import psycopg2

# #配置したDBよって変更
# host = "localhost"
# port = "5432"
# dbname = "future_hayashi"
# user = "postgres"
# password = "taiki0831"

# conn = psycopg2.connect(\
#     "host=" + host + \
#     " port=" + port + \
#     " dbname=" + dbname + \
#     " user=" + user + \
#     " password=" + password\
#         )

# cur = conn.cursor()
# cur.execute("SELECT * from test_table")
# n = cur.fetchall()
# print(n)

from flask import Flask, render_template, request, session
from datetime import datetime
import time
import psycopg2
import dict_list

app = Flask(__name__)
app.secret_key = os.urandom(32)

#上のif階層では下で得られるセッションは全て消す
#テンプレートはifのなかにifを置いていく流れ
#場所=>(場所から選択可能な日を抽出、選択肢に反映)年月日=>(時間は全部0~2359でOK)開始時間と終了時間

@app.route("/",methods=["POST","GET"])
def begin_page():
    if("where" in request.form):
        where = request.form["where"]
        session["where"] = where
        session.pop("when",None)
        return render_template("test_flask.html",where = where)
    elif("when" in request.form):
        when = request.form["when"]
        session["when"] = when
        where = session["where"]
        return render_template("test_flask.html",where=where,when = when)
    else:
        return render_template("test_flask.html")