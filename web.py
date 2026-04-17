import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request
from datetime import datetime

# 1. Firebase 初始化
if not firebase_admin._apps:
    if os.path.exists('serviceAccountKey.json'):
        cred = credentials.Certificate('serviceAccountKey.json')
    else:
        firebase_config = os.getenv('FIREBASE_CONFIG')
        if firebase_config:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
        else:
            raise ValueError("找不到 Firebase 設定！")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Flask 初始化
app = Flask(__name__)

@app.route("/")
def index():
    link = "<h1>YCC的Python網頁</h1>"
    link += "<a href=/mis>課程</a><br><hr>"
    link += "<a href=/today>今天日期時間</a><br><hr>"
    link += "<a href=/me>我的網頁</a><br><hr>"
    link += "<a href=/welcome?u=ycc&d=靜宜資管&c=資訊管理導論>Get傳值</a><br><hr>"
    link += "<a href=/account>POST傳值</a><br><hr>"
    link += "<a href=/count>次方與根號計算</a><br><hr>"   
    link += "<a href=/read>讀取Firestore資料</a><hr>" 
    link += "<a href=/read2>讀取Firestore資料(關鍵字)</a><hr>" 
    link += "<a href=/find>找老師</a><hr>" 
    link += "<a href=/teacher>老師本學期的課程</a><hr>" 
    return link

@app.route("/read2")
def read2():
    Result = ""
    keyword = "楊"
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.get()    
    for doc in docs: 
        teacher = doc.to_dict()
        if keyword in teacher.get("name", ""):        
            Result += str(teacher) + "<br>" 
    if Result == "":
        Result = "查無資料"
    return Result + "<br><a href=/>返回首頁</a>"

@app.route("/read")
def read():
    Result = ""
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.get()    
    for doc in docs:          
        Result += str(doc.to_dict()) + "<br>"    
    return Result + "<br><a href=/>返回首頁</a>"

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>返回首頁</a>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html", datetime = str(now))

@app.route("/me")
def me():
    now = datetime.now()
    return render_template("MIS2B411316337.html", datetime = str(now))

@app.route("/welcome", methods=["GET"])
def welcome():
    user = request.values.get("u")
    d = request.values.get("d")
    c = request.values.get("c")   
    return render_template("welcome.html", name=user, dep=d, course=c)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        return "您輸入的帳號是：" + user + "；密碼為：" + pwd 
    return render_template("account.html")

@app.route("/count")
def count():
    return render_template("count.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            collection_ref = db.collection("靜宜資管")
            docs = collection_ref.get()
            for doc in docs:
                teacher = doc.to_dict()
                if keyword in teacher.get("name", ""):
                    results.append(teacher)
    return render_template("search.html", results=results, keyword=keyword)

@app.route("/teacher")
def teacher():
    return "<h1>老師本學期的課程</h1><p>這是尚未實作的功能</p><a href=/>返回首頁</a>"

if __name__ == '__main__':
    app.run(debug=True)