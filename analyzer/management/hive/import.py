import os
import subprocess

# 配置
hive_host = 'localhost'
hive_port = 10000
hive_username = 'hive'
hive_password = 'hive'
hive_database = 'default'

# CSV 文件路径（相对路径）
price_history_csv = r'..\spider\csv\GPU_price_history.csv'
products_csv = r'..\spider\csv\GPU_products.csv'

# HDFS 路径
hdfs_price_history = '/user/hive/data/gpu/GPU_price_history.csv'
hdfs_products = '/user/hive/data/gpu/GPU_products.csv'

# Hive 表名
price_history_table = 'gpu_price_history'
products_table = 'gpu_products'

def upload_to_hdfs(local_path, hdfs_path):
    """上传文件到 HDFS"""
    if not os.path.exists(local_path):
        print(f"错误：文件 {local_path} 不存在")
        return False
    cmd = f"hdfs dfs -put -f {local_path} {hdfs_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"成功上传 {local_path} 到 {hdfs_path}")
        return True
    else:
        print(f"上传失败: {result.stderr}")
        return False

def run_beeline_query(query):
    """执行 Beeline 查询"""
    beeline_cmd = (
        f"beeline -u jdbc:hive2://{hive_host}:{hive_port}/{hive_database} "
        f"-n {hive_username} -p {hive_password} -e \"{query}\""
    )
    result = subprocess.run(beeline_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"成功执行: {query[:50]}...")
    else:
        print(f"Beeline 错误: {result.stderr}")

def create_tables():
    """创建 Hive 表结构"""
    create_price_history_table = f"""
    CREATE TABLE IF NOT EXISTS {price_history_table} (
        record_id STRING,
        product_id STRING,
        price DECIMAL(10,2),
        date DATE,
        crawl_time TIMESTAMP
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    """

    create_products_table = f"""
    CREATE TABLE IF NOT EXISTS {products_table} (
        product_id STRING,
        title STRING,
        reference_price DECIMAL(10,2),
        current_price DECIMAL(10,2),
        jd_url STRING,
        image_url STRING,
        specs STRING,
        shop_name STRING,
        comment_count INT,
        crawl_time TIMESTAMP
    )
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY ','
    STORED AS TEXTFILE
    """

    run_beeline_query(create_price_history_table)
    run_beeline_query(create_products_table)

def load_data_to_hive(hdfs_path, hive_table):
    """从 HDFS 加载数据到 Hive"""
    load_cmd = f"""
    LOAD DATA INPATH '{hdfs_path}'
    OVERWRITE INTO TABLE {hive_table}
    """
    run_beeline_query(load_cmd)

def main():
    # 验证文件路径
    for csv_file in [price_history_csv, products_csv]:
        if not os.path.exists(csv_file):
            print(f"错误：文件 {csv_file} 不存在，请检查路径")
            return

    # 上传 CSV 到 HDFS
    if not (upload_to_hdfs(price_history_csv, hdfs_price_history) and
            upload_to_hdfs(products_csv, hdfs_products)):
        return

    # 创建表
    create_tables()

    # 加载数据
    load_data_to_hive(hdfs_price_history, price_history_table)
    load_data_to_hive(hdfs_products, products_table)

if __name__ == "__main__":
    main()