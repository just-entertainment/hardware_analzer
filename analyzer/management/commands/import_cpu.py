import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = '导入CPU产品和价格历史数据从CSV文件'

    def handle(self, *args, **options):
        # 设置CSV文件路径
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PRODUCTS_CSV = os.path.join(BASE_DIR, '../../../spider/cleaned/cleaned_cpu_products.csv')
        PRICE_HISTORY_CSV = os.path.join(BASE_DIR, '../../../spider/cleaned/cleaned_cpu_price_history.csv')

        try:
            with transaction.atomic():
                self.import_products(PRODUCTS_CSV)
                self.import_price_history(PRICE_HISTORY_CSV)
            self.stdout.write(self.style.SUCCESS('CPU数据导入成功!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'导入失败: {str(e)}'))

    def import_products(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 数据清洗和转换
                product_id = row['产品ID'].strip()
                title = row['标题'].strip()
                reference_price = self.clean_decimal(row.get('参考价', '0'))
                jd_price = self.clean_decimal(row.get('京东价'))
                jd_link = self.clean_url(row.get('京东链接'))
                product_image = self.clean_url(row.get('产品图片'))
                specs = row.get('产品参数', '').strip()
                shop_name = row.get('京东店铺', '').strip()
                comment_count = row.get('评论数', '').strip()

                # 从产品参数中提取CPU特有字段
                specs_dict = self.parse_specs(specs)

                # 创建或更新CPU记录
                cpu, created = CPU.objects.update_or_create(
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
                        # CPU特有字段
                        'suitable_type': specs_dict.get('适用类型'),
                        'cpu_series': specs_dict.get('CPU系列') or specs_dict.get('系列'),
                        'cpu_frequency': specs_dict.get('CPU主频') or specs_dict.get('主频'),
                        'max_turbo_frequency': specs_dict.get('最高睿频') or specs_dict.get('睿频'),
                        'l3_cache': specs_dict.get('三级缓存') or specs_dict.get('缓存'),
                        'socket_type': specs_dict.get('插槽类型') or specs_dict.get('接口类型'),
                        'core_count': specs_dict.get('核心数量') or specs_dict.get('核心数'),
                        'thread_count': specs_dict.get('线程数') or specs_dict.get('线程数量'),
                        'manufacturing_tech': specs_dict.get('制作工艺') or specs_dict.get('工艺'),
                        'tdp': specs_dict.get('热设计功耗(TDP)') or specs_dict.get('TDP'),
                        'turbo_boost_frequency': specs_dict.get('动态加速频率') or specs_dict.get('加速频率'),
                        'package_size': specs_dict.get('封装大小') or specs_dict.get('封装规格'),
                    }
                )
                action = "创建" if created else "更新"
                self.stdout.write(f'{action} CPU: {cpu.title}')

    def import_price_history(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 数据清洗和转换
                product_id = row['产品ID'].split('_')[0]  # 处理可能的后缀
                price = self.clean_decimal(row['价格'])
                date = self.clean_date(row['日期'])

                try:
                    cpu = CPU.objects.get(product_id=product_id)
                    # 创建价格历史记录
                    price_history, created = CPUPriceHistory.objects.get_or_create(
                        cpu=cpu,
                        date=date,
                        defaults={'price': price}
                    )
                    if not created:
                        price_history.price = price
                        price_history.save()

                    action = "创建" if created else "更新"
                    self.stdout.write(f'{action} 价格记录: {cpu.title} - {date} - ¥{price}')
                except CPU.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'未找到产品ID {product_id} 对应的CPU，跳过价格记录'))

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
    django.setup()

    from analyzer.models import CPU, CPUPriceHistory

    CPUPriceHistory.objects.all().delete()
    CPU.objects.all().delete()
    command = Command()
    command.handle()