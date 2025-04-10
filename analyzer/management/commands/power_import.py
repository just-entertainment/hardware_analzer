import os
import csv
import django
from django.conf import settings

if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    django.setup()

    from analyzer.models import PowerSupply

    # 配置CSV路径（三种方式任选）
    # 方式1：硬编码路径
    csv_path = '../../../spider/clearcsv/电源.csv'

    # 方式2：相对于脚本的路径
    # csv_path = os.path.join(os.path.dirname(__file__), "data", "powersupplies.csv")

    # 方式3：使用Django的BASE_DIR
    # from django.conf import settings
    # csv_path = os.path.join(settings.BASE_DIR, "data", "powersupplies.csv")

    if not os.path.exists(csv_path):
        print(f"❌ 错误：CSV文件不存在 {csv_path}")
        exit()

    print(f"🔍 开始导入电源数据: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                PowerSupply.objects.create(
                    title=row['标题'].strip(),
                    reference_price=float(row['参考价']) if row['参考价'].strip() else 0.00,
                    jd_price=float(row['京东价']) if row['京东价'].strip() else None,
                    jd_link=row['京东链接'].strip() or None,
                    product_image=row['产品图片'].strip() or 'https://example.com/default.jpg',
                    product_parameters=row.get('产品参数', '').strip(),
                    psu_type=row.get('电源类型', '').strip(),
                    cable_type=row.get('出线类型', '').strip(),
                    rated_power=row.get('额定功率', '').strip(),
                    max_power=row.get('最大功率', '').strip(),
                    motherboard_connector=row.get('主板接口', '').strip(),
                    hdd_connector=row.get('硬盘接口', '').strip(),
                    pfc_type=row.get('PFC类型', '').strip(),
                    efficiency=row.get('转换效率', '').strip()
                )
                print(f"✅ 已导入: {row['标题']}")
            except Exception as e:
                print(f"⚠️ 导入失败: {row['标题']} | 错误: {str(e)}")

    print("🎉 电源数据导入完成！")