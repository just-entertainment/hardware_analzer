import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
import django
django.setup()

import uuid
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from analyzer.models import RAM, RAMPriceHistory, Favorite
from django.contrib.contenttypes.models import ContentType

# 清理旧数据
CustomUser.objects.filter(phone='15631128911').delete()
RAM.objects.filter(title="Test RAM").delete()


# 创建用户
user = CustomUser.objects.create_user(
    phone='15631128911',
    username='testuser',
    password='testpass',
    email='1696995719@eqq.com'
)

# 创建 RAM 配件，确保 product_id 唯一
ram = RAM.objects.create(
    product_id=f"test_ram_{uuid.uuid4().hex[:8]}",
    title="Test RAM",
    reference_price=500,
    jd_price=480
)

# 创建收藏
content_type = ContentType.objects.get_for_model(RAM)
Favorite.objects.create(user=user, content_type=content_type, object_id=ram.id)

# 创建历史价格
RAMPriceHistory.objects.create(
    ram=ram,
    price=480,
    date=timezone.now().date() - timedelta(days=1)
)
RAMPriceHistory.objects.create(
    ram=ram,
    price=450,
    date=timezone.now().date()
)

print("Test data created successfully!")