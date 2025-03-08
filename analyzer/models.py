from django.db import models

# Create your models here.
from django.db import models

class CPU(models.Model):
    name = models.CharField(max_length=100)  # CPU 名称
    brand = models.CharField(max_length=50)  # 品牌 (Intel/AMD)
    series = models.CharField(max_length=50)  # 系列 (Core i/Ryzen)
    type = models.CharField(max_length=50)   # 适用类型 (PC/Laptop)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 价格

    def __str__(self):
        return self.name
class RAM(models.Model):
    name = models.CharField(max_length=100)  # 内存条名称
    capacity = models.IntegerField()         # 容量 (GB)
    ram_type = models.CharField(max_length=50)  # 类型 (DDR4/DDR5)
    frequency = models.IntegerField()        # 频率 (MHz)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 价格

    def __str__(self):
        return self.name