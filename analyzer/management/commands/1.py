import os
import csv
import django
from django.conf import settings


def safe_strip(value):
    """安全处理字符串，防止None值报错"""
    return value.strip() if value and isinstance(value, str) else None


if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    django.setup()

    from accounts.models import CustomUser

    print(CustomUser.objects.filter(phone='15631128911').values('username', 'email', 'phone', 'password'))