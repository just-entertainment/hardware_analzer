import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
import django
django.setup()

from django.core.mail import send_mail

send_mail(
    '您收藏的配件 testram 价格发生变化！',
    '当前价格450\n前一天价格：¥480\n',
    '1696995719@qq.com',  # 如果settings.py中配置了DEFAULT_FROM_EMAIL，可以省略
    ['1696995719@qq.com'],  # 收件人列表
    fail_silently=False,  # 如果发送失败是否静默处理

)