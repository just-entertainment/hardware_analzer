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

class CPU(models.Model):
    title = models.CharField(max_length=255, verbose_name='标题')
    reference_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='参考价')
    jd_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='京东价')
    jd_link = models.URLField(max_length=500, null=True, blank=True, verbose_name='京东链接')
    product_image = models.URLField(max_length=500, default='https://example.com/default.jpg', verbose_name='产品图片')
    product_parameters = models.TextField(null=True, blank=True, verbose_name='产品参数')

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