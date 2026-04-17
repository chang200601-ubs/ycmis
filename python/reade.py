from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# 初始化 Firebase (確保只初始化一次)
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    keyword = ""
    
    if request.method == "POST":
        keyword = request.form.get("keyword", "")
        collection_ref = db.collection("靜宜資管")
        docs = collection_ref.get()
        
        for doc in docs:
            teacher = doc.to_dict()
            if keyword in teacher.get("name", ""):
                results.append(teacher)
                
    return render_template("index.html", results=results, keyword=keyword)

if __name__ == "__main__":
    app.run(debug=True)