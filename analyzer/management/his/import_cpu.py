import os
import sys
import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from datetime import datetime

# 设置Django环境
if __name__ == "__main__":
    # 替换为你实际的Django项目名称
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hardware_analyzer.settings")
    import django

    django.setup()

# 导入你的模型（替换your_app为你的实际应用名）
from analyzer.models import CPU, CPUPriceHistory


def import_cpu_data():
    """导入CPU基本信息"""
    # 替换为你的CPU数据CSV文件路径
    cpu_csv_path = "../../../spider/csv/cpu_products.csv"

    if not os.path.exists(cpu_csv_path):
        print(f"错误：CPU数据文件不存在 - {cpu_csv_path}")
        return

    print(f"开始导入CPU数据从 {cpu_csv_path}...")

    with open(cpu_csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0
        created = 0
        updated = 0

        for row in reader:
            total += 1
            # 转换空字符串为None
            for key in row:
                if row[key] == '':
                    row[key] = None

            # 创建或更新CPU记录
            cpu, created_flag = CPU.objects.update_or_create(
                product_id=row['产品ID'],
                defaults={
                    'title': row['标题'],
                    'reference_price': row['参考价'],
                    'jd_price': row['京东价'],
                    'jd_link': row['京东链接'],
                    'product_image': row['产品图片'],
                    'product_parameters': row['产品参数'],
                    'jd_store': row['京东店铺'],
                    'comment_count': row['评论数'],
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        print(f"CPU数据导入完成！总计处理 {total} 条，新增 {created} 条，更新 {updated} 条")


def import_price_history():
    """导入CPU历史价格数据"""
    # 替换为你的历史价格CSV文件路径
    price_csv_path = "../../../spider/csv/cpu_price_history.csv"

    if not os.path.exists(price_csv_path):
        print(f"错误：历史价格文件不存在 - {price_csv_path}")
        return

    print(f"开始导入CPU历史价格数据从 {price_csv_path}...")

    with open(price_csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0
        created = 0
        skipped = 0

        for row in reader:
            total += 1
            try:
                # 查找对应的CPU
                cpu = CPU.objects.get(product_id=row['产品ID'])

                # 转换日期格式
                date = parse_date(row['日期'])
                if not date:
                    raise ValueError(f"无效的日期格式: {row['日期']}")

                # 创建价格记录
                _, created_flag = CPUPriceHistory.objects.get_or_create(
                    cpu=cpu,
                    date=date,
                    defaults={
                        'price': row['价格'],
                        'created_at': datetime.strptime(
                            row['爬取时间'],
                            '%Y-%m-%d %H:%M:%S'
                        ) if '爬取时间' in row else datetime.now()
                    }
                )

                if created_flag:
                    created += 1
                else:
                    skipped += 1

            except CPU.DoesNotExist:
                print(f"警告: 跳过记录 - 未找到产品ID为 {row['产品ID']} 的CPU")
                skipped += 1
            except Exception as e:
                print(f"错误: 处理记录时出错 - {e} (行内容: {row})")
                skipped += 1

        print(f"历史价格导入完成！总计处理 {total} 条，新增 {created} 条，跳过 {skipped} 条")


if __name__ == "__main__":
    # 在这里设置你的CSV文件路径（修改为你实际的文件路径）
    CPU_CSV_PATH = "../../../spider/csv/cpu_products.csv"  # CPU基本信息CSV路径
    PRICE_CSV_PATH = "../../../spider/csv/cpu_price_history.csv"  # 历史价格CSV路径

    # 创建csv目录（如果不存在）
    os.makedirs("csv", exist_ok=True)

    print("=" * 50)
    print("开始导入数据到数据库")
    print("=" * 50)

    # 导入CPU数据
    if os.path.exists(CPU_CSV_PATH):
        import_cpu_data()
    else:
        print(f"CPU数据文件不存在，跳过: {CPU_CSV_PATH}")

    print("-" * 50)

    # 导入历史价格数据
    if os.path.exists(PRICE_CSV_PATH):
        import_price_history()
    else:
        print(f"历史价格文件不存在，跳过: {PRICE_CSV_PATH}")

    print("=" * 50)
    print("数据导入完成！")
    print("=" * 50)

    # 防止窗口立即关闭（Windows系统）
    if os.name == 'nt':

        input("按Enter键退出...")