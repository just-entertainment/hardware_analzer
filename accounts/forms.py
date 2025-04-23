from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.db.models import Q
import logging

# 初始化日志记录器
logger = logging.getLogger(__name__)

class CustomUserCreationForm(UserCreationForm):
    """
    用户注册表单，支持 username、email、phone、avatar 和密码。
    """
    phone = forms.CharField(max_length=15, required=True, label="手机号码")
    avatar = forms.ImageField(required=False, label="头像")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'avatar', 'password1', 'password2')

    def clean_phone(self):
        """验证手机号码：唯一、数字、至少10位"""
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("此手机号码已被使用")
        if not phone.isdigit() or len(phone) < 10:
            raise ValidationError("请输入有效的手机号码（至少10位数字）")
        return phone

    def clean_email(self):
        """验证邮箱：唯一，转换为小写"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email.lower()).exists():
            raise ValidationError("此邮箱已被使用")
        return email.lower()

    def clean_password1(self):
        """验证密码：至少8位，含字母和数字"""
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError("密码长度必须至少8位")
        if not any(c.isdigit() for c in password1):
            raise ValidationError("密码必须包含数字")
        if not any(c.isalpha() for c in password1):
            raise ValidationError("密码必须包含字母")
        return password1

    def save(self, commit=True):
        """保存用户，确保密码哈希和字段正确设置"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(forms.Form):
    """
    登录表单，支持用户名、邮箱或手机登录，直接查询 CustomUser。
    """
    login_field = forms.CharField(max_length=254, label="用户名/邮箱/手机")
    password = forms.CharField(widget=forms.PasswordInput, label="密码")

    def clean(self):
        """验证登录凭据，直接查询 CustomUser"""
        cleaned_data = super().clean()
        login_field = cleaned_data.get('login_field')
        password = cleaned_data.get('password')

        if login_field and password:
            login_field = login_field.strip()
            logger.debug(f"尝试认证: login_field={login_field}")
            try:
                # 直接查询 CustomUser
                user = CustomUser.objects.get(
                    Q(username=login_field) |
                    Q(email__iexact=login_field) |
                    Q(phone=login_field)
                )
                # 验证密码
                if user.check_password(password):
                    logger.info(f"认证成功: 用户 {user.username}")
                    self.user = user
                else:
                    logger.error(f"认证失败: 密码错误 for {login_field}")
                    raise ValidationError("用户名、邮箱或手机与密码不匹配")
            except CustomUser.DoesNotExist:
                logger.error(f"认证失败: 用户不存在 for {login_field}")
                raise ValidationError("用户名、邮箱或手机与密码不匹配")
            except CustomUser.MultipleObjectsReturned:
                logger.error(f"认证失败: 多个用户匹配 for {login_field}")
                raise ValidationError("用户名、邮箱或手机与密码不匹配")
        return cleaned_data

class CustomUserChangeForm(forms.ModelForm):
    """
    用户资料编辑表单，支持修改 username、email、phone、avatar。
    """
    phone = forms.CharField(max_length=15, required=True, label="手机号码")
    avatar = forms.ImageField(required=False, label="头像")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'avatar')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': '用户名'}),
            'email': forms.EmailInput(attrs={'placeholder': '邮箱'}),
            'phone': forms.TextInput(attrs={'placeholder': '手机号码'}),
        }

    def clean_phone(self):
        """验证手机号码：唯一、数字、至少10位"""
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise ValidationError("此手机号码已被使用")
        if not phone.isdigit() or len(phone) < 10:
            raise ValidationError("请输入有效的手机号码（至少10位数字）")
        return phone

    def clean_email(self):
        """验证邮箱：唯一，转换为小写"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email.lower()).exclude(pk=self.instance.pk).exists():
            raise ValidationError("此邮箱已被使用")
        return email.lower()