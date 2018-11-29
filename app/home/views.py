import os
import datetime
import json
from functools import wraps  # 登录装饰器

from werkzeug.utils import secure_filename
from . import home
from flask import render_template, redirect, url_for, flash, session, request, jsonify
from werkzeug.security import generate_password_hash
from decimal import Decimal, ROUND_CEILING

from app import db, config

from home.forms import RegisterForm, LoginForm, UserForm, PasswordForm

from app.models import User, AdminUser, Userlog, Product, Tag, Order, OrderInfo, Cart, CartInfo, Comment


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # 上传通过检查

"""
    工具类型函数
"""


def allowed_file(filename):
    """
    上传通过检查
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def change_name(filename):
    """
    修改文件名称
    """
    file_info = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + file_info[-1]
    return filename


"""
    用户逻辑函数
"""


def user_login_dec(f):
    """
    登录装饰器
    已登录就可以访问，否则重定向至登录，next页面为当前请求的url
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for('home.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@home.route("/login/", methods=["GET", "POST"])
def login():
    """
    登录视图
    :return: login.html
    """
    if request.method == 'GET':  # get请求
        form = LoginForm()
        return render_template('home/login.html', form=form)
    else:   # post请求
        form = LoginForm(request.form)
        if form.validate_on_submit():
            data = form.data
            user = User.query.filter_by(name=data['name']).first()
            if user:
                if not user.check_password(data['password']):
                    flash("密码错误", 'err')
                    return redirect(url_for('home.login'))
            else:
                flash("输入的账户不存在", 'err')
                return redirect(url_for('home.login'))

            session['user'] = user.name
            session['user_id'] = user.id
            userlog = Userlog(
                user_id=user.id
            )
            db.session.add(userlog)
            db.session.commit()
            return redirect(url_for('home.user'))
        return render_template('home/login.html', form=form)


@home.route('/pay/', methods=['GET', 'POST'])
def pay():
    order_id = request.form['order_id']
    order_sub_total = request.form['order_sub_total']
    order = Order.query.filter(Order.id == order_id).first()
    order.status = 1
    db.session.commit()
    orderinfos = OrderInfo.query.filter(OrderInfo.order_id == order_id).all()
    for orderinfo in orderinfos:
        product = Product.query.filter(Product.id == orderinfo.product_id).first()
        product.stock = product.stock - orderinfo.quantity
        product.sell = product.sell + orderinfo.quantity
        db.session.commit()
    return render_template('home/pay.html', order_id=order_id, order_subTotal=order_sub_total)


@home.route('/pay_to/', methods=['GET', 'POST'])
def pay_to():
    order_id = request.form['order_id']
    order_subTotal = request.form['order_subTotal']
    order = Order.query.filter(Order.id == order_id).first()
    order.status = 1
    order.add_time = datetime.datetime.now()
    db.session.commit()
    orderinfos = OrderInfo.query.filter(OrderInfo.order_id == order_id).all()
    for orderinfo in orderinfos:
        product = Product.query.filter(Product.id == orderinfo.product_id).first()
        product.stock = product.stock - orderinfo.quantity
        product.sell = product.sell + orderinfo.quantity
        db.session.commit()
    return render_template('home/pay.html', order_id=order_id, order_subTotal=order_subTotal)


@home.route("/register/", methods=["GET", "POST"])
def register():
    """
    注册视图
    :return: register.html
    """
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            password=generate_password_hash(data["password"])
        )
        db.session.add(user)
        db.session.commit()
        #     数据库事务回滚
        # except
        #     db.session.rollback()

        flash("你已经成功注册", "ok")

    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_dec
