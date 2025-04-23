import os
from celery import Celery

# 设置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')

# 初始化 Celery 应用
app = Celery('hardware_analyzer')

# 从 Django 设置加载 Celery 配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()