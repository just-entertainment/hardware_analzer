from django.db import models

class Motherboard(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '主板'
        verbose_name_plural = '主板'
        db_table = 'motherboards'

    def __str__(self):
        return self.title


from django.db import models


class CPU(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    # 新增字段
    suitable_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='适用类型')
    cpu_series = models.CharField(max_length=100, null=True, blank=True, verbose_name='CPU系列')
    cpu_frequency = models.CharField(max_length=100, null=True, blank=True, verbose_name='CPU主频')
    max_turbo_frequency = models.CharField(max_length=100, null=True, blank=True, verbose_name='最高睿频')
    l3_cache = models.CharField(max_length=100, null=True, blank=True, verbose_name='三级缓存')
    socket_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='插槽类型')
    core_count = models.CharField(max_length=100, null=True, blank=True, verbose_name='核心数量')
    thread_count = models.CharField(max_length=100, null=True, blank=True, verbose_name='线程数')
    manufacturing_tech = models.CharField(max_length=100, null=True, blank=True, verbose_name='制作工艺')
    tdp = models.CharField(max_length=100, null=True, blank=True, verbose_name='热设计功耗(TDP)')
    turbo_boost_frequency = models.CharField(max_length=100, null=True, blank=True, verbose_name='动态加速频率')
    package_size = models.CharField(max_length=100, null=True, blank=True, verbose_name='封装大小')

    class Meta:
        verbose_name = 'CPU'
        verbose_name_plural = 'CPU'
        db_table = 'cpus'

    def __str__(self):
        return self.title

class GPU(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '显卡'
        verbose_name_plural = '显卡'
        db_table = 'gpus'

    def __str__(self):
        return self.title

class RAM(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '内存'
        verbose_name_plural = '内存'
        db_table = 'ram'

    def __str__(self):
        return self.title

class SSD(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '固态硬盘'
        verbose_name_plural = '固态硬盘'
        db_table = 'ssds'

    def __str__(self):
        return self.title

class Cooler(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '散热器'
        verbose_name_plural = '散热器'
        db_table = 'coolers'

    def __str__(self):
        return self.title

class PowerSupply(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '电源'
        verbose_name_plural = '电源'
        db_table = 'power_supplies'

    def __str__(self):
        return self.title
class Chassis(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

    class Meta:
        verbose_name = '机箱'
        verbose_name_plural = '机箱'
        db_table = 'chassis'

    def __str__(self):
        return self.title


from django.db import models

class PriceHistory(models.Model):
    component_type = models.CharField(max_length=50)
    component_id = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '价格历史'
        verbose_name_plural = '价格历史'
        db_table = 'price_history'

    def __str__(self):
        return f"{self.component_type} {self.component_id} - {self.price} at {self.date}"