import os
import csv
import django
from django.conf import settings

# 设置Django环境
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    django.setup()

    from analyzer.models import SSD

    # 配置CSV路径
    csv_path = '../../../spider/clearcsv/硬盘.csv'


    def import_ssd_data(file_path):
        print(f"开始导入SSD数据: {file_path}")
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    SSD.objects.update_or_create(
                        title=row['标题'].strip(),
                        defaults={
                            'reference_price': float(row['参考价']) if row['参考价'].strip() else 0.00,
                            'jd_price': float(row['京东价']) if row['京东价'].strip() else None,
                            'product_image': row['产品图片'].strip() or 'https://example.com/default.jpg',
                            'capacity': row.get('存储容量', '').strip(),
                            'interface': row.get('接口类型', '').strip(),
                            # 其他字段...
                            'cache' : row.get('缓存', '').strip() or None,
                            'read_speed' : row.get('读取速度', '').strip() or None,
                            'write_speed' : row.get('写入速度', '').strip() or None,
                            'seek_time' : row.get('平均寻道时间', '').strip() or None,
                            'mtbf' : row.get('平均无故障时间', '').strip() or None
                        }
                    )
                    print(f"已导入: {row['标题']}")
                except Exception as e:
                    print(f"导入失败: {row['标题']} | 错误: {str(e)}")


    if os.path.exists(csv_path):
        import_ssd_data(csv_path)
    else:
        print(f"错误: 文件不存在 {csv_path}")