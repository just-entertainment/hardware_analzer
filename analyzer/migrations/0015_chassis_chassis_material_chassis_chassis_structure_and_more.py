# Generated by Django 4.1 on 2025-04-13 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0014_gpu_api_support_gpu_chip_manufacturer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chassis',
            name='chassis_material',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='机箱材质'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='chassis_structure',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='机箱结构'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='chassis_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='机箱类型'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='compatible_motherboard',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='适用主板'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='expansion_slots',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='扩展插槽'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='front_interface',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='前置接口'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='panel_thickness',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='板材厚度'),
        ),
        migrations.AddField(
            model_name='chassis',
            name='power_design',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='电源设计'),
        ),
    ]
