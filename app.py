from flask import Flask, render_template, request, session
from datetime import datetime
import pandas as pd
import time
import os
import psycopg2
import dict_list

app = Flask(__name__)
app.secret_key = os.urandom(32)

conn = psycopg2.connect(\
    "host=XXXX\
    port=XXXX \
    dbname=test_db \
    user=XXXX \
    password=XXXX"\
        )

#グラフ用15分区切り
time_list = []
for i in list(range(0,24)):
    if i < 10:
        i = "0" + str(i)
    else:
        i = str(i)
    for k in ["00","15","30","45"]:
        time_list.append(i + ":" + k)

#ドロップダウン用rasp_id
cur = conn.cursor()
cur.execute("SELECT * from test_table_2")
full_table = cur.fetchall()
rasp_id = []
for i in full_table:
    if i[1] not in rasp_id:
        rasp_id.append(i[1])

#データ持ってきてない時の描画用
list_zero = []
for i in range(0,24):
    for k in range(0,4):
        list_zero.append(0)

#最大値関数 [最大値,[最大時間]]
def get_max(score_list):
    count = 0
    max_score = max(score_list)
    max_time = []
    for i in time_list:
        if score_list[count] == max_score:
            max_time.append(i)
        count += 1
    return max_score,max_time

#平均値
def get_mean(score_list):
    mean = sum(score_list) / len(score_list)
    return mean

#総合値
def get_sum(score_list):
    all_sum = sum(score_list)
    return all_sum


