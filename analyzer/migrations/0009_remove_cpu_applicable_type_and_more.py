# Generated by Django 4.1 on 2025-04-06 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0008_pricehistory_cpu_applicable_type_cpu_core_count_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cpu',
            name='applicable_type',
        ),
        migrations.RemoveField(
            model_name='cpu',
            name='cpu_base_frequency',
        ),
        migrations.RemoveField(
            model_name='cpu',
            name='dynamic_boost_frequency',
        ),
        migrations.RemoveField(
            model_name='cpu',
            name='manufacturing_process',
        ),
        migrations.RemoveField(
            model_name='cpu',
            name='packaging_size',
        ),
        migrations.AddField(
            model_name='cpu',
            name='cpu_frequency',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='CPU主频'),
        ),
        migrations.AddField(
            model_name='cpu',
            name='manufacturing_tech',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='制作工艺'),
        ),
        migrations.AddField(
            model_name='cpu',
            name='package_size',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='封装大小'),
        ),
        migrations.AddField(
            model_name='cpu',
            name='suitable_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='适用类型'),
        ),
        migrations.AddField(
            model_name='cpu',
            name='turbo_boost_frequency',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='动态加速频率'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='core_count',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='核心数量'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='cpu_series',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='CPU系列'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='jd_link',
            field=models.URLField(blank=True, max_length=500, null=True, verbose_name='京东链接'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='jd_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='京东价'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='l3_cache',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='三级缓存'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='max_turbo_frequency',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='最高睿频'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='product_image',
            field=models.URLField(default='https://example.com/default.jpg', max_length=500, verbose_name='产品图片'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='product_parameters',
            field=models.TextField(blank=True, null=True, verbose_name='产品参数'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='reference_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='参考价'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='socket_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='插槽类型'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='tdp',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='热设计功耗(TDP)'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='thread_count',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='线程数'),
        ),
        migrations.AlterField(
            model_name='cpu',
            name='title',
            field=models.CharField(max_length=255, verbose_name='标题'),
        ),
        migrations.AlterModelTable(
            name='cpu',
            table='cpus',
        ),
    ]