def user():
    """
    用户信息中心视图
    :return: user.html
    """
    form = UserForm()
    user = User.query.get(int(session['user_id']))
    form.face.validators = []
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.card.data = user.card
        form.info.data = user.info
        form.address.data = user.address
        form.location.data = user.location
    if form.validate_on_submit():
        data = form.data
        if form.face.data != "":
            file_face = secure_filename(form.face.data.filename)
            if not os.path.exists(config.FACE_FOLDER):
                os.makedirs(config.FACE_FOLDER)
                os.chmod(config.FACE_FOLDER)
            user.face = change_name(file_face)
            form.face.data.save(config.FACE_FOLDER + user.face)

        name_count = User.query.filter_by(name=data['name']).count()
        if data['name'] != user.name and name_count == 1:
            flash("用户名已经存在", 'err')
            return redirect(url_for('home.user'))

        email_count = User.query.filter_by(email=data['email']).count()
        if data['email'] != user.email and email_count == 1:
            flash("邮箱已经存在", 'err')
            return redirect(url_for('home.user'))

        phone_count = User.query.filter_by(phone=data['phone']).count()
        if data['phone'] != user.phone and phone_count == 1:
            flash("手机号码已经存在", 'err')
            return redirect(url_for('home.user'))

        card_count = User.query.filter_by(card=data['card']).count()
        if data['card'] != user.card and card_count == 1:
            flash("银行卡号码已经存在", 'err')
            return redirect(url_for('home.user'))

        user.name = data['name']
        user.email = data['email']
        user.phone = data['phone']
        user.card = data['card']
        user.info = data['info']
        user.address = data['address']
        user.location = data['location']

        db.session.add(user)
        try:
            db.session.commit()
        except:
            db.session.rollback()

        flash("你的信息已经修改成功", 'ok')
        return redirect(url_for('home.user'))

    return render_template("home/user.html", form=form, user=user)


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_dec
def pwd():
    """
    修改密码视图
    :return:  pwd.html
    """
    form = PasswordForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=session["user"]).first()
        if not user.check_password(data["old_password"]):
            flash("旧密码错误", "error")
            return redirect(url_for('home.pwd'))
        user.pwd = generate_password_hash(data["new_password"])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home.login'))
    return render_template("home/pwd.html", form=form)


@home.route("/logout/")
def logout():
    """
    退出登录视图
    :return: redirect to login
    """
    session.pop("user", None)
    session.pop("user_id", None)

    return redirect(url_for('home.login'))


"""
    商品逻辑函数
"""


@home.route("/", methods=['GET'])
def index():
    """
    商品首页视图
    """
    tags = Tag.query.all()
    total = Product.query.all()
    total = len(total)
    discounts = Product.query.filter(Product.discount < 10).all()
    for discount in discounts:
        # discount.sale_price = discount.price * discount.discount * 0.1
        discount.true_price = Decimal(discount.price * discount.discount * 0.1).quantize(Decimal('0.00'), ROUND_CEILING)
        # db.session.commit()
    one_dollers = Product.query.filter(Product.isKilled is True).all()
    return render_template("home/index.html", tags=tags, total=total, discounts=discounts, one_dollers=one_dollers)


@home.route("/news/", methods=['GET'])
def new_product():
    """
    新品视图
    """
    page = request.args.get("page", 1, type=int)
    page_data = Product.query.order_by(Product.add_time.desc())
    page_data = page_data.paginate(page=page, per_page=8, error_out=False)
    news = page_data.items
    return render_template("home/news.html", news=news, page_data=page_data, page=page)


@home.route("/all_product/", methods=['GET'])
def all_product():
    page = request.args.get("page", 1, type=int)
    page_data = Product.query
    page_data = page_data.paginate(page=page, per_page=8, error_out=False)
    products = page_data.items
    return render_template("home/all_product.html", products=products, page_data=page_data, page=page)


@home.route('/guess_like/', methods=['GET'])
def guess_like():
    """
    商品推荐视图
    """
    page = request.args.get('page', 1, type=int)
    if "user" not in session:
        page_data = Product.query.order_by(Product.sell.desc())
        page_data = page_data.paginate(page=page, per_page=8, error_out=False)
        likes = page_data.items
    else:
        user = User.query.filter(User.id == session.get('user_id')).first()
        orders = Order.query.filter(Order.user_id == user.id).all()
        for order in orders:
            orderinfos = OrderInfo.query.filter(OrderInfo.order_id == order.id).all()
            for orderinfo in orderinfos:
                product_count = Product.query.filter(Product.id == orderinfo.product_id).count()


