from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, validators, HiddenField
from wtforms.validators import DataRequired, Email, Regexp, ValidationError, EqualTo, Length
from app.models import User, AdminUser, db
from werkzeug.security import generate_password_hash, check_password_hash


class RegisterForm(FlaskForm):
    """
    注册表单
    """
    name = StringField(
        label="用户名",
        validators=[
            DataRequired("用户名不能为空!")
        ],
        description="用户名",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入你的用户名",
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空！"),
            Email("输入的邮箱格式不正确")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入你的邮箱地址",
        }
    )

    phone = StringField(
        label="手机",
        validators=[
            DataRequired("手机号不能为空！"),
            Regexp("1[3458]\\d{9}", message="输入的手机号格式不正确！")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入你的手机号",
        }
    )

    password = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空！"),
            Length(min=6, message="密码长度不能小于%(min)d位")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入你的密码",
        }
    )

    re_password = PasswordField(
        label="确认密码",
        validators=[
            DataRequired("请输入确认密码"),
            EqualTo('password', message="两次密码不一致")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请确认你的密码",
        }
    )

    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-warning btn-block",
        }
    )

    def validate_name(self, field):
        """
        注册验证用户名的重复性
        """
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("用户名已经存在")

    def validate_email(self, field):
        """
        注册验证邮箱的唯一性
        """
        email = field.data
        user = User.query.filter_by(email=email).count()
        if user == 1:
            raise ValidationError("邮箱已经存在")

    def validate_phone(self, field):
        """
        注册验证手机号码的唯一性
        """
        phone = field.data
        user = User.query.filter_by(phone=phone).count()
        if user == 1:
            raise ValidationError("手机号码已经存在！")


class LoginForm(FlaskForm):
    """
    登录表单
    """
    name = StringField(
        label="用户名",
        validators=[
            DataRequired("用户名不能为空")
        ],
        description="用户名",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入用户信息",
        }
    )

    password = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空"),
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码",
        }
    )

    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-warning btn-block",
        }
    )


class UserForm(FlaskForm):
    """
    用户中心表单
    """
    name = StringField(
        label="用户名",
        validators=[
            DataRequired("用户名不能为空")
        ],
        description="用户名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入用户名",
        }
    )

    email = StringField(
        label="邮箱",
        validators=[
            DataRequired("邮箱不能为空")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入邮箱",
        }
    )

    phone = StringField(
        label="手机号",
        validators=[
            DataRequired("手机号不能为空"),
            Regexp("1[3458]\\d{9}", message="手机号格式不正确！")
        ],
        description="手机号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入手机号",
        }
    )

    card = StringField(
        label="银行卡",
        description="银行卡",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入银行卡号",
        }
    )

    face = FileField(
        label="头像",
        validators=[
            DataRequired("请上传头像")
        ],
        description="头像",
        render_kw={
            "class": "form-control",
            "placeholder": "请上传头像",
        }
    )

    address = StringField(
        label="收货地址",
        validators=[
            DataRequired("请添加收货地址")
        ],
        description="收货地址",
        render_kw={
            "class": "form-control",
            "data-toggle": "city-picker",
        }
    )

    location = StringField(
        label="学校楼层",
        validators=[
            DataRequired("请填写你的学校与宿舍楼层")
        ],
        description="学校楼层",
        render_kw={
            "class": "form-control",
            "placeholder": "请填写学校与宿舍楼层",
        }
    )

    info = TextAreaField(
        label="简介",
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10,
        }
    )

    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-warning",
        }
    )


class PasswordForm(FlaskForm):
    """
    修改密码表单
    """
    old_password = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("旧密码不能为空")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码",
        }
    )

    new_password = PasswordField(
        label="新密码",
        validators=[
            DataRequired("新密码不能为空"),
            Length(min=6, message="密码长度不能小于%(min)d位")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码",
        }
    )

    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-warning"
        }
    )


# 为flask-login添加注册和登录表单
class AdminLoginForm(FlaskForm):
    login = StringField(
        label="管理员登录",
        validators=[
            DataRequired("管理员账号不能为空")
        ],
        description="管理员登录",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入你的用户名",
        }

    )

    password = PasswordField(
        label="密码",
        validators=[
            DataRequired("密码不能为空")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入你的密码",
        }

    )

    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-success btn-lg active"
        }
    )

    def validate_login(self, field):
        adminuser = self.get_user()

        if adminuser is None:
            raise validators.ValidationError(u'账号不存在')

        if not check_password_hash(adminuser.password, self.password.data):
            raise validators.ValidationError(u'不合法的密码')

    def get_user(self):
        return db.session.query(AdminUser).filter_by(login=self.login.data).first()


class RegistrationForm(FlaskForm):
    login = StringField(
        label="管理员注册登录名",
        validators=[
            DataRequired("登录名不能为空")
        ],
        description="管理员注册",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入你的登录名",
        }
    )

    email = StringField(
        label="邮箱名",
        validators=[
            DataRequired("邮箱不能为空")
        ],
        description="管理员注册邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入你的邮箱",
        }
    )

    password = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("密码不能为空")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入你的密码",
        }
    )

    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-success btn-lg active"
        }
    )

    def validate_login(self, field):
        if db.session.query(AdminUser).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError(u'重复的登录用户')

