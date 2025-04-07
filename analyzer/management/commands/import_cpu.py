
# your_app/management/commands/import_cpu.py
import csv
import os
from django.core.management.base import BaseCommand

from analyzer.models import CPU



class Command(BaseCommand):
    help = 'Import CPU data from CSV file (will delete existing data first)'

    # 直接在代码中指定CSV文件路径
    CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), '../../../spider/clearcsv/cpu.csv')

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-delete',
            action='store_true',
            help='Skip deleting existing data before import'
        )

    def handle(self, *args, **kwargs):
        skip_delete = kwargs['no_delete']

        if not skip_delete:
            # 删除所有现有数据
            deleted_count, _ = CPU.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing CPU records'))

        try:
            with open(self.CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as csv_file:
                reader = csv.DictReader(csv_file)
                cpus_to_create = []

                for row in reader:
                    cpu = CPU(
                        title=row['标题'],
                        reference_price=row['参考价'],
                        jd_price=row['京东价'] or None,
                        jd_link=row['京东链接'] or None,
                        product_image=row['产品图片'] or 'https://example.com/default.jpg',
                        product_parameters=row['产品参数'] or None,
                        suitable_type=row['适用类型'] or None,
                        cpu_series=row['CPU系列'] or None,
                        cpu_frequency=row['CPU主频'] or None,
                        max_turbo_frequency=row['最高睿频'] or None,
                        l3_cache=row['三级缓存'] or None,
                        socket_type=row['插槽类型'] or None,
                        core_count=row['核心数量'] or None,
                        thread_count=row['线程数'] or None,
                        manufacturing_tech=row['制作工艺'] or None,
                        tdp=row['热设计功耗(TDP)'] or None,
                        turbo_boost_frequency=row['动态加速频率'] or None,
                        package_size=row['封装大小'] or None
                    )
                    cpus_to_create.append(cpu)

                # 批量创建
                CPU.objects.bulk_create(cpus_to_create)
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(cpus_to_create)} CPU records'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found at {self.CSV_FILE_PATH}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing data: {str(e)}'))