from django.db import models

class RAM(models.Model):
    title = models.TextField()
    reference_price = models.IntegerField(null=True, blank=True)
    jd_price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'ram'

    def __str__(self):
        return self.title