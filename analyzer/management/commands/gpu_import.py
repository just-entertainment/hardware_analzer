import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = '导入显卡产品和价格历史数据从CSV文件'

    def handle(self, *args, **options):
        # 设置CSV文件路径
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PRODUCTS_CSV = os.path.join(BASE_DIR, '../../../spider/cleaned/cleaned_gpu_products.csv')
        PRICE_HISTORY_CSV = os.path.join(BASE_DIR, '../../../spider/cleaned/cleaned_gpu_price_history.csv')

        try:
            with transaction.atomic():
                self.import_products(PRODUCTS_CSV)
                self.import_price_history(PRICE_HISTORY_CSV)
            self.stdout.write(self.style.SUCCESS('显卡数据导入成功!'))
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

                # 从产品参数中提取GPU特有字段
                specs_dict = self.parse_specs(specs)

                # 创建或更新GPU记录
                gpu, created = GPU.objects.update_or_create(
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
                        # 芯片信息
                        'chip_manufacturer': specs_dict.get('芯片厂商') or specs_dict.get('显卡芯片厂商'),
                        'gpu_chip': specs_dict.get('显卡芯片') or specs_dict.get('GPU芯片'),
                        'chip_series': specs_dict.get('显示芯片系列') or specs_dict.get('芯片系列'),
                        'process_tech': specs_dict.get('制作工艺') or specs_dict.get('工艺'),
                        'core_code': specs_dict.get('核心代号'),
                        # 核心规格
                        'core_clock': specs_dict.get('核心频率'),
                        'stream_processors': specs_dict.get('流处理单元') or specs_dict.get('流处理器'),
                        'cuda_cores': specs_dict.get('CUDA核心') or specs_dict.get('CUDA处理器'),
                        # 显存规格
                        'memory_type': specs_dict.get('显存类型'),
                        'memory_size': specs_dict.get('显存容量'),
                        'memory_bus': specs_dict.get('显存位宽'),
                        'memory_clock': specs_dict.get('显存频率'),
                        'memory_bandwidth': specs_dict.get('内存带宽'),
                        # 显示输出
                        'max_resolution': specs_dict.get('最大分辨率'),
                        'interface_type': specs_dict.get('接口类型'),
                        'io_ports': specs_dict.get('I/O接口') or specs_dict.get('显示接口'),
                        # 电源需求
                        'power_connectors': specs_dict.get('电源接口'),
                        'recommended_psu': specs_dict.get('建议电源'),
                        # 物理特性
                        'gpu_type': specs_dict.get('显卡类型'),
                        'cooling': specs_dict.get('散热方式'),
                        'model_number': specs_dict.get('产品型号'),
                        'dimensions': specs_dict.get('产品尺寸'),
                        'design': specs_dict.get('显卡设计'),
                        # 技术支持
                        'api_support': specs_dict.get('3D API') or specs_dict.get('API支持'),
                    }
                )
                action = "创建" if created else "更新"
                self.stdout.write(f'{action} 显卡: {gpu.title}')

    def import_price_history(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 数据清洗和转换
                product_id = row['product_id'].split('_')[0]  # 处理可能的后缀
                price = self.clean_decimal(row['price'])
                date = self.clean_date(row['date'])

                try:
                    gpu = GPU.objects.get(product_id=product_id)
                    # 创建价格历史记录
                    price_history, created = GPUPriceHistory.objects.get_or_create(
                        gpu=gpu,
                        date=date,
                        defaults={'price': price}
                    )
                    if not created:
                        price_history.price = price
                        price_history.save()

                    action = "创建" if created else "更新"
                    self.stdout.write(f'{action} 价格记录: {gpu.title} - {date} - ¥{price}')
                except GPU.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'未找到产品ID {product_id} 对应的显卡，跳过价格记录'))

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

    from analyzer.models import GPU, GPUPriceHistory

    GPUPriceHistory.objects.all().delete()
    GPU.objects.all().delete()
    command = Command()
    command.handle()