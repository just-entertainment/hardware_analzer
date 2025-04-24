from celery import shared_task
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from .models import Favorite,  PriceHistory, PriceAlert
from django.utils import timezone
import logging
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

# 初始化日志记录器
logger = logging.getLogger(__name__)

# 阿里云 SMS 配置（替换为你的密钥和模板）
ALICLOUD_ACCESS_KEY = 'your_access_key'
ALICLOUD_ACCESS_SECRET = 'your_access_secret'
ALICLOUD_SIGN_NAME = 'your_sign_name'
ALICLOUD_TEMPLATE_CODE = 'your_template_code'

@shared_task
def check_price_drops():
    """
    定时任务：检查收藏的硬件价格是否降低，并发送邮件或短信通知。
    """
    logger.info("开始检查硬件价格降价")
    # 获取 Hardware 的 ContentType
    hardware_content_type = ContentType.objects.get_for_model(Hardware)

    # 遍历所有收藏的硬件
    favorites = Favorite.objects.filter(content_type=hardware_content_type).select_related('user', 'content_object')
    for favorite in favorites:
        hardware = favorite.content_object
        user = favorite.user

        # 获取最近的价格历史
        latest_price_history = PriceHistory.objects.filter(
            component_type=hardware.component_type,
            component_id=hardware.product_id
        ).order_by('-date').first()

        if latest_price_history and hardware.current_price < latest_price_history.price:
            # 检测到降价
            price_drop = latest_price_history.price - hardware.current_price
            logger.info(f"检测到降价: {hardware.title} 从 {latest_price_history.price} 降到 {hardware.current_price}")

            # 创建降价提醒记录
            alert = PriceAlert.objects.create(
                user=user,
                favorite=favorite,
                previous_price=latest_price_history.price,
                current_price=hardware.current_price,
                method='email'
            )

            # 发送邮件通知
            subject = f"硬件降价提醒: {hardware.title}"
            message = (
                f"尊敬的 {user.username}，\n\n"
                f"您收藏的硬件 {hardware.title} 已降价！\n"
                f"- 之前价格: ￥{latest_price_history.price}\n"
                f"- 当前价格: ￥{hardware.current_price}\n"
                f"- 降价幅度: ￥{price_drop}\n\n"
                f"点击查看详情: {hardware.jd_url}\n\n"
                f"感谢使用配件分析平台！"
            )
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=None,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                logger.info(f"邮件发送成功: {user.email}")
            except Exception as e:
                logger.error(f"邮件发送失败: {user.email}, 错误: {str(e)}")
                alert.delete()

            # 发送短信通知（可选）
            try:
                client = AcsClient(ALICLOUD_ACCESS_KEY, ALICLOUD_ACCESS_SECRET, 'cn-hangzhou')
                request = SendSmsRequest()
                request.set_accept_format('json')
                request.set_SignName(ALICLOUD_SIGN_NAME)
                request.set_TemplateCode(ALICLOUD_TEMPLATE_CODE)
                request.set_PhoneNumbers(user.phone)
                request.set_TemplateParam({
                    "product": hardware.title,
                    "price": str(hardware.current_price)
                })
                response = client.do_action_with_exception(request)
                logger.info(f"短信发送成功: {user.phone}")
                alert.method = 'sms'
                alert.save()
            except Exception as e:
                logger.error(f"短信发送失败: {user.phone}, 错误: {str(e)}")