from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import check_password_hash

# 实例化app
appm = Flask(__name__)
appm.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:111111@127.0.0.1:3306/shop"
appm.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(appm)
migrate = Migrate(appm, db)

manager = Manager(appm)
manager.add_command('db', MigrateCommand)


class User(db.Model):
    """会员数据模型"""
    __tablename__ = "user"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 昵称
    name = db.Column(db.String(100), unique=True)
    # 密码字段
    password = db.Column(db.String(100))
    # 邮箱
    email = db.Column(db.String(100), unique=True)
    # 手机
    phone = db.Column(db.String(11), unique=True)
    # 银行卡
    card = db.Column(db.String(255), unique=True)
    # 头像
    face = db.Column(db.String(255))
    # 收货地址
    address = db.Column(db.String(255))
    # 收货学校以及楼层
    location = db.Column(db.String(255))
    # 个人简介
    info = db.Column(db.Text)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # 会员登录日志关系外联
    userlogs = db.relationship('Userlog', backref='user')
    # 用户评论外键关系关联
    comments = db.relationship('Comment', backref='user')
    # 用户购物车外键关系关联
    carts = db.relationship('Cart', backref='user')
    orders = db.relationship('Order', backref='user')

    def __repr__(self):
        return "<User %r>" % self.name

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Userlog(db.Model):
    """会员登录日志"""
    __tablename__ = "userlog"
    __table_args = {
        "useexisting": True
    }
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 所属会员外键
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 登录时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<User %r>" % self.id


class Product(db.Model):
    """商品数据模型"""
    __tablename__ = "product"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 名称
    name = db.Column(db.String(255), unique=True)
    # 价格
    price = db.Column(db.Float)
    # 打折折数
    discount = db.Column(db.Float, default=10)
    # 真实打折后价格
    true_price = db.Column(db.Float)
    # 是否一元秒杀区
    isKilled = db.Column(db.Boolean, default=False)
    # 库存
    stock = db.Column(db.Integer)
    # 销量
    sell = db.Column(db.Integer, default=0)
    # 图片
    pic = db.Column(db.String(255))
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # 商品浏览量
    view_num = db.Column(db.Integer, default=0)
    # 商品描述
    description = db.Column(db.Text)
    # 商品所属分类
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    # 商品评论外键关系关联
    comments = db.relationship("Comment", backref='product')
    cartinfos = db.relationship('CartInfo', backref='product')

    def __repr__(self):
        return "<Product %r>" % self.name


class Tag(db.Model):
    """商品属性分类"""
    __tablename__ = "tag"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 标题
    name = db.Column(db.String(100), unique=True)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # 商品外键关系关联
    products = db.relationship("Product", backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name


class Cart(db.Model):
    """购物车表"""
    __tablename__ = 'cart'
    # 购物车编号
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    cartinfos = db.relationship('CartInfo', backref='cart')

    def __repr__(self):
        return "<Cart %r>" % self.id


class CartInfo(db.Model):
    """购物车详情表"""
    __tablename__ = 'cartinfo'
    # 购物车详情编号
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 商品数量
    quantity = db.Column(db.Integer)
    # 商品名字
    product_name = db.Column(db.String(100))
    # 商品价格
    product_price = db.Column(db.Float)
    # 一栏小计
    total = db.Column(db.Float)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self):
        return "<CartInfo %r>" % self.id


class Order(db.Model):
    """订单表"""
    __tablename__ = "order"
    # 订单编号
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 订单所属用户
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 订单添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # 订单状态   0 入库待存   1  待付款   2 已付款
    status = db.Column(db.Integer, default=0)
    subTotal = db.Column(db.Float, default=0.0)
    # 订单详情信息关系关联
    orderinfo = db.relationship("OrderInfo", backref='order')

    def __repr__(self):
        return "<Order %r>" % self.id


class OrderInfo(db.Model):
    """订单明细表"""
    __tablename__ = "orderinfo"

    # 订单详情编号
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    # 商品数量
    quantity = db.Column(db.Integer)
    # 商品名字
    product_name = db.Column(db.String(100))
    # 商品价格
    product_price = db.Column(db.Float)
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)
    # 商品价格小计
    total = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    def __repr__(self):
        return "<OrderInfo %r>" % self.id


class Comment(db.Model):
    """评论"""
    __tablename__ = "comment"
    # 编号
    id = db.Column(db.Integer, primary_key=True)
    # 评论内容
    content = db.Column(db.Text)
    # 所属商品
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    # 所属用户
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 添加时间
    add_time = db.Column(db.DateTime, index=True, default=datetime.now)

    def __repr__(self):
        return "<Comment %r>" % self.id


class AdminUser(db.Model):
    """
    管理员
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(6000))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return "<Administrator %r>" % self.name


if __name__ == '__main__':
    manager.run()
