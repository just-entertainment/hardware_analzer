from django.db import models

class RAM(models.Model):
    title = models.TextField()
    reference_price = models.IntegerField(null=True, blank=True)
    jd_price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'ram'

    def __str__(self):
        return self.title
class GPU(models.Model):
    title = models.TextField()  # GPU 标题
    reference_price = models.IntegerField(null=True, blank=True)  # 参考价
    jd_price = models.FloatField(null=True, blank=True)  # 京东价

    class Meta:
        db_table = 'gpu'  # 表名为 'gpu'

    def __str__(self):
        return self.title


class CPU(models.Model):
    title = models.TextField()  # CPU 标题
    reference_price = models.IntegerField(null=True, blank=True)  # 参考价
    jd_price = models.FloatField(null=True, blank=True)  # 京东价

    class Meta:
        db_table = 'cpu'  # 表名为 'cpu'

    def __str__(self):
        return self.title