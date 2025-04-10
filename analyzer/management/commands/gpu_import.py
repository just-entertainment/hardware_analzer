import os
import csv
import django
from django.conf import settings


def safe_strip(value):
    """安全处理字符串，防止None值报错"""
    return value.strip() if value and isinstance(value, str) else None


if __name__ == "__main__":
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hardware_analyzer.settings')
    django.setup()

    from analyzer.models import GPU

    # 配置CSV路径（修改为实际路径）
    csv_path = '../../../spider/clearcsv/gpu.csv'

    if not os.path.exists(csv_path):
        print(f"❌ 错误：CSV文件不存在 {csv_path}")
        exit()

    print(f"🔍 开始导入显卡数据: {csv_path}")

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # 准备数据字典（所有字段都经过安全处理）
                data = {
                    'title': safe_strip(row.get('标题')),
                    'reference_price': float(row['参考价']) if row.get('参考价') and row['参考价'].strip() else 0.00,
                    'jd_price': float(row['京东价']) if row.get('京东价') and row['京东价'].strip() else None,
                    'jd_link': safe_strip(row.get('京东链接')),
                    'product_image': safe_strip(row.get('产品图片')) or 'https://example.com/default.jpg',
                    'product_parameters': safe_strip(row.get('产品参数')),

                    # 芯片信息
                    'chip_manufacturer': safe_strip(row.get('芯片厂商')),
                    'gpu_chip': safe_strip(row.get('显卡芯片')),
                    'chip_series': safe_strip(row.get('显示芯片系列')),
                    'process_tech': safe_strip(row.get('制作工艺')),
                    'core_code': safe_strip(row.get('核心代号')),

                    # 核心规格
                    'core_clock': safe_strip(row.get('核心频率')),
                    'stream_processors': safe_strip(row.get('流处理单元')),
                    'cuda_cores': safe_strip(row.get('CUDA核心')),

                    # 显存规格
                    'memory_type': safe_strip(row.get('显存类型')),
                    'memory_size': safe_strip(row.get('显存容量')),
                    'memory_bus': safe_strip(row.get('显存位宽')),
                    'memory_clock': safe_strip(row.get('显存频率')),
                    'memory_bandwidth': safe_strip(row.get('内存带宽')),

                    # 显示输出
                    'max_resolution': safe_strip(row.get('最大分辨率')),
                    'interface_type': safe_strip(row.get('接口类型')),
                    'io_ports': safe_strip(row.get('I/O接口')),

                    # 电源需求
                    'power_connectors': safe_strip(row.get('电源接口')),
                    'recommended_psu': safe_strip(row.get('建议电源')),

                    # 物理特性
                    'gpu_type': safe_strip(row.get('显卡类型')),
                    'cooling': safe_strip(row.get('散热方式')),
                    'model_number': safe_strip(row.get('产品型号')),
                    'dimensions': safe_strip(row.get('产品尺寸')),
                    'design': safe_strip(row.get('显卡设计')),

                    # 技术支持
                    'api_support': safe_strip(row.get('3D API'))
                }

                # 创建或更新记录
                GPU.objects.update_or_create(
                    title=data['title'],
                    defaults={k: v for k, v in data.items() if v is not None}
                )
                print(f"✅ 已导入: {row.get('标题', '未知显卡')}")

            except Exception as e:
                print(f"⚠️ 导入失败: {row.get('标题', '未知显卡')} | 错误: {str(e)}")
                print(f"问题数据: {row}")

    print("🎉 显卡数据导入完成！")