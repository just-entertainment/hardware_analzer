import pandas as pd
import os
import glob


def clean_comment_count(df):
    """清洗评论数据"""
    if 'comment_count' in df.columns:
        # 处理"万+"情况
        df['comment_count'] = df['comment_count'].astype(str).str.replace('万\+', '0000', regex=True)
        # 处理"+"情况
        df['comment_count'] = df['comment_count'].astype(str).str.replace('\+', '', regex=True)
        # 转换为数值类型
        df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce')
    return df


def clean_price_columns(df):
    """清洗价格数据"""
    price_columns = ['current_price', 'reference_price']

    for column in price_columns:
        if column in df.columns:
            # 去掉 '￥' 和 '¥' 符号
            df[column] = df[column].astype(str).str.replace('￥', '').str.replace('¥', '')

            # 处理 '万' 字，并转换为数值
            has_wan = df[column].str.contains('万', na=False)
            df.loc[has_wan, column] = (
                    df.loc[has_wan, column]
                    .str.replace('万', '')
                    .astype(float) * 10000
            )

            # 确保所有值转换为数值
            df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def process_csv_file(file_path):
    """处理单个CSV文件"""
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 清洗数据
        df = clean_comment_count(df)
        df = clean_price_columns(df)

        # 保存清洗后的文件
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        cleaned_file_name = f"cleaned_{file_name}"
        cleaned_file_path = os.path.join(dir_name, cleaned_file_name)

        df.to_csv(cleaned_file_path, index=False)
        print(f"成功处理并保存: {cleaned_file_path}")

    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")


def batch_process_csv_files(directory='csv'):
    """批量处理目录下的所有CSV文件"""
    # 获取目录下所有CSV文件
    csv_files = glob.glob(os.path.join(directory, '*.csv'))

    if not csv_files:
        print(f"在目录 {directory} 中没有找到CSV文件")
        return

    print(f"找到 {len(csv_files)} 个CSV文件需要处理:")
    for file in csv_files:
        print(f"- {file}")

    # 处理每个文件
    for file_path in csv_files:
        # 跳过已经清洗过的文件(文件名以cleaned_开头)
        if os.path.basename(file_path).startswith('cleaned_'):
            print(f"跳过已处理的文件: {file_path}")
            continue

        process_csv_file(file_path)

    print("所有文件处理完成!")


# 执行批量处理
batch_process_csv_files()