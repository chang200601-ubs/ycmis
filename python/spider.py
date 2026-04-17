import requests
from bs4 import BeautifulSoup

@app.route("/find", methods=["GET", "POST"])
def find():
    keyword = ""
    results = []
    
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        
        if keyword:
            # 1. 從 Firestore 查詢符合的老師
            collection_ref = db.collection("靜宜資管")
            docs = collection_ref.get()
            
            for doc in docs:
                teacher = doc.to_dict()
                if keyword in teacher.get("name", ""):
                    # 2. 爬取老師的課程頁面
                    teacher_courses = []
                    url = teacher.get("url", "")  # Firestore 裡存的老師課程網址
                    
                    if url:
                        try:
                            resp = requests.get(url, timeout=5)
                            resp.encoding = "utf-8"
                            soup = BeautifulSoup(resp.text, "html.parser")
                            
                            # 抓取所有 <tr> 裡的課程資料（依實際網頁結構調整）
                            rows = soup.select("table tr")
                            for row in rows[1:]:  # 跳過標題列
                                cols = [td.get_text(strip=True) for td in row.find_all("td")]
                                if cols:
                                    teacher_courses.append(cols)
                        except Exception as e:
                            teacher_courses = [["（課程資料讀取失敗：" + str(e) + "）"]]
                    
                    teacher["courses"] = teacher_courses
                    results.append(teacher)
    
    return render_template("find.html", keyword=keyword, results=results)