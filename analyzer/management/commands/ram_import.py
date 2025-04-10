import os
import csv
import django
from django.conf import settings

if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    django.setup()

    from analyzer.models import RAM

    # 配置CSV路径（三种方式任选）
    # 方式1：硬编码路径
    csv_path = '../../../spider/clearcsv/内存.csv'



    if not os.path.exists(csv_path):
        print(f"❌ 错误：CSV文件不存在 {csv_path}")
        exit()

    print(f"🔍 开始导入内存数据: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                RAM.objects.create(
                    title=row['标题'].strip(),
                    reference_price=float(row['参考价']) if row['参考价'].strip() else 0.00,
                    jd_price=float(row['京东价']) if row['京东价'].strip() else None,
                    jd_link=row['京东链接'].strip() or None,
                    product_image=row['产品图片'].strip() or 'https://example.com/default.jpg',
                    suitable_type=row.get('适用类型', '').strip(),
                    capacity=row.get('内存容量', '').strip(),
                    memory_type=row.get('内存类型', '').strip(),
                    frequency=row.get('内存主频', '').strip()
                )
                print(f"✅ 已导入: {row['标题']}")
            except Exception as e:
                print(f"⚠️ 导入失败: {row['标题']} | 错误: {str(e)}")

    print("🎉 内存数据导入完成！")