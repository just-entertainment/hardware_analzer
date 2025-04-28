# analyzer/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from analyzer.models import (
    ChassisPriceHistory, CPUPriceHistory, RAMPriceHistory, SSDPriceHistory,
    MotherboardPriceHistory, GPUPriceHistory, CoolerPriceHistory, Favorite,
    PriceChangeNotification
)
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)

# 支持的硬件历史价格模型
PRICE_HISTORY_MODELS = [
    ChassisPriceHistory,
    CPUPriceHistory,
    RAMPriceHistory,
    SSDPriceHistory,
    MotherboardPriceHistory,
    GPUPriceHistory,
    CoolerPriceHistory,
]

# 定义组件类型到历史价格模型的映射
COMPONENT_PRICE_HISTORY_MODELS = {
    'cpu': CPUPriceHistory,
    'ram': RAMPriceHistory,
    'gpu': GPUPriceHistory,
    'motherboard': MotherboardPriceHistory,
    'ssd': SSDPriceHistory,
    'cooler': CoolerPriceHistory,
    'chassis': ChassisPriceHistory,
}


@receiver(post_save, sender=None)
def price_history_created(sender, instance, created, **kwargs):
    """当新的历史价格记录创建时，发送邮件通知"""
    if sender not in PRICE_HISTORY_MODELS or not created:
        return

    # 获取组件类型和实例
    component_type = None
    component = None
    price = instance.price
    for key, model in COMPONENT_PRICE_HISTORY_MODELS.items():
        if sender == model:
            component_type = key
            field_name = key if key != 'chassis' else 'chassis'
            try:
                component = getattr(instance, field_name)
            except AttributeError:
                logger.error(f"Invalid field_name {field_name} for {sender.__name__}")
                return
            break

    if not component_type or not component:
        logger.warning(f"No component found for {sender.__name__}")
        return

    # 查找收藏该配件的用户
    content_type = ContentType.objects.get_for_model(component)
    favorites = Favorite.objects.filter(
        content_type=content_type,
        object_id=component.id
    )

    if not favorites:
        logger.info(f"No favorites found for {component.title} ({component_type})")
        return

    # 获取前一天的价格（如果有）
    previous_price = None
    previous_record = sender.objects.filter(
        **{field_name: component},
        date__lt=instance.date
    ).order_by('-date').first()
    if previous_record:
        previous_price = previous_record.price

    # 检查是否需要通知（价格变化或新记录）
    for favorite in favorites:
        user = favorite.user
        # 检查最近 24 小时内是否已通知
        recent_notification = PriceChangeNotification.objects.filter(
            user=user,
            content_type=content_type,
            object_id=component.id,
            notified_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        if not recent_notification:
            # 准备邮件内容
            subject = f"您收藏的配件 {component.title} 价格发生变化！"
            detail_url = f"http://127.0.0.1:8000//"

            # 纯文本内容
            text_content = (
                f"您收藏的配件 {component.title} 添加了新的价格记录！\n\n"
                f"当前价格：¥{float(price):.2f}\n"
            )
            if previous_price is not None:
                text_content += f"前一天价格：¥{float(previous_price):.2f}\n"
            text_content += f"查看详情：{detail_url}\n"

            # HTML 内容
            html_content = render_to_string('email/price_update.html', {
                'component_title': component.title,
                'current_price': float(price),
                'previous_price': float(previous_price) if previous_price is not None else None,
                'detail_url': detail_url,
            })

            # 发送邮件
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=None,  # 使用 settings.DEFAULT_FROM_EMAIL
                    to=[user.email],
                )
                email.attach_alternative(html_content, 'text/html')
                email.send(fail_silently=False)

                # 记录通知
                PriceChangeNotification.objects.create(
                    user=user,
                    content_type=content_type,
                    object_id=component.id,
                    current_price=price,
                    previous_price=previous_price if previous_price is not None else price,
                    notified_at=timezone.now()
                )
                logger.info(f"Notification sent to {user.email} for {component.title}")
            except Exception as e:
                logger.error(f"Failed to send notification for {component.title} to {user.email}: {str(e)}")