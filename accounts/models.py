from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # 添加您的自定义字段
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'