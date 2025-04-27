from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from analyzer.models import Favorite, PriceChangeNotification, GPUPriceHistory, MotherboardPriceHistory, \
    SSDPriceHistory, CoolerPriceHistory, ChassisPriceHistory
from datetime import timedelta
import logging

from analyzer.models import Favorite, PriceChangeNotification,  CPUPriceHistory, \
    RAMPriceHistory
from datetime import timedelta
COMPONENT_PRICE_HISTORY_MODELS = {
    'cpu': CPUPriceHistory,
    'ram': RAMPriceHistory,
    'gpu': GPUPriceHistory,
    'motherboard': MotherboardPriceHistory,
    'ssd': SSDPriceHistory,
    'cooler': CoolerPriceHistory,
    # 'power_supply': PowerSupplyPriceHistory,
    'case': ChassisPriceHistory,
}

logger = logging.getLogger(__name__)
@shared_task
def check_price_changes():
    logger.info("Starting check_price_changes task")
    for favorite in Favorite.objects.select_related('user', 'content_type').all():
        try:
            user = favorite.user
            logger.info(f"Processing favorite {favorite.id} for user {user.phone}, component_type: {favorite.content_type.model}")
            component_type = favorite.content_type.model
            item = favorite.content_object  # 修复：使用 content_object
            if not item:
                logger.warning(f"Item not found for favorite {favorite.id}")
                continue
            price_history_model = COMPONENT_PRICE_HISTORY_MODELS.get(component_type)
            if not price_history_model:
                logger.warning(f"No price history model for {component_type}")
                continue
            latest_price_record = price_history_model.objects.filter(
                **{component_type: item}
            ).order_by('-date').first()
            current_price = latest_price_record.price if latest_price_record else (item.jd_price or item.reference_price)
            if not current_price:
                logger.warning(f"No current price for item {item.title}")
                continue
            previous_price_record = price_history_model.objects.filter(
                **{component_type: item},
                date__lt=latest_price_record.date if latest_price_record else timezone.now().date()
            ).order_by('-date').first()
            previous_price = previous_price_record.price if previous_price_record else current_price
            logger.info(f"Item {item.title}: current_price={current_price}, previous_price={previous_price}")
            if current_price != previous_price:
                recent_notification = PriceChangeNotification.objects.filter(
                    user=user,
                    content_type=favorite.content_type,
                    object_id=favorite.object_id,
                    notified_at__gte=timezone.now() - timedelta(days=1)
                ).exists()
                if not recent_notification:
                    logger.info(f"Sending email for {item.title} to {user.email}")
                    subject = f'价格变化通知：{item.title}'
                    message = (
                        f'您收藏的配件 {item.title} 价格发生变化！\n'
                        f'当前价格：¥{current_price}\n'
                        f'前一天价格：¥{previous_price}\n'
                        f'查看详情：{settings.SITE_URL}/api/detail/{component_type}/{item.id}/'
                    )
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True
                    )
                    PriceChangeNotification.objects.create(
                        user=user,
                        content_type=favorite.content_type,
                        object_id=favorite.object_id,
                        current_price=current_price,
                        previous_price=previous_price
                    )
                    logger.info(f"Email sent and notification recorded for {item.title}")
                else:
                    logger.info(f"Recent notification exists for {item.title}")
            else:
                logger.info(f"No price change for {item.title}")
        except Exception as e:
            logger.error(f"Error checking price change for favorite {favorite.id}: {e}", exc_info=True)