import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction



class Command(BaseCommand):
    help = '导入SSD产品和价格历史数据从CSV文件'

    def handle(self, *args, **options):
        # 设置CSV文件路径 - 请根据实际情况修改
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PRODUCTS_CSV = os.path.join(BASE_DIR, '../../../spider/csv/ssd_products.csv')
        PRICE_HISTORY_CSV = os.path.join(BASE_DIR, '../../../spider/csv/ssd_price_history.csv')

        try:
            with transaction.atomic():
                self.import_products(PRODUCTS_CSV)
                self.import_price_history(PRICE_HISTORY_CSV)
            self.stdout.write(self.style.SUCCESS('数据导入成功!'))
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

                # 从产品参数中提取SSD特有字段
                specs_dict = self.parse_specs(specs)

                # 创建或更新SSD记录
                ssd, created = SSD.objects.update_or_create(
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
                        # SSD特有字段
                        'capacity': specs_dict.get('硬盘容量'),
                        'size': specs_dict.get('硬盘尺寸'),
                        'interface': specs_dict.get('接口类型'),
                        'cache': specs_dict.get('缓存'),
                    }
                )
                action = "创建" if created else "更新"
                self.stdout.write(f'{action} SSD: {ssd.title}')

    def import_price_history(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 数据清洗和转换
                product_id = row['product_id'].split('_')[0]  # 处理可能的后缀
                price = self.clean_decimal(row['price'])
                date = self.clean_date(row['date'])

                try:
                    ssd = SSD.objects.get(product_id=product_id)
                    # 创建价格历史记录
                    price_history, created = SSDPriceHistory.objects.get_or_create(
                        ssd=ssd,
                        date=date,
                        defaults={'price': price}
                    )
                    if not created:
                        price_history.price = price
                        price_history.save()

                    action = "创建" if created else "更新"
                    self.stdout.write(f'{action} 价格记录: {ssd.title} - {date} - ¥{price}')
                except SSD.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'未找到产品ID {product_id} 对应的SSD，跳过价格记录'))

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

    from analyzer.models import SSD, SSDPriceHistory

    SSDPriceHistory.objects.all().delete()
    SSD.objects.all().delete()
    command = Command()
    command.handle()