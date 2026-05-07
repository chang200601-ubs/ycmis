import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, render_template, request
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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
    link += "<a href=/search>找老師</a><hr>" 
    link += "<a href=/teacher>爬取老師本學期的課程</a><hr>"
    link += "<a href=/movie>電影連結資訊圖表</a><hr>"
    link += "<a href=/moviesearch>爬取即將上映的電影</a><hr>"
    link += "<a href=/spidermovie>讀取開眼電影即將上映影片，寫入Firestore</a><br><hr>"
    link += "<a href=/readmovie> 輸入片名關鍵字,查詢資料庫符合的電影包含編號,片名,海報,介紹頁及上映日期</a><br><hr>"
    link += "<a href=/rode>台中市十大肇事路口</a><br><hr>"
    return link



@app.route("/rode")
def rode():
    R = "<h1>台中市十大肇事路口(113年10月)</h1><br>" 
    url = "https://datacenter.taichung.gov.tw/swagger/OpenData/a1b899c0-511f-4e3d-b22b-814982a97e41"
    headers={'User-Agent':'Mozilla/5.0'}
    Data = requests.get(url,verify=False)
    #print(Data.text)

    JsonData = json.loads(Data.text)
    for item in JsonData:
        R+=item["路口名稱"] + ",原因：" + item["主要肇因"] + "<br>"

    return R + "<br><a href=/>返回首頁</a>"


@app.route("/readmovie", methods=["GET", "POST"])
def readmovie():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            collection_ref = db.collection("電影")
            docs = collection_ref.get()
            for doc in docs:
                movie = doc.to_dict()
                if keyword in movie.get("title", ""):
                    results.append({
                        "id": doc.id,               # 編號
                        "title": movie.get("title", ""),
                        "picture": movie.get("picture", ""),
                        "hyperlink": movie.get("hyperlink", ""),
                        "showDate": movie.get("showDate", "")
                    })
    return render_template("readmovie.html", results=results, keyword=keyword)

@app.route("/spidermovie")
def spidermovie():
    db = firestore.client()
    R=""
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate=sp.find(class_="smaller09").text.replace("更新時間：","")

    result=sp.select(".filmListAllX li")
    info = ""
    total=0
    for item in result:
        total+=1
        movie_id=item.find("a").get("href").replace("/movie/","").replace("/","")
        title=item.find(class_="filmtitle").text
        picture="http://www.atmovies.com.tw"+item.find("img").get("src")
        hyperlink="http://www.atmovies.com.tw"+item.find("a").get("href")
        showDate=item.find(class_="runtime").text[0:15]


        doc = {
            "title": title,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "lastUpdate": lastUpdate
        }

        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)
        
    R+="最後更新日期" + lastUpdate + "<br>"
    R+="總共爬取"+str(total)+"部電影資料庫" +"<br>"
    return R + "<br><a href=/>返回首頁</a>"

@app.route("/moviesearch", methods=["GET", "POST"])
def moviesearch():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            url = "https://www.atmovies.com.tw/movie/next/"
            Data = requests.get(url)
            Data.encoding = "utf-8"
            sp = BeautifulSoup(Data.text, "html.parser")
            items = sp.select(".filmListAllX li")
            for item in items:
                title = item.find("img").get("alt")
                if keyword in title:
                    results.append({
                        "title": title,
                        "url": "https://www.atmovies.com.tw" + item.find("a").get("href"),
                        "img": "https://www.atmovies.com.tw" + item.find("img").get("src")
                    })
    return render_template("moviesearch.html", results=results, keyword=keyword)

@app.route("/movie")
def movie():
    url = "https://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    R = "" 
    
    for item in result:
        title = item.find("img").get("alt")
        movie_url = "https://www.atmovies.com.tw" + item.find("a").get("href")
        img_url = "https://www.atmovies.com.tw" + item.find("img").get("src")
        
        R += f"<b>{title}</b><br>"
        R += f"<a href='{movie_url}' target='_blank'>{movie_url}</a><br>"
        R += f"<img src='{img_url}' width='100'><br><br>"  # 這行改掉
    
    return R + "<br><a href=/>返回首頁</a>"


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
    import requests
    from bs4 import BeautifulSoup

    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")

        result = ""
        seen = set()
        for a in soup.select("a"):
            href = a.get("href", "")
            name = a.get_text(strip=True)
            if "drive.google.com" in href and href not in seen:
                seen.add(href)
                result += name + href + "<br>"

        if result == "":
            result = "抓不到課程資料"
    except Exception as e:
        result = "錯誤：" + str(e)

    return result + "<br><a href=/>返回首頁</a>"

if __name__ == '__main__':
    app.run(debug=True)