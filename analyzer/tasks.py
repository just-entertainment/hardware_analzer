# analyzer/tasks.py

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from analyzer.models import PriceChangeNotification, CustomUser
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)

@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_price_update_notification(user_id, component_type, component_id, component_title, current_price, previous_price, detail_url):
    print('进入tasks函数')
    """异步发送价格更新通知邮件"""
    try:
        user = CustomUser.objects.get(id=user_id)
        print(user)
        subject = f"您收藏的配件 {component_title} 价格发生变化！"
        print(subject)

        # 纯文本内容
        text_content = (
            f"您收藏的配件 {component_title} 添加了新的价格记录！\n\n"
            f"当前价格：¥{current_price:.2f}\n"
        )
        if previous_price is not None:
            text_content += f"前一天价格：¥{previous_price:.2f}\n"
        text_content += f"查看详情：{detail_url}\n"

        # HTML 内容
        html_content = render_to_string('email/price_update.html', {
            'component_title': component_title,
            'current_price': current_price,
            'previous_price': previous_price,
            'detail_url': detail_url,
        })

        # 发送邮件
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=None,  # 使用 settings.DEFAULT_FROM_EMAIL
            to=[user.email],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=False)

        # 记录通知
        content_type = ContentType.objects.get(app_label='analyzer', model=component_type)
        PriceChangeNotification.objects.create(
            user=user,
            content_type=content_type,
            object_id=component_id,
            current_price=current_price,
            previous_price=previous_price if previous_price is not None else current_price,
            notified_at=timezone.now()
        )

        logger.info(f"Notification sent to {user.email} for {component_title}")
    except Exception as e:
        logger.error(f"Failed to send notification for {component_title} to user_id {user_id}: {str(e)}", exc_info=True)
        raise  # 触发 Celery 重试