@home.route("/hot_sale/", methods=['GET'])
def hot_sale():
    """
    热销商品视图
    """
    # hots = Product.query.order_by('sell desc').all()
    page = request.args.get("page", 1, type=int)
    page_data = Product.query.order_by(Product.sell.desc())
    page_data = page_data.paginate(page=page, per_page=8, error_out=False)
    hots = page_data.items
    # print(hots)
    return render_template("home/hot_sale.html", hots=hots, page_data=page_data, page=page)


@home.route('/detail/<product_id>/')
def detail(product_id):
    """
    正常状态下商品详情视图
    """
    comments_num = Comment.query.join(Product).filter(Product.id == product_id).count()
    product_model = Product.query.filter(Product.id == product_id).first()
    return render_template('home/detail.html', product=product_model, comments_num=comments_num)


@home.route('/detail_onsale/<product_id>/')
def detail_onsale(product_id):
    """
    活动状态下商品详情视图
    """
    comments = Comment.query.join(Product).filter(Product.id == product_id).all()
    users = User.query.all()
    comments_num = Comment.query.join(Product).filter(Product.id == product_id).count()
    product_model = Product.query.filter(Product.id == product_id).first()
    return render_template('home/detail_onsale.html', product=product_model, comments_num=comments_num,
                           comments=comments, users=users)


@home.route('/category/<tag_id>/', methods=['GET'])
def category(tag_id):
    """
    商品分类视图
    """
    tag = Tag.query.filter(Tag.id == tag_id).first()
    product_cate = Product.query.join(Tag).filter(Tag.id == tag_id).all()
    return render_template('home/category.html', product_cate=product_cate, tag=tag)


@home.route('/search/<int:page>/')
def search(page=None):
    """
        搜索界面
    """
    if page is None:
        page = 1
    key = request.args.get('key', '')
    product_count = Product.query.filter(Product.name.ilike('%' + key + '%')).count()
    page_data = Product.query.filter(Product.name.ilike('%' + key + '%')). \
        order_by(Product.add_time.desc()).paginate(page=page, per_page=10)
    page_data.key = key
    return render_template('home/search.html', product_count=product_count, key=key, page_data=page_data)


@home.route('/checkout/')
def checkout():
    """
        购物车
    """
    return render_template('home/checkout.html')


@home.route('/cart/', methods=['POST'])
def cart():
    if "user" not in session:
        flash("请登录后再试")
    else:
        user = User.query.filter(User.id == session.get('user_id')).first()
        cart = Cart.query.filter(Cart.user_id == user.id).first()
        if cart is None:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()
            # 得到传来的json数据
            data = json.loads(request.form.get('data'))
            # 得到商品的名称
            name = data["itemName"]
            # 得到商品实际付的价格
            price = float(data["itemPrice"])
            # 得到商品的数量
            quantity = int(data["itemQty"])
            # 得到商品的总价
            total = data['itemTotal'].strip('￥')
            cart_infos = dict()
            cart_infos['name'] = name
            cart_infos['price'] = price
            cart_infos['quality'] = quantity
            cart_infos['total'] = total
            product = Product.query.filter(Product.name == name).first()
            cart_info = CartInfo(quantity=quantity, product_name=name, cart_id=cart.id,
                                 product_id=product.id, product_price=price, total=total)
            db.session.add(cart_info)

            try:
                db.session.commit()
            except:
                db.session.rollback()

        else:
            # 得到传来的json数据
            data = json.loads(request.form.get('data'))
            # 得到商品的名称
            name = data["itemName"]
            # 得到商品实际付的价格
            price = float(data["itemPrice"])
            # 得到商品的数量
            quantity = int(data["itemQty"])
            # 得到商品的总价
            total = data['itemTotal'].strip('￥')
            cart_infos = dict()
            cart_infos['name'] = name
            cart_infos['price'] = price
            cart_infos['quality'] = quantity
            cart_infos['total'] = total
            # 得到当前session中登录的用户
            product = Product.query.filter(Product.name == name).first()
            cart_info = CartInfo(quantity=quantity, product_name=name, cart_id=cart.id,
                                 product_id=product.id, product_price=price, total=total)
            db.session.add(cart_info)
            try:
                db.session.commit()
            except:
                db.session.rollback()

        return jsonify(cart_infos)


@home.route('/order/', methods=['GET', 'POST'])
def order():
    # 得到当前访问的订单所属用户
    user = User.query.filter(User.id == session.get('user_id')).first()
    order = Order.query.filter(Order.user_id == user.id).first()

    order = Order(user_id=user.id, subTotal=0)
    db.session.add(order)
    db.session.commit()
    # cartinfos = CartInfo.query.join(Cart).filter(Cart.user_id == user.id).all()
    cartinfos = CartInfo.query.join(Cart).filter(Cart.user_id == session.get('user_id')).all()
    orderinfos = list()

    for cartinfo in cartinfos:

        orderinfo = OrderInfo(quantity=cartinfo.quantity, product_name=cartinfo.product_name, order_id=order.id,
                              product_id=cartinfo.product_id, product_price=cartinfo.product_price, total=
                              cartinfo.total)
        db.session.add(orderinfo)
        db.session.delete(cartinfo)
        # db.session.commit()
        # try:
        #     db.session.commit()
        # except:
        #     db.session.rollback()
        order.subTotal = order.subTotal + orderinfo.total


    cart = Cart.query.filter(Cart.user_id == session.get('user_id')).first()

    orderinfos = OrderInfo.query.join(Order).filter(Order.id == order.id).all()

    # db.session.delete(cart)
    db.session.commit()
    # orderinfos = OrderInfo.query.join(Order).filter(Order.user_id == user.id).all()
    # orderinfos = OrderInfo.query.join(Order).filter(Order.id == order.id).all()

    # else:
    #
    #     cartinfos = CartInfo.query.join(Cart).filter(Cart.user_id == user.id).all()
    #     for cartinfo in cartinfos:
    #         orderinfo = OrderInfo(quantity=cartinfo.quantity, product_name=cartinfo.product_name, order_id=order.id,
    #                               product_id=cartinfo.product_id, product_price=cartinfo.product_price,
    #                               total=cartinfo.total)
    #         db.session.add(orderinfo)
    #         db.session.delete(cartinfo)
    #         try:
    #             db.session.commit()
    #         except:
    #             db.session.rollback()
    #         order.subTotal = order.subTotal + orderinfo.total
    #
    #     cart = Cart.query.filter(Cart.user_id == user.id).first()
    #
    #     db.session.delete(cart)
    #     db.session.commit()
    #
    #     orderinfos = OrderInfo.query.join(Order).filter(Order.user_id == user.id).all()
    return render_template('home/order.html', user=user, order=order, orderinfos=orderinfos)


@home.route('/order_manage/', methods=['GET', 'POST'])
def order_manage():
    # 得到当前用户的信息
    user = User.query.filter(User.id == session.get('user_id')).first()
    # 得到所有订单的list
    orders = Order.query.filter(Order.user_id == user.id).order_by(Order.add_time.desc()).all()
    order_infos = OrderInfo.query.all()
    products = Product.query.all()
    # 得到未付款订单的list
    order_nopays = Order.query.filter(Order.user_id == user.id, Order.status == 0).order_by(Order.add_time.desc()).all()
    # 得到已付款订单的list
    order_haspays = Order.query.filter(Order.user_id == user.id, Order.status == 1).order_by(Order.add_time.desc()).all()
    return render_template('home/ordermanage.html', orders=orders, order_infos=order_infos, products=products
                           , order_nopays=order_nopays, order_haspays=order_haspays)
