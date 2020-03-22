import os
# from flask import Flask,render_template,request,session,redirect,url_for
# from flask import send_from_directory
from flask import *
from models.models import OnegaiContent
from models.models import User
from models.database import db_session
from datetime import datetime
from app import key
from hashlib import sha256
from werkzeug.utils import secure_filename

#Flaskオブジェクトの生成
app = Flask(__name__)
#暗号化キー
app.secret_key = key.SECRET_KEY

# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './static/uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
@app.route("/index")
def index():
    if "user_name" in session: #ログインのセッション情報がある場合
        name = session["user_name"]
        all_onegai = OnegaiContent.query.all()
        rename = "success"
        return render_template("index.html",name=name,all_onegai=all_onegai,rename=rename)
    else:
        return redirect(url_for("top",status="logout"))

@app.route("/top")
def top():
    status = request.args.get("status")
    return render_template("top.html",status=status)

@app.route("/newcomer")
def newcomer():
    status = request.args.get("status")
    return render_template("newcomer.html",status=status)

#@app.route("/index",methods=["post"])
# def post():
#     name = request.form["name"]
#     okyo = ["1","2","3"]
#     all_onegai = OnegaiContent.query.all()
#     return render_template("index.html",name=name,okyo=okyo,all_onegai=all_onegai)

@app.route("/add",methods=["post"])
def add():
    title = request.form["title"]
    body = request.form["body"]
    content = OnegaiContent(title,body,datetime.now())
    db_session.add(content)
    db_session.commit()
    return redirect(url_for("index"))

@app.route("/update",methods=["post"])
def update():
    content = OnegaiContent.query.filter_by(id=request.form["update"]).first()
    content.title = request.form["title"]
    content.body = request.form["body"]
    db_session.commit()
    return redirect(url_for("index"))

@app.route("/delete",methods=["post"])
def delete():
    id_list = request.form.getlist("delete")
    for id in id_list:
        content = OnegaiContent.query.filter_by(id=id).first()
        db_session.delete(content)
    db_session.commit()
    return redirect(url_for("index"))

#ログイン処理
@app.route("/login",methods=["post"])
def login():
    user_name = request.form["user_name"] #入力されたユーザ名取得
    user = User.query.filter_by(user_name=user_name).first() #そのユーザ名を持つDBレコードをusersテーブルから抽出
    if user: #DBレコードがあった場合
        password = request.form["password"] #入力されたパスワード取得
        hashed_password = sha256((user_name + password + key.SALT).encode("utf-8")).hexdigest() #パスワードをハッシュ(テーブル)化
        if user.hashed_password == hashed_password: #DBレコードのハッシュ化パスワードと一致するか判定
            session["user_name"] = user_name
            return redirect(url_for("index"))
        else:
            return redirect(url_for("top",status="wrong_password"))
    else:
        return redirect(url_for("top",status="user_notfound"))

#ログアウト処理
@app.route("/logout")
def logout():
    session.pop("user_name", None)
    return redirect(url_for("top",status="logout"))

#ユーザ登録処理
@app.route("/registar",methods=["post"])
def registar():
    user_name = request.form["user_name"]
    user = User.query.filter_by(user_name=user_name).first()
    if user:
        return redirect(url_for("newcomer",status="exist_user"))
    else:
        password = request.form["password"]
        hashed_password = sha256((user_name + password + key.SALT).encode("utf-8")).hexdigest()
        user = User(user_name, hashed_password)
        db_session.add(user)
        db_session.commit()
        session["user_name"] = user_name
        return redirect(url_for("index"))

#ユーザ名変更
@app.route("/changeName",methods=["post"])
def changeName():
    user = User.query.filter_by(user_name=session["user_name"]).first()
    password = request.form["password"]
    hashed_password = sha256((user.user_name + password + key.SALT).encode("utf-8")).hexdigest()
    if user.hashed_password == hashed_password:
        new_name = request.form["new_name"]
        user.user_name = new_name
        user.hashed_password = sha256((new_name + request.form["password"] + key.SALT).encode("utf-8")).hexdigest()
        session["user_name"] = new_name
        db_session.commit()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))

#おまじない
if __name__ == "__main__":
    app.run(debug=True)
