from pyhive import hive
import os
from tqdm import tqdm

# 配置信息
HIVE_HOST = '192.168.80.128'
HIVE_PORT = 10000
HIVE_USERNAME = 'node1'
DATABASE_NAME = 'default'

# 所有硬件类型配置（使用cleaned文件）
HARDWARE_CONFIG = {
    'broad': {
        'price_history': 'broad_price_history',
        'products': 'broad_products',
        'price_csv': '../spider/cleaned/cleaned_broad_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_broad_products.csv'
    },
    'chassis': {
        'price_history': 'chassis_price_history',
        'products': 'chassis_products',
        'price_csv': '../spider/cleaned/cleaned_chassis_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_chassis_products.csv'
    },
    'cooler': {
        'price_history': 'cooler_price_history',
        'products': 'cooler_products',
        'price_csv': '../spider/cleaned/cleaned_cooler_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_cooler_products.csv'
    },
    'cpu': {
        'price_history': 'cpu_price_history',
        'products': 'cpu_products',
        'price_csv': '../spider/cleaned/cleaned_cpu_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_cpu_products.csv'
    },
    'gpu': {
        'price_history': 'gpu_price_history',
        'products': 'gpu_products',
        'price_csv': '../spider/cleaned/cleaned_gpu_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_gpu_products.csv'
    },
    'power': {
        'price_history': 'power_price_history',
        'products': 'power_products',
        'price_csv': '../spider/cleaned/cleaned_power_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_power_products.csv'
    },
    'ram': {
        'price_history': 'ram_price_history',
        'products': 'ram_products',
        'price_csv': '../spider/cleaned/cleaned_RAM_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_RAM_products.csv'
    },
    'ssd': {
        'price_history': 'ssd_price_history',
        'products': 'ssd_products',
        'price_csv': '../spider/cleaned/cleaned_ssd_price_history.csv',
        'products_csv': '../spider/cleaned/cleaned_ssd_products.csv'
    }
}


def create_connection():
    """创建 Hive 连接"""
    conn = hive.Connection(
        host=HIVE_HOST,
        port=HIVE_PORT,
        username=HIVE_USERNAME,
        auth='NOSASL',
        database=DATABASE_NAME
    )
    cursor = conn.cursor()
    # 设置 Hive 参数优化导入速度
    cursor.execute('SET hive.support.concurrency=false')
    cursor.execute('SET hive.exec.dynamic.partition=true')
    cursor.execute('SET hive.exec.dynamic.partition.mode=nonstrict')
    return conn, cursor


def drop_table_if_exists(cursor, table_name):
    """删除表（如果存在）"""
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")


def create_table(cursor, table_name, is_price_history=False):
    """创建 Hive 表"""
    if is_price_history:
        create_sql = f"""
            CREATE TABLE {table_name} (
                record_id STRING,
                product_id STRING,
                price FLOAT,
                `date` STRING,
                crawl_time STRING
            ) ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    else:
        create_sql = f"""
            CREATE TABLE {table_name} (
                product_id STRING,
                title STRING,
                reference_price FLOAT,
                current_price FLOAT,
                jd_url STRING,
                image_url STRING,
                specs STRING,
                shop_name STRING,
                comment_count STRING,
                crawl_time STRING
            ) ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    cursor.execute(create_sql)


def load_data_to_hive(cursor, table_name, csv_file):
    """加载数据到Hive表"""
    # 获取文件名并处理路径
    filename = os.path.basename(csv_file)
    # 虚拟机上的文件路径（假设已上传到/tmp目录）
    vm_path = f"/tmp/{filename}"

    # 检查文件是否存在
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"本地CSV文件不存在: {csv_file}")

    load_cmd = f"LOAD DATA LOCAL INPATH '{vm_path}' OVERWRITE INTO TABLE {table_name}"
    cursor.execute(load_cmd)


def process_hardware_type(cursor, hw_type, config):
    """处理单个硬件类型的数据导入"""
    print(f"\n正在处理 {hw_type} 数据...")

    try:
        # 删除旧表
        drop_table_if_exists(cursor, config['price_history'])
        drop_table_if_exists(cursor, config['products'])

        # 创建新表
        create_table(cursor, config['price_history'], is_price_history=True)
        create_table(cursor, config['products'], is_price_history=False)

        # 导入数据
        print(f"导入价格历史数据: {os.path.basename(config['price_csv'])}")
        load_data_to_hive(cursor, config['price_history'], config['price_csv'])

        print(f"导入产品数据: {os.path.basename(config['products_csv'])}")
        load_data_to_hive(cursor, config['products'], config['products_csv'])

        print(f"{hw_type} 数据导入完成")
        return True
    except Exception as e:
        print(f"处理 {hw_type} 数据时出错: {str(e)}")
        return False


def main():
    # 创建连接
    connection, cursor = create_connection()

    try:
        # 检查文件是否已上传
        print("请确保已将所有cleaned CSV文件上传到虚拟机的/tmp目录:")
        for hw_type, config in HARDWARE_CONFIG.items():
            print(f"- {os.path.basename(config['price_csv'])}")
            print(f"- {os.path.basename(config['products_csv'])}")
        input("按Enter键继续...")

        # 处理所有硬件类型
        success_count = 0
        for hw_type, config in tqdm(HARDWARE_CONFIG.items(), desc="导入进度"):
            if process_hardware_type(cursor, hw_type, config):
                success_count += 1

        print(f"\n导入完成！成功导入 {success_count}/{len(HARDWARE_CONFIG)} 种硬件类型数据")
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    main()