import csv
import json
import os
from datetime import datetime

import cv2
import base64
import numpy as np

import Back_End, Create_Folder_and_DataSet, Stroke_Video_Generation
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from wtforms import StringField, PasswordField, SubmitField  # 表单类型
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import DataRequired, Email, EqualTo  # 验证数据不能为空
from flask_bootstrap import Bootstrap
import time
import subprocess

""""""""""""""""""""""""
""" 这里是初始化的代码 """
""""""""""""""""""""""""

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')
app.config["SECRET_KEY"] = "123456"
bootstrap = Bootstrap(app)

# MYSQL 的主机名
HOSTNAME = 'localhost'

# MYSQL 的端口号
PORT = 3306

# 连接MYSQL的用户名
USERNAME = 'root'

# 连接MYSQL的密码
PASSWORD = '123456'

# 数据库名称
DATABASE = 'stroke_database'

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4'

db = SQLAlchemy(app)

# basedir
basedir = os.path.abspath(os.path.dirname(__file__))

""""""""""""""""""""""""
""" 这里是测试的代码 """
""""""""""""""""""""""""

# # 用于测试连接的代码
# with app.app_context():
#     with db.engine.connect() as conn:
#         rs = conn.execute(text("select 1"))
#         print(rs.fetchone())

# 同步数据库代码
# with app.app_context():
#     db.create_all()

""""""""""""""""""""""""
""" 这里ORM的代码 """
""""""""""""""""""""""""


# 这里存放数据库中的表单——ORM模型
# ORM 模型

# 模型 1 创建了customer数据库
class Customer(db.Model):
    __tablename__ = 'Customer'
    username = db.Column(db.String(255), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# 模型2 创建提交图片表格
class PictureSet(db.Model):
    __tablename__ = 'PictureSet'
    pk = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    Picture = db.Column(db.PickleType, nullable=False)
    PictureName = db.Column(db.String(255), nullable=False)
    CreateTime = db.Column(db.DateTime, nullable=False)


# 模型3 创建历史表格
class History(db.Model):
    __tablename__ = 'History'
    pk = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    picture_name = db.Column(db.String(255), nullable=False)
    picture_id = db.Column(db.Integer, nullable=False)
    Picture = db.Column(db.PickleType, nullable=False)
    Picture_Stroke_list = db.Column(db.String(8192), nullable=False)

""""""""""""""""""""""""
""" 这里是主页的代码 """
""""""""""""""""""""""""


# 主页
@app.route('/')
def hello_world():  # put application's code here
    return render_template('mainpage.html')


""""""""""""""""""""""""
""" 这里是登录的代码 """
""""""""""""""""""""""""


# 登录表格
class LogInForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired("用户名不能为空")])
    password = PasswordField(label='密码', validators=[DataRequired("密码不能为空")])
    submit = SubmitField(label='登录')


# 登录
@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LogInForm()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_Exist_User = Customer.query.filter_by(username=username).count()
        if not is_Exist_User:
            flash("不存在该用户！")
            db.session.rollback()
        else:
            true_password = Customer.query.filter_by(username=username).first().password
            if password == true_password:
                # 登录成功
                return redirect(url_for('Stroke', username=username))
            else:
                flash("密码错误！")
                db.session.rollback()
    return render_template('login.html', form=form)


""""""""""""""""""""""""
""" 这里是注册的代码 """
""""""""""""""""""""""""


# 定义注册表单模型
class RegistrationForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired("用户名不能为空")])
    password = PasswordField(label='密码', validators=[DataRequired("密码不能为空")])
    submit = SubmitField(label='注册')


# 注册
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    # 创建表单类型
    form = RegistrationForm()
    # 下面开始注册需要的代码
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_Exist_User = Customer.query.filter_by(username=username).count()
        # print(is_Exist_User)
        if not is_Exist_User:
            try:
                new_customer = Customer(username=username, password=password)
                db.session.add(new_customer)
                db.session.commit()
                flash('注册成功！请登录')
                return redirect(url_for('login'))
            except Exception as e:
                print(e)
                flash('注册失败')
                db.session.rollback()
        else:
            flash('用户名已被占用！')
            db.session.rollback()
    # print(form.username)
    # print(form.password)
    # 表单返回模板
    return render_template('signup.html', form=form)


""""""""""""""""""""""""
""" 这里是主要功能的代码 """
""""""""""""""""""""""""


# 主要功能
# 这里显示的是允许上传的图片类型，这里我们初步只支持jpg格式的图片文件
class Submit_Picture(FlaskForm):
    PictureName = StringField(label='图片名称', validators=[DataRequired("请输入作品名称!")])
    SubmitPicture = FileField(label='请上传书法作品jpg图片', validators=[FileAllowed(['jpg'])])
    submit = SubmitField(label='提交')


@app.route('/Stroke<username>', methods=['GET', 'POST'])
def Stroke(username):
    form = Submit_Picture()
    if request.method == 'POST':
        if 'modify' not in request.form:
            return '未正确上传图片'
        Picture = request.files['SubmitPicture']
        Time = time.localtime()
        CreateTime = time.strftime("%Y-%m-%d %H:%M:%S", Time)
        if Picture:
            is_Exist_Same_Name = PictureSet.query.filter_by(username=username, PictureName=Picture.filename).count()
            if is_Exist_Same_Name == 0:
                try:
                    new_picture = PictureSet(username=username, Picture=Picture, PictureName=Picture.filename
                                             , CreateTime=CreateTime)
                    db.session.add(new_picture)
                    db.session.commit()
                    flash('上传成功！请耐心等待！')
                    # 图片上传至后端
                    # 返回 ret_map
                    Back_End.start_project(Picture, username, Picture.filename)
                    return redirect(url_for('DIY', username=username, PictureName=Picture.filename))
                except:
                    flash("上传失败，可能的原因是：1.上传的图片格式非jpg 2.图片过大 3.图片不合规")
                    db.session.rollback()
            else:
                flash('有相同名字的图片！')
                db.session.rollback()
        else:
            flash('请上传图片！')
        # if request.method == 'POST':

    return render_template('Stroke.html', form=form, username=username)


""""""""""""""""""""""""
""" 这里是存放历史的代码 """
""""""""""""""""""""""""


@app.route('/history<username>', methods=['GET', 'POST'])
def history(username):
    base_path = f"static/data/{username}"
    has_work = True
    has_history = True
    # 将所有的作品文件的名字获取
    file_names = []
    file = os.listdir(base_path + "/GIF")
    # file.sort(key=lambda x: int(x.split('.')[0]))
    for filename in os.listdir(base_path + "/GIF"):
        if filename.endswith('.gif'):
            file_names.append(filename)
    if len(file_names) == 0:
        print("无作品目前")
        has_work = False
    data_list = []
    # gif = History.query.filter_by(username=username).all()[0]
    # gif_data = base64.b64encode(gif.Picture).decode('utf-8')
    # print(gif_data)
    gif_all = History.query.filter_by(username=username).all()
    if len(gif_all) == 0:
        print("无作品")
        has_history = False
    for i in range(len(gif_all)):
        gif = gif_all[i]
        gif_data = base64.b64encode(gif.Picture).decode('utf-8')
        data_list.append(gif_data)
        # print(gif_data)
    # return render_template('history.html', username=username, file_names=file_names, picture_list=gif_data)
    return render_template('history.html', username=username, file_names=file_names,
                           picture_list=data_list, has_work=has_work, has_history=has_history)


""""""""""""""""""""""""
""" 这里是墨客DIY界面的代码 """
""""""""""""""""""""""""


@app.route('/Stroke/DIY/<username>/<PictureName>', methods=['GET', 'POST'])
def DIY(username, PictureName):
    # print(basedir)
    picture_folder = f'static/data/{username}/Short_Skeleton'
    picture_path = os.listdir(picture_folder)
    picture_number = len(picture_path)
    base_path = f'static/data/{username}'
    # print(picture_path)
    # Stroke_Video_Generation.start_generate(username, PictureName, )
    with open(f'static/data/{username}/Short_Skeleton_data.csv', "r") as f:
        reader = csv.reader(f)
        # ret_map = csv.reader(f)
        ret_map = np.array(list(reader)).astype("int")
    ret_map = ret_map.reshape(-1)
    # data = request.json
    # print(type(ret_map))

    # picture_name =
    if request.method == 'POST':
        data = bytes.decode(request.data)[10: -2]

        index = data.index(',[')
        this_picture_number = int(data[:index])
        # 将字符串处理成二维数组
        stroke_string = data[index + 1:]
        stroke = eval(stroke_string)
        # print(stroke_string)
        # print(stroke)
        Stroke_Video_Generation.start_generate(username, PictureName, picture_number, base_path, this_picture_number,
                                               stroke)
        picture_list = base_path + '/Cutting'
        with open(picture_list + f'/{this_picture_number}.jpg', 'rb') as f:
            image = f.read()
            new_image = History(username=username, picture_name=PictureName, picture_id=this_picture_number, Picture=image, Picture_Stroke_list=stroke_string)
            db.session.add(new_image)
        db.session.commit()
        #
        # if this_picture_number + 1 == picture_number:
        #     for i in range(len(os.listdir(picture_list))):
        #         try:
        #             with open(picture_list + f'/{i}.jpg', 'rb') as f:
        #                 image = f.read()
        #                 new_image = History(username=username, picture_name=PictureName, picture_id=id, Picture=image, PictureList=)
        #                 id += 1
        #                 t += 1
        #                 print(t)
        #                 db.session.add(new_image)
        #         except:
        #             with open(picture_list + f'/{PictureName}.jpg', 'rb') as f:
        #                 image = f.read()
        #                 new_image = History(username=username, picture_name=PictureName, picture_id=id, Picture=image)
        #                 id += 1
        #                 t += 1
        #                 print(t)
        #                 db.session.add(new_image)
        #     db.session.commit()

    return render_template('DIY.html', username=username, picture_folder=picture_folder, picture_number=picture_number,
                           pitcure_path=picture_path, Stroke_Map=ret_map, PictureName=PictureName)


""""""""""""""""""""""""
""" 这里是招贤纳士的代码 """
""""""""""""""""""""""""


# 加入我们
@app.route('/contact')
def contact():
    return render_template('contact.html')


# 了解更多
@app.route('/more_info')
def more_info():
    return render_template('more_info.html')


# 成品展示
@app.route('/masterpiece')
def masterpiece():
    return render_template('masterpiece.html')


""""""""""""""""""""""""
""" 这里是墨客启动的代码 """
""""""""""""""""""""""""

if __name__ == '__main__':
    bootstrap.init_app(app)
    app.json.ensure_ascii = False  # 解决中文乱码问题
    app.run(debug=True)
