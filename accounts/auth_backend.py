from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
import logging

# 初始化日志记录器
logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    """
    自定义认证后端，支持通过用户名、邮箱或手机登录。
    """
    def authenticate(self, request, login_field=None, password=None, **kwargs):
        """
        认证用户，验证 login_field 和 password。

        参数:
            request: HTTP 请求对象
            login_field: 用户输入的用户名、邮箱或手机
            password: 用户输入的密码
            **kwargs: 其他参数（兼容默认后端）

        返回:
            User 对象（成功）或 None（失败）
        """
        # 获取用户模型（CustomUser）
        UserModel = get_user_model()

        # 检查输入是否为空
        if not login_field or not password:
            logger.error("认证失败: login_field 或 password 为空")
            return None

        # 清理 login_field，去除首尾空格
        login_field = login_field.strip()
        logger.debug(f"尝试认证: login_field={login_field}")

        try:
            # 查询匹配用户名、邮箱（忽略大小写）或手机的用户
            user = UserModel.objects.get(
                Q(username=login_field) |
                Q(email__iexact=login_field) |
                Q(phone=login_field)
            )
            # 验证密码
            if user.check_password(password):
                logger.info(f"认证成功: 用户 {user.username}")
                return user
            else:
                logger.error(f"认证失败: 密码错误 for {login_field}")
                return None
        except UserModel.DoesNotExist:
            logger.error(f"认证失败: 用户不存在 for {login_field}")
            return None
        except UserModel.MultipleObjectsReturned:
            logger.error(f"认证失败: 多个用户匹配 for {login_field}")
            return None