@app.route("/",methods=["POST","GET"])
def begin_page():
    #最下層時間指定
    if("start_time" in request.form) and ("fin_time" in request.form):
        #when,where,year,month,date,start_time,fin_time
        #ラズパイID
        where = session["where"]
        #年日時str
        when = session["when"]
        #年
        year = session["year"]
        #月
        month = session["month"]
        #日
        date = session["date"]
        #開始時間
        start_time = request.form["start_time"]
        #終了時間
        fin_time = request.form["fin_time"]
        print(start_time,fin_time)

        #ドロップダウン用
        #y-m-dで取得できるものをstr取得
        drop_when = []
        for i in full_table:
            if int(where) == i[1]:
                if i[3] < 10:
                    y_m_d = str(i[2]) + "-0" + str(i[3]) + "-" + str(i[4])
                else:
                    y_m_d = str(i[2]) + "-" + str(i[3]) + "-" + str(i[4])
                if y_m_d not in drop_when:
                    drop_when.append(y_m_d)
        
        #データを引っ張ってきた
        #選択した日時のやつ
        dic_lis = dict_list.get_dict_list(where,year,month,date)
        list_count = dic_lis[1]

        #最大値などmax_thing[0,1]
        max_thing = get_max(list_count)
        print("最大値など\n",max_thing[0])
        print(max_thing[1])
        max_score = max_thing[0]
        max_time = max_thing[1]

        #平均mean_thing
        mean_thing = get_mean(list_count)
        print("平均値\n",mean_thing)

        #総合値all_sum_thing
        all_sum_thing = get_sum(list_count)
        print("総合値\n",all_sum_thing)

        #四分位count_75,count_25
        four_df = pd.DataFrame(data=list_count)
        Quart = four_df[0].describe()
        print("25%="+str(Quart[4]),"75%="+str(Quart[6]))
        count_75 = []
        count_25 = []
        count = 0
        for i in time_list:
            if list_count[count] >= Quart[6]:
                if list_count[count] != 0:
                    count_75.append(i)
            elif list_count[count] <= Quart[4]:
                if list_count[count] != 0:
                    count_25.append(i)
            count += 1
        if len(count_75) == 0:
            count_75.append("集計出来ませんでした")
        if len(count_25) == 0:
            count_25.append("集計出来ませんでした")
        print("75以上",count_75,"\n25以下",count_25)

        human_count = 0
        human_time = {}
        for i in time_list:
            if list_count[human_count] >= mean_thing:
                human_time[human_count] = i
            human_count += 1
        think = 0
        think_list = []
        for i in human_time:
            if i + 1 == think or i - 1 == think:
                think_list.append([time_list[think],time_list[i]])
            else:
                think = i
        print("混雑時",think_list)

        #----------------前日取得用-----------------------------------------------------------------------------
        if len(drop_when) > 1:
            if when != drop_when[0]:
                when_count = 0
                for i in drop_when:
                    if when == i:
                        break
                    when_count += 1
                when_count -= 1
                zen_when = drop_when[when_count]
                zen_year = drop_when[when_count][0:4]
                #session["zen_year"] = zen_year
                zen_month = drop_when[when_count][5:7]
                #session["zen_month"] = zen_month
                zen_date = drop_when[when_count][8:]
                #session["zen_date"] = zen_date
                print("zen_年月日",zen_year,zen_month,zen_date)
                zen_dic_lis = dict_list.get_dict_list(where,zen_year,zen_month,zen_date)
                zen_dict_quarter = zen_dic_lis[0]
                zen_list_count = zen_dic_lis[1]

                #最大値などmax_thing[0,1]
                zen_max_thing = get_max(zen_list_count)
                print("zen_最大値など\n",zen_max_thing[0])
                print(zen_max_thing[1])
                zen_max_score = zen_max_thing[0]
                zen_max_time = zen_max_thing[1]

                #平均mean_thing
                zen_mean_thing = get_mean(zen_list_count)
                print("zen_平均値\n",zen_mean_thing)

                #総合値all_sum_thing
                zen_all_sum_thing = get_sum(zen_list_count)
                print("zen_総合値\n",zen_all_sum_thing)

                #四分位count_75,count_25
                zen_four_df = pd.DataFrame(data=zen_list_count)
                zen_Quart = zen_four_df[0].describe()
                print("zen_25%="+str(zen_Quart[4]),"zen_75%="+str(zen_Quart[6]))
                zen_count_75 = []
                zen_count_25 = []
                count = 0
                for i in time_list:
                    if zen_list_count[count] >= zen_Quart[6]:
                        if zen_list_count[count] != 0:
                            zen_count_75.append(i)
                    elif zen_list_count[count] <= zen_Quart[4]:
                        if zen_list_count[count] != 0:
                            zen_count_25.append(i)
                    count += 1
                if len(zen_count_75) == 0:
                    zen_count_75.append("集計出来ませんでした")
                if len(zen_count_25) == 0:
                    zen_count_25.append("集計出来ませんでした")
                print("zen_75以上",zen_count_75,"\nzen_25以下",zen_count_25)

                zen_human_count = 0
                zen_human_time = {}
                for i in time_list:
                    if zen_list_count[zen_human_count] >= zen_mean_thing:
                        zen_human_time[zen_human_count] = i
                    zen_human_count += 1
                zen_think = 0
                zen_think_list = []
                for i in zen_human_time:
                    if i + 1 == zen_think or i - 1 == zen_think:
                        zen_think_list.append([time_list[zen_think],time_list[i]])
                    else:
                        zen_think = i
                print("zen_混雑時",zen_think_list)
            else:
                zen_when = "None"
                zen_year = "None"
                zen_month = "None"
                zen_date = "None"
                zen_max_score = "None"
                zen_max_time = "None"
                zen_mean_thing = "None"
                zen_all_sum_thing = "None"
                zen_count_75 = ["None"]
                zen_count_25 = ["None"]
                zen_think_list = ["None"]
        else:
            zen_when = "None"
            zen_year = "None"
            zen_month = "None"
            zen_date = "None"
            zen_max_score = "None"
            zen_max_time = "None"
            zen_mean_thing = "None"
            zen_all_sum_thing = "None"
            zen_count_75 = ["None"]
            zen_count_25 = ["None"]
            zen_think_list = ["None"]
        #----------------前日取得用-----------------------------------------------------------------------------

        return render_template("hist_page.html",rasp_id=rasp_id,where=where,drop_when=drop_when,\
            when=when,list_count=list_count,time_list=time_list,start_time=start_time,fin_time=fin_time,\
                max_score=max_score,max_time=max_time,mean_thing=mean_thing,all_sum_thing=all_sum_thing,count_75=count_75,\
                    count_25=count_25,zen_when=zen_when,zen_max_score=zen_max_score,zen_max_time=zen_max_time,\
                        zen_mean_thing=zen_mean_thing,zen_all_sum_thing=zen_all_sum_thing,zen_count_75=zen_count_75,zen_count_25=zen_count_25,think_list=think_list,zen_think_list=zen_think_list)

    #二層目日時指定
    elif("when" in request.form):
        #whenとwhere
        where = session["where"]
        when = request.form["when"]

        #開始終了時間のセッション削除
        session.pop("start_time",None)
        session.pop("fin_time",None)

        #ドロップダウンメニュー用
        drop_when = []
        for i in full_table:
            if int(where) == i[1]:
                if i[3] < 10:
                    y_m_d = str(i[2]) + "-0" + str(i[3]) + "-" + str(i[4])
                else:
                    y_m_d = str(i[2]) + "-" + str(i[3]) + "-" + str(i[4])
                if y_m_d not in drop_when:
                    drop_when.append(y_m_d)
        #sessionに入れておく
        session["when"] = when

        #年月日抽出
        year = when[0:4]
        session["year"] = year
        month = when[5:7]
        session["month"] = month
        date = when[8:]
        session["date"] = date
        print("年月日",year,month,date)

        #データを持ってくる
        dic_lis = dict_list.get_dict_list(where,year,month,date)
        dict_quarter = dic_lis[0]
        list_count = dic_lis[1]

        #最大値などmax_thing[0,1]
        max_thing = get_max(list_count)
        print("最大値など\n",max_thing[0])
        print(max_thing[1])
        max_score = max_thing[0]
        max_time = max_thing[1]

        #平均mean_thing
        mean_thing = get_mean(list_count)
        print("平均値\n",mean_thing)

        #総合値all_sum_thing
        all_sum_thing = get_sum(list_count)
        print("総合値\n",all_sum_thing)

        #四分位count_75,count_25
        four_df = pd.DataFrame(data=list_count)
        Quart = four_df[0].describe()
        print("25%="+str(Quart[4]),"75%="+str(Quart[6]))
        count_75 = []
        count_25 = []
        count = 0
        for i in time_list:
            if list_count[count] >= Quart[6]:
                if list_count[count] != 0:
                    count_75.append(i)
            elif list_count[count] <= Quart[4]:
                if list_count[count] != 0:
                    count_25.append(i)
            count += 1
        if len(count_75) == 0:
            count_75.append("集計出来ませんでした")
        if len(count_25) == 0:
            count_25.append("集計出来ませんでした")
        print("75以上",count_75,"\n25以下",count_25)

        human_count = 0
        human_time = {}
        for i in time_list:
            if list_count[human_count] >= mean_thing:
                human_time[human_count] = i
            human_count += 1
        think = 0
        think_list = []
        for i in human_time:
            if i + 1 == think or i - 1 == think:
                think_list.append([time_list[think],time_list[i]])
            else:
                think = i
        print("混雑時",think_list)
        # print(time_list)
        #----------------前日取得用-----------------------------------------------------------------------------
        if len(drop_when) > 1:
            if when != drop_when[0]:
                when_count = 0
                for i in drop_when:
                    if when == i:
                        break
                    when_count += 1
                when_count -= 1
                zen_when = drop_when[when_count]
                zen_year = drop_when[when_count][0:4]
                #session["zen_year"] = zen_year
                zen_month = drop_when[when_count][5:7]
                #session["zen_month"] = zen_month
                zen_date = drop_when[when_count][8:]
                #session["zen_date"] = zen_date
                print("zen_年月日",zen_year,zen_month,zen_date)
                zen_dic_lis = dict_list.get_dict_list(where,zen_year,zen_month,zen_date)
                zen_dict_quarter = zen_dic_lis[0]
                zen_list_count = zen_dic_lis[1]

                #最大値などmax_thing[0,1]
                zen_max_thing = get_max(zen_list_count)
                print("zen_最大値など\n",zen_max_thing[0])
                print(zen_max_thing[1])
                zen_max_score = zen_max_thing[0]
                zen_max_time = zen_max_thing[1]

                #平均mean_thing
                zen_mean_thing = get_mean(zen_list_count)
                print("zen_平均値\n",zen_mean_thing)

                #総合値all_sum_thing
                zen_all_sum_thing = get_sum(zen_list_count)
                print("zen_総合値\n",zen_all_sum_thing)

                #四分位count_75,count_25
                zen_four_df = pd.DataFrame(data=zen_list_count)
                zen_Quart = zen_four_df[0].describe()
                print("zen_25%="+str(zen_Quart[4]),"zen_75%="+str(zen_Quart[6]))
                zen_count_75 = []
                zen_count_25 = []
                count = 0
                for i in time_list:
                    if zen_list_count[count] >= zen_Quart[6]:
                        if zen_list_count[count] != 0:
                            zen_count_75.append(i)
                    elif zen_list_count[count] <= zen_Quart[4]:
                        if zen_list_count[count] != 0:
                            zen_count_25.append(i)
                    count += 1
                if len(zen_count_75) == 0:
                    zen_count_75.append("集計出来ませんでした")
                if len(zen_count_25) == 0:
                    zen_count_25.append("集計出来ませんでした")
                print("zen_75以上",zen_count_75,"\nzen_25以下",zen_count_25)
                
                zen_human_count = 0
                zen_human_time = {}
                for i in time_list:
                    if zen_list_count[zen_human_count] >= zen_mean_thing:
                        zen_human_time[zen_human_count] = i
                    zen_human_count += 1
                zen_think = 0
                zen_think_list = []
                for i in zen_human_time:
                    if i + 1 == zen_think or i - 1 == zen_think:
                        zen_think_list.append([time_list[zen_think],time_list[i]])
                    else:
                        zen_think = i
                print("zen_混雑時",zen_think_list)

            else:
                zen_when = "None"
                zen_year = "None"
                zen_month = "None"
                zen_date = "None"
                zen_max_score = "None"
                zen_max_time = "None"
                zen_mean_thing = "None"
                zen_all_sum_thing = "None"
                zen_count_75 = ["None"]
                zen_count_25 = ["None"]
                zen_think_list = ["None"]
        else:
            zen_when = "None"
            zen_year = "None"
            zen_month = "None"
            zen_date = "None"
            zen_max_score = "None"
            zen_max_time = "None"
            zen_mean_thing = "None"
            zen_all_sum_thing = "None"
            zen_count_75 = ["None"]
            zen_count_25 = ["None"]
            zen_think_list = ["None"]
        #----------------前日取得用-----------------------------------------------------------------------------


        return render_template("hist_page.html",rasp_id=rasp_id,where=where,drop_when=drop_when,\
            when=when,dict_quarter=dict_quarter,list_count=list_count,time_list=time_list,\
                max_score=max_score,max_time=max_time,mean_thing=mean_thing,all_sum_thing=all_sum_thing,count_75=count_75,\
                    count_25=count_25,zen_when=zen_when,zen_max_score=zen_max_score,zen_max_time=zen_max_time,\
                        zen_mean_thing=zen_mean_thing,zen_all_sum_thing=zen_all_sum_thing,zen_count_75=zen_count_75,zen_count_25=zen_count_25,think_list=think_list,zen_think_list=zen_think_list)

    elif("where" in request.form):
        #ラズパイID
        where = request.form["where"]
        session["where"] = where

        #下層のセッション削除
        session.pop("when",None)

        #ドロップダウン用ymdリスト
        drop_when = []
        for i in full_table:
            if int(where) == i[1]:
                if i[3] < 10:
                    y_m_d = str(i[2]) + "-0" + str(i[3]) + "-" + str(i[4])
                else:
                    y_m_d = str(i[2]) + "-" + str(i[3]) + "-" + str(i[4])
                if y_m_d not in drop_when:
                    drop_when.append(y_m_d)
        
        conn.commit()
        #conn.close()
        return render_template("hist_page.html",rasp_id=rasp_id,where=where,drop_when=drop_when,list_count=list_zero)
    else:
        conn.commit()
        #conn.close()
        return render_template("hist_page.html",rasp_id=rasp_id,list_count=list_zero)
