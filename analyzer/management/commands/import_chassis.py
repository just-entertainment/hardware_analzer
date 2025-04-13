import os
import sys
import csv
from decimal import Decimal

# 设置Django环境
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')  # 替换为您的项目名称
    import django

    django.setup()
    from analyzer.models import Chassis  # 替换为您的应用名称


def import_chassis_from_csv(csv_file_path):
    """
    从CSV文件导入机箱数据到数据库
    :param csv_file_path: CSV文件路径
    """
    try:
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # 处理空值，将空字符串转换为None
                for key in row:
                    if row[key] == '':
                        row[key] = None

                # 创建Chassis对象
                chassis = Chassis(
                    title=row['标题'],
                    reference_price=Decimal(row['参考价']) if row['参考价'] else Decimal('0.00'),
                    jd_price=Decimal(row['京东价']) if row['京东价'] else None,
                    jd_link=row['京东链接'],
                    product_image=row['产品图片'] if row['产品图片'] else 'https://example.com/default.jpg',
                    product_parameters=row['产品参数'],
                    chassis_type=row['机箱类型'],
                    chassis_structure=row['机箱结构'],
                    compatible_motherboard=row['适用主板'],
                    power_design=row['电源设计'],
                    expansion_slots=row['扩展插槽'],
                    front_interface=row['前置接口'],
                    chassis_material=row['机箱材质'],
                    panel_thickness=row['板材厚度']
                )

                # 保存到数据库
                chassis.save()
                print(f"成功导入: {row['标题']}")

        print(f"导入完成! 共处理了 {reader.line_num - 1} 条记录。")

    except FileNotFoundError:
        print(f"错误: 文件 {csv_file_path} 未找到!")
    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")


if __name__ == '__main__':
    # 在这里指定您的CSV文件路径
    csv_path = '../../../spider/clearcsv/机箱.csv'  # 替换为您的CSV文件实际路径

    # 检查文件是否存在
    if not os.path.exists(csv_path):
        print(f"错误: 文件 {csv_path} 不存在!")
        sys.exit(1)

    # 执行导入
    print(f"开始从 {csv_path} 导入数据...")
    import_chassis_from_csv(csv_path)