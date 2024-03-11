from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from wtforms import StringField, PasswordField, SubmitField  # 表单类型
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, EqualTo  # 验证数据不能为空
from flask_bootstrap import Bootstrap

""""""""""""""""""""""""
""" 这里是初始化的代码 """
""""""""""""""""""""""""

app = Flask(__name__, template_folder='templates', static_url_path='/')
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
    __tablename__ = 'customer'
    # 主键, ID 自动增长
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


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
                return redirect(url_for('Stroke', customer=username))
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
@app.route('/Stroke<customer>')
def Stroke(customer):
    return render_template('Stroke.html')


""""""""""""""""""""""""
""" 这里是招贤纳士的代码 """
""""""""""""""""""""""""


# 加入我们
@app.route('/contact')
def contact():
    return render_template('contact.html')


""""""""""""""""""""""""
""" 这里是墨客启动的代码 """
""""""""""""""""""""""""

if __name__ == '__main__':
    bootstrap.init_app(app)
    app.run(debug=True)
