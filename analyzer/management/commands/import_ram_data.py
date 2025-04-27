import os
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_date
from django.core.exceptions import ValidationError
from decimal import Decimal

# 在这里直接设置CSV文件路径 - 修改这两行即可
PRODUCTS_CSV = os.path.join(os.path.dirname(__file__), '../../../spider/csv/RAM_products.csv')  # 替换为你的实际路径
PRICE_HISTORY_CSV = os.path.join(os.path.dirname(__file__), '../../../spider/csv/RAM_price_history.csv')  # 替换为你的实际路径


class Command(BaseCommand):
    help = 'Import RAM products and price history from CSV files'

    def handle(self, *args, **options):
        # 验证文件是否存在
        if not os.path.exists(PRODUCTS_CSV):
            raise FileNotFoundError(f'Products CSV file not found: {PRODUCTS_CSV}')
        if not os.path.exists(PRICE_HISTORY_CSV):
            raise FileNotFoundError(f'Price history CSV file not found: {PRICE_HISTORY_CSV}')

        self.stdout.write(self.style.SUCCESS('Starting data import...'))
        self.stdout.write(f'Products file: {PRODUCTS_CSV}')
        self.stdout.write(f'Price history file: {PRICE_HISTORY_CSV}')

        # 使用事务确保数据一致性
        with transaction.atomic():
            self.import_products(PRODUCTS_CSV)
            self.import_price_history(PRICE_HISTORY_CSV)

        self.stdout.write(self.style.SUCCESS('Data import completed successfully!'))

    def import_products(self, csv_file):
        """Import RAM products from CSV"""
        from analyzer.models import RAM  # 替换为你的实际应用名

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = created = updated = 0

            for row in reader:
                total += 1
                product_id = row.get('product_id')
                if not product_id:
                    self.stdout.write(self.style.WARNING(f'Skipping row {total}: Missing product_id'))
                    continue

                # 准备产品数据
                product_data = {
                    'title': row.get('title', ''),
                    'reference_price': self.parse_decimal(row.get('reference_price')),
                    'jd_price': self.parse_decimal(row.get('current_price')),
                    'jd_link': row.get('jd_url', ''),
                    'product_image': row.get('image_url', 'https://example.com/default.jpg'),
                    'product_parameters': row.get('specs', ''),
                    'jd_store': row.get('shop_name', ''),
                    'comment_count': self.parse_comment_count(row.get('comment_count', '')),
                }

                # 解析产品规格
                specs = self.parse_specs(row.get('specs', ''))
                product_data.update({
                    'suitable_type': specs.get('适用类型'),
                    'capacity': specs.get('内存容量'),
                    'memory_type': specs.get('内存类型'),
                    'frequency': specs.get('内存主频'),
                })

                # 创建或更新产品
                try:
                    obj, created_flag = RAM.objects.update_or_create(
                        product_id=product_id,
                        defaults=product_data
                    )
                    if created_flag:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(f'Created product: {product_id}'))
                    else:
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(f'Updated product: {product_id}'))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(f'Error importing product {product_id}: {e}'))
                    continue

            self.stdout.write(self.style.SUCCESS(
                f'\nProducts import summary:\n'
                f'Total rows processed: {total}\n'
                f'New products created: {created}\n'
                f'Existing products updated: {updated}\n'
            ))

    def import_price_history(self, csv_file):
        """Import RAM price history from CSV"""
        from analyzer.models import RAM, RAMPriceHistory  # 替换为你的实际应用名

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total = created = skipped = 0

            for row in reader:
                total += 1
                product_id = row.get('product_id')
                if not product_id:
                    self.stdout.write(self.style.WARNING(f'Skipping row {total}: Missing product_id'))
                    skipped += 1
                    continue

                # 解析日期和价格
                try:
                    date = parse_date(row.get('date', ''))
                    if not date:
                        raise ValueError('Invalid date format')
                    price = self.parse_decimal(row.get('price'))
                    if not price:
                        raise ValueError('Invalid price')
                except (ValueError, TypeError) as e:
                    self.stdout.write(self.style.WARNING(
                        f'Skipping row {total}: Invalid date or price - {e}'
                    ))
                    skipped += 1
                    continue

                # 查找对应的产品
                try:
                    ram = RAM.objects.get(product_id=product_id)
                except RAM.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'Skipping row {total}: Product not found - {product_id}'
                    ))
                    skipped += 1
                    continue

                # 创建价格历史记录
                try:
                    _, created_flag = RAMPriceHistory.objects.get_or_create(
                        ram=ram,
                        date=date,
                        defaults={'price': price}
                    )
                    if created_flag:
                        created += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'Created price record: {product_id} - {date} - ¥{price}'
                        ))
                except ValidationError as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error importing price history for {product_id}: {e}'
                    ))
                    continue

            self.stdout.write(self.style.SUCCESS(
                f'\nPrice history import summary:\n'
                f'Total rows processed: {total}\n'
                f'New records created: {created}\n'
                f'Rows skipped: {skipped}\n'
            ))

    def parse_specs(self, specs_text):
        """Parse product specs text into a dictionary"""
        specs = {}
        if not specs_text:
            return specs

        lines = specs_text.split('\n')
        for line in lines:
            if '：' in line:  # 中文冒号
                key, value = line.split('：', 1)
                specs[key.strip()] = value.strip()
            elif ':' in line:  # 英文冒号
                key, value = line.split(':', 1)
                specs[key.strip()] = value.strip()

        return specs

    def parse_decimal(self, value):
        """Convert string to Decimal, handling empty/None values"""
        if not value:
            return None
        try:
            return Decimal(str(value).strip())
        except:
            return None

    def parse_comment_count(self, value):
        """Parse comment count string (e.g. "5万+" -> "50000")"""
        if not value:
            return ''

        value = value.strip().replace('+', '')
        if '万' in value:
            try:
                num = float(value.replace('万', ''))
                return str(int(num * 10000))
            except:
                return value
        return value


if __name__ == '__main__':

    # 允许直接右键运行脚本（仅用于开发测试）
    import django
    import sys
    from django.conf import settings

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    django.setup()

    # 设置Django环境
    if not settings.configured:
        settings.configure(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': 'db.sqlite3',
                }
            },
            INSTALLED_APPS=[
                'your_app',  # 替换为你的实际应用名
            ]
        )
        django.setup()

    # 运行命令
    from django.core.management import execute_from_command_line

    execute_from_command_line([sys.argv[0], 'import_ram_data'])