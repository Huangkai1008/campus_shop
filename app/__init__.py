"""
注册蓝图
"""
import os
import os.path as op

import sys


from flask_admin.model import BaseModelView
from jinja2 import Markup

from flask import Flask, render_template, url_for, redirect, request, abort, flash

from wtforms import form, fields, validators
import flask_login as login
import flask_admin as admin
from flask_admin import Admin, form
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import expose
from flask_babelex import Babel  # flask-admin的国际化

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.event import listens_for

from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db
from models import User, Product, Tag, Comment, AdminUser, Userlog
from home.forms import AdminLoginForm, RegistrationForm

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")  # 上传文件路径
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# file_path = op.join(op.dirname(__file__), 'static/uploads/products/')  # 商品文件上传路径
file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/products")

app = Flask(__name__)

babel = Babel(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FACE_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/users/")  # 头像路径

app.config['BABEL_DEFAULT_LOCALE'] = 'zh_CN'  # 修改后台翻译为中文

app.config.from_object('config')


def product_root():
    return file_path


app.jinja_env.globals.update(product_root=product_root)

"""
flask-login
"""


# 初始化flask-login


def init_login():
    login_manager = login.LoginManager()
    login_manager.login_view = 'adminuser.login'
    login_manager.login_message = u'请登录'
    login_manager.init_app(app)

    # 创建管理员加载函数
    @login_manager.user_loader
    def load_user(adminuser_id):
        return db.session.query(AdminUser).get(adminuser_id)


# 创建定制的model view class


class MyModelView(sqla.ModelView):
    """
    管理员视图并集成了flask-login的认证系统
    """
    can_create = False
    can_edit = False
    can_delete = False

    column_labels = {
        'id': u'编号',
        'name': u'昵称',
        'login': u'登录名',
        'email': u'邮箱',
        'password': u'密码'
    }

    column_exclude_list = ['name', 'password']   # 隐藏管理员密码字段

    column_filters = ['login', 'email']

    def is_accessible(self):
        return login.current_user.is_authenticated

    def on_model_change(self, form, model, is_created):
        AdminUser.password = form.password_hash.data


# 创建定制的flask-admin主页视图(注册和登录逻辑):
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=("GET", "POST"))
    def login_view(self):
        """管理员登录"""
        form = AdminLoginForm(request.form)
        if admin_helpers.validate_form_on_submit(form):
            adminuser = form.get_user()
            login.login_user(adminuser)
            flash(u'你已经成功登录')

        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        return self.render("admin/login.html", form=form)

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if admin_helpers.validate_form_on_submit(form):
            adminuser = AdminUser()

            form.populate_obj(adminuser)

            adminuser.password = generate_password_hash(form.password.data)

            db.session.add(adminuser)

            try:
                db.session.commit()
            except:
                db.session.rollback()

            login.login_user(adminuser)
            return redirect(url_for('.index'))
        return self.render("admin/register.html", form=form)

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# 初始化flask_login
init_login()

"""
flask-admin
"""


class UserAdmin(sqla.ModelView):
    """
    用户管理视图
    """
    def is_accessible(self):
        return login.current_user.is_authenticated

    can_create = False
    can_edit = False
    can_delete = False
    column_display_pk = True
    column_labels = {
        'id': u'编号',
        'name': u'昵称',
        'password': u'密码',
        'email': u'邮箱',
        'phone': u'手机号',
        'card': u'银行卡',
        'face': u'头像',
        'address': u'收货地址',
        'add_time': u'添加时间',
        'comments': u'评论'
    }

    column_list = ('id', 'name', 'email', 'phone', 'card', 'face', 'address', 'add_time')

    column_filters = ('name', 'phone', 'address', 'add_time')

    column_searchable_list = ['name', 'email', 'phone']


class ProductAdmin(sqla.ModelView):
    """
    商品管理视图
    """
    def is_accessible(self):
        return login.current_user.is_authenticated

    column_display_pk = True
    column_list = ('id', 'name', 'price', 'old_price', 'stock', 'sell', 'view_num', 'add_time', 'pic')
    column_labels = {
        'id': u'编号',
        'name': u'名称',
        'price': u'价格',
        'old_price': u'原价',
        'stock': u'库存',
        'sell': u'销量',
        'view_num': u'浏览量',
        'add_time': u'添加时间',
        'tag_id': u'分类',
        'tag': u'所属分类',
        'comments': u'评论',
        'pic': u'图片',
    }
    form_excluded_columns = ['comments', 'pic']

    column_filters = ('id', 'name', 'price', 'stock', 'sell', 'tag_id', 'view_num')

    column_searchable_list = ['name', 'id', 'price', 'stock', 'sell', 'tag_id']

    # 设置缩略图
    def _list_thumbnail(view, context, model, name):
        if not model.pic:
            return ''
        return Markup(
            '<img src="%s">' % url_for('static', filename=form.thumbgen_filename(model.pic)))
        print(filename)
    # 格式化列表图像显示
    column_formatters = {
        'pic': _list_thumbnail
    }
    # 扩展列表显示的头像为60*60像素
    form_extra_fields = {
        'pic': form.ImageUploadField(label=u'图像',
                                     base_path=file_path,
                                     relative_path="uploads/products/uploadFile/",
                                     thumbnail_size=(60, 60, True)
                                     )
    }

    @listens_for(Product, 'after_delete')
    def del_image(mapper, connection, target):
        if target.pic:
            # 删除图片
            try:
                os.remove(op.join(file_path, target.pic))
            except OSError:
                flash("删除图片出错")


            try:
                os.remove(op.join(file_path,
                                  form.thumbgen_filename(target.pic)))
            except OSError:
                flash("删除缩略图出错")


class UserlogAdmin(sqla.ModelView):
    """
    用户登录日志视图
    """
    def is_accessible(self):
        return login.current_user.is_authenticated

    can_create = False
    can_edit = False
    can_delete = False

    column_list = ('add_time', 'user_id')

    column_display_pk = True

    column_labels = {
        'add_time': u'登录时间',
        'user_id': u'所属用户'
    }

    column_searchable_list = ['user_id']


class TagAdmin(sqla.ModelView):
    """
    商品分类管理视图
    """

    def is_accessible(self):
        return login.current_user.is_authenticated

    column_list = ('name', 'add_time', 'products')

    column_labels = {
        'name': u'名称',
        'add_time': u'添加时间',
        'products': u'下属商品'
    }

    column_filters = ('name', 'add_time')

    column_searchable_list = ['name', 'add_time']


class CommentAdmin(sqla.ModelView):
    """
    评论管理视图
    """

    def is_accessible(self):
        return login.current_user.is_authenticated

    can_delete = False
    can_edit = False
    can_create = False
    column_labels = {
        'id': u'编号',
        'content': u'评论内容',
        'product_id': u'所属商品',
        'user_id': u'所属用户',
        'add_time': u'添加时间',
    }

    column_filters = ('content', 'add_time', 'product_id')

    column_searchable_list = ('content', 'add_time', 'product_id', 'user_id')


admin = Admin(app, name=u'校园商铺管理系统', template_mode='bootstrap3', index_view=MyAdminIndexView(), base_template='my\
_master.html')

admin.add_view(MyModelView(AdminUser, db.session, name=u'管理员管理'))
admin.add_view(UserAdmin(User, db.session, name=u'用户管理'))
admin.add_view(UserlogAdmin(Userlog, db.session, name=u'用户日志管理'))
admin.add_view(ProductAdmin(Product, db.session, name=u'商品管理'))
admin.add_view(TagAdmin(Tag, db.session, name=u'标签管理'))
admin.add_view(CommentAdmin(Comment, db.session, name=u'评论管理'))

# 开启调试模式
app.debug = False

from app.home import home as home_blueprint

app.register_blueprint(home_blueprint)

"""
定制错误界面
"""


@app.errorhandler(404)
def page_not_found(error):
    """
    404错误
    :param error:
    :return: home/404.html
    """
    return render_template("home/404.html"), 404