import pandas as pd
import re
from typing import List, Dict


def parse_motherboard_params(input_file, output_file, predefined_params=None):
    """
    解析主板产品参数CSV文件（不排序版本）

    参数:
        input_file (str): 输入CSV文件路径
        output_file (str): 输出CSV文件路径
        predefined_params (list): 预定义参数列表
    """
    # 读取原始CSV文件
    df = pd.read_csv(input_file, encoding='utf-8')



    # 收集所有动态发现的参数
    dynamic_params = set()

    # 解析每一行的产品参数
    for index, row in df.iterrows():
        if pd.isna(row.get('产品参数', '')):
            continue

        param_lines = str(row['产品参数']).split('\n')

        for line in param_lines:
            # 处理多种分隔符情况
            match = re.match(r'^(.+?)[：:]\s*(.*)$', line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()

                # 检查是否为预定义参数
                if key in predefined_params:
                    df.at[index, key] = value
                else:
                    # 动态添加新列（如果尚未存在）
                    if key not in df.columns:
                        dynamic_params.add(key)
                        df[key] = ''
                    df.at[index, key] = value

    # 保存处理后的数据（保持原始列顺序+新参数列追加在最后）
    df.to_csv(output_file, index=False, encoding='utf_8_sig')
    print(f"成功处理 {len(df)} 条主板记录，结果已保存到: {output_file}")
    print(f"发现的动态参数: {dynamic_params}")


# 使用示例
if __name__ == "__main__":
    # 自定义预定义参数（可根据需要修改）
    custom_params = [
        '存储容量', '硬盘尺寸', '接口类型', '缓存',
        '读取速度', '写入速度', '平均寻道时间', '平均无故障时间'
    ]

    parse_motherboard_params(
        input_file="../csv/SSD01.csv",
        output_file="../clearcsv/硬盘.csv",
        predefined_params=custom_params
    )