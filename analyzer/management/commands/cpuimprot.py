import os
import sys
import django
import csv
from django.conf import settings

# 设置Django环境（关键步骤！）
c

    # 现在可以正常导入模型和命令
    from analyzer.models import Motherboard


    # 方式1：硬编码绝对路径
    csv_path = '../../../spider/clearcsv/motherborad01.csv'



    # 验证路径
    if not os.path.exists(csv_path):
        print(f"❌ 错误：CSV文件不存在 {csv_path}")
        sys.exit(1)


    # 导入函数
    def import_from_csv(file_path):
        print(f"🔍 开始导入 {file_path}")
        success = 0
        total = 0

        with open(file_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total += 1
                try:
                    # 数据清洗
                    data = {
                        'title': row['标题'].strip(),
                        'reference_price': float(row['参考价']) if row['参考价'].strip() else 0.00,
                        'jd_price': float(row['京东价']) if row['京东价'].strip() else None,
                        'jd_link': row['京东链接'].strip() or None,
                        'product_image': row['产品图片'].strip() or 'https://example.com/default.jpg',
                        'chipset': row.get('主芯片组', '').strip() or None,'audio_chip': row.get('音频芯片', '').strip() or None,
                        'memory_type': row.get('内存类型', '').strip() or None,
                        'max_memory': row.get('最大内存容量', '').strip() or None,
                        'form_factor': row.get('主板板型', '').strip() or None,
                        'dimensions': row.get('外形尺寸', '').strip() or None,
                        'power_connector': row.get('电源插口', '').strip() or None,
                        'power_phase': row.get('供电模式', '').strip() or None
                    }

                    # 创建记录
                    Motherboard.objects.update_or_create(
                        title=data['title'],
                        defaults=data
                    )
                    success += 1

                except Exception as e:
                    print(f"⚠️ 第 {total} 行错误: {e} | 数据: {row}")

        print(f"✅ 完成！成功导入 {success}/{total} 条记录")


    # 执行导入
    import_from_csv(csv_path)