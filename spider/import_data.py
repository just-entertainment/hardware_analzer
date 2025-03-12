import csv
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
django.setup()

from analyzer.models import RAM


def parse_ram_title(title):
    """解析内存标题，提取容量、类型和频率"""
    parts = title.split()
    capacity = next((part.replace('GB', '') for part in parts if 'GB' in part), '0')
    ram_type = next((part for part in parts if 'DDR' in part), '')
    frequency = next((part.replace('MHz', '') for part in parts if 'MHz' in part), '0')
    return {
        'name': title,
        'capacity': int(capacity or 0),
        'ram_type': ram_type,
        'frequency': int(frequency or 0),
        'price': 0  # 初始值，稍后更新
    }


def import_ram_data_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data = parse_ram_title(row['标题'])
            # 处理价格（优先京东价，若无则用参考价）
            price = row['京东价'] or row['参考价']
            price = float(price.replace('￥', '') or 0)

            RAM.objects.update_or_create(
                name=data['name'],
                defaults={
                    'capacity': data['capacity'],
                    'ram_type': data['ram_type'],
                    'frequency': data['frequency'],
                    'price': price
                }
            )
        print("内存数据导入完成！")


if __name__ == "__main__":
    csv_file_path = 'csv/zgram0310.csv'  # 替换为实际路径
    import_ram_data_from_csv(csv_file_path)