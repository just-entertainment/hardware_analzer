import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = '导入主板产品和价格历史数据从CSV文件'

    def handle(self, *args, **options):
        # 设置CSV文件路径 - 请根据实际情况修改
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PRODUCTS_CSV = os.path.join(BASE_DIR, '../../../spider/cleaned/cleaned_borad_products.csv')
        PRICE_HISTORY_CSV = os.path.join(BASE_DIR, '../../../spider/cleaned/cleaned_broad_price_history.csv')

        try:
            with transaction.atomic():
                self.import_products(PRODUCTS_CSV)
                self.import_price_history(PRICE_HISTORY_CSV)
            self.stdout.write(self.style.SUCCESS('主板数据导入成功!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入失败: {str(e)}'))

    def import_products(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 数据清洗和转换
                product_id = row['product_id'].strip()
                title = row['title'].strip()
                reference_price = self.clean_decimal(row.get('reference_price', '0'))
                jd_price = self.clean_decimal(row.get('current_price'))
                jd_link = self.clean_url(row.get('jd_url'))
                product_image = self.clean_url(row.get('image_url'))
                specs = row.get('specs', '').strip()
                shop_name = row.get('shop_name', '').strip()
                comment_count = row.get('comment_count', '').strip()

                # 从产品参数中提取主板特有字段
                specs_dict = self.parse_specs(specs)

                # 创建或更新主板记录
                board, created = Motherboard.objects.update_or_create(
                    product_id=product_id,
                    defaults={
                        'title': title,
                        'reference_price': reference_price,
                        'jd_price': jd_price,
                        'jd_link': jd_link,
                        'product_image': product_image or 'https://example.com/default.jpg',
                        'product_parameters': specs,
                        'jd_store': shop_name if shop_name else None,
                        'comment_count': comment_count if comment_count else None,
                        # 主板特有字段
                        'chipset': specs_dict.get('主芯片组') or specs_dict.get('芯片组'),
                        'audio_chip': specs_dict.get('音频芯片'),
                        'memory_type': specs_dict.get('内存类型'),
                        'max_memory': specs_dict.get('最大内存容量'),
                        'form_factor': specs_dict.get('主板板型') or specs_dict.get('板型'),
                        'dimensions': specs_dict.get('外形尺寸') or specs_dict.get('尺寸'),
                        'power_connector': specs_dict.get('电源插口') or specs_dict.get('电源接口'),
                        'power_phase': specs_dict.get('供电模式') or specs_dict.get('电源相数'),
                    }
                )
                action = "创建" if created else "更新"
                self.stdout.write(f'{action} 主板: {board.title}')

    def import_price_history(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 数据清洗和转换
                product_id = row['product_id'].split('_')[0]  # 处理可能的后缀
                price = self.clean_decimal(row['price'])
                date = self.clean_date(row['date'])

                try:
                    board = Motherboard.objects.get(product_id=product_id)
                    # 创建价格历史记录
                    price_history, created = MotherboardPriceHistory.objects.get_or_create(
                        motherboard=board,
                        date=date,
                        defaults={'price': price}
                    )
                    if not created:
                        price_history.price = price
                        price_history.save()

                    action = "创建" if created else "更新"
                    self.stdout.write(f'{action} 价格记录: {board.title} - {date} - ¥{price}')
                except Motherboard.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'未找到产品ID {product_id} 对应的主板，跳过价格记录'))

    def clean_decimal(self, value):
        """清洗并转换价格为Decimal"""
        if not value or str(value).strip() == '':
            return None
        try:
            return float(str(value).replace(',', '').strip())
        except (ValueError, TypeError):
            return None

    def clean_url(self, url):
        """清洗URL"""
        if not url or str(url).strip() == '':
            return None
        return str(url).strip()

    def clean_date(self, date_str):
        """清洗日期字符串"""
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return datetime.now().date()

    def parse_specs(self, specs):
        """解析产品参数为字典"""
        if not specs:
            return {}

        result = {}
        lines = specs.split('\n')
        for line in lines:
            if '：' in line:  # 中文冒号分隔
                key, value = line.split('：', 1)
                result[key.strip()] = value.strip()
            elif ':' in line:  # 英文冒号分隔
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()

        return result


if __name__ == '__main__':
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    import django
    django.setup()

    from analyzer.models import Motherboard, MotherboardPriceHistory

    MotherboardPriceHistory.objects.all().delete()
    Motherboard.objects.all().delete()
    command = Command()
    command.handle()