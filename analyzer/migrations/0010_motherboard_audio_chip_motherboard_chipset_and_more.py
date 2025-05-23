# Generated by Django 4.1 on 2025-04-10 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0009_remove_cpu_applicable_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='motherboard',
            name='audio_chip',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='音频芯片'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='chipset',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='主芯片组'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='dimensions',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='外形尺寸'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='form_factor',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='主板板型'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='max_memory',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='最大内存容量'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='memory_type',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='内存类型'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='power_connector',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='电源插口'),
        ),
        migrations.AddField(
            model_name='motherboard',
            name='power_phase',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='供电模式'),
        ),
    ]
