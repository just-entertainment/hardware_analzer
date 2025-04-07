import pandas as pd
import re


def parse_gpu_params(input_file, output_file):
    """
    解析显卡产品参数CSV文件

    参数:
        input_file (str): 输入CSV文件路径
        output_file (str): 输出CSV文件路径
    """
    # 读取原始CSV文件
    df = pd.read_csv(input_file, encoding='utf-8')

    # 预定义的显卡参数列表（基于提供的示例）
    predefined_params = [
        '芯片厂商', '显卡芯片', '显示芯片系列', '制作工艺', '核心代号',
        '核心频率', '流处理单元', 'CUDA核心', '显存类型', '显存容量',
        '显存位宽', '显存频率', '内存带宽', '最大分辨率', '接口类型',
        'I/O接口', '电源接口', '建议电源', '显卡类型', '散热方式',
        '产品型号', '3D API'
    ]

    # 初始化所有预定义参数列为空字符串
    for param in predefined_params:
        if param not in df.columns:
            df[param] = ''

    # 解析每一行的产品参数
    for index, row in df.iterrows():
        if pd.isna(row.get('产品参数', '')):
            continue

        # 分割参数行
        param_lines = str(row['产品参数']).split('\n')

        # 解析每个参数键值对
        for line in param_lines:
            # 处理多种分隔符情况（中文制表符、冒号、空格等）
            match = re.split(r'[：:\t]', line.strip(), maxsplit=1)
            if len(match) == 2:
                key = match[0].strip()
                value = match[1].strip()

                # 统一处理键名变体
                key = normalize_gpu_key(key)

                # 检查是否为预定义参数
                if key in predefined_params:
                    df.at[index, key] = value
                else:
                    # 对于未预定义的参数，动态添加新列
                    if key not in df.columns:
                        df[key] = ''
                    df.at[index, key] = value

    # 保存处理后的数据
    df.to_csv(output_file, index=False, encoding='utf_8_sig')
    print(f"成功处理 {len(df)} 条显卡记录，结果已保存到: {output_file}")


def normalize_gpu_key(key):
    """统一化显卡参数键名"""
    # 常见键名变体映射
    key_variants = {
        '显示芯片': '显卡芯片',
        'GPU芯片': '显卡芯片',
        'GPU': '显卡芯片',
        '核心代号名称': '核心代号',
        '显存大小': '显存容量',
        '显存规格': '显存类型',
        '输出接口': 'I/O接口',
        '显示输出接口': 'I/O接口',
        '电源需求': '建议电源',
        'TDP': '建议电源',
        '功耗': '建议电源',
        '散热设计': '散热方式',
        '冷却系统': '散热方式'
    }

    # 去除特殊字符和多余空格
    key = re.sub(r'[\(\)（）]', '', key).strip()

    # 检查是否为已知变体
    return key_variants.get(key, key)


# 使用示例
if __name__ == "__main__":
    parse_gpu_params(
        input_file="../csv/gpu01.csv",
        output_file="../clearcsv/gpu.csv"
    )