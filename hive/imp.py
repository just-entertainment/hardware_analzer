from pyhive import hive
import os

# 配置信息
HIVE_HOST = '192.168.80.128'
HIVE_PORT = 10000
HIVE_USERNAME = 'node1'
DATABASE_NAME = 'default'


# Hive 表定义
TABLE_PRICE_HISTORY = 'broad_price_history'
TABLE_PRODUCTS = 'broad_products'

# CSV 文件路径（本地Windows路径）
CSV_PRICE_HISTORY = '../spider/csv/broad_price_history.csv'
CSV_PRODUCTS = '../spider/csv/borad_products.csv'


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
    return conn


def drop_table_if_exists(cursor, table_name):
    """删除表（如果存在）"""
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")


def create_tables(cursor):
    """创建 Hive 表"""
    # 删除表（如果存在）
    drop_table_if_exists(cursor, TABLE_PRICE_HISTORY)
    drop_table_if_exists(cursor, TABLE_PRODUCTS)

    # 创建表
    cursor.execute(f"""
        CREATE TABLE {TABLE_PRICE_HISTORY} (
            record_id STRING,
            product_id STRING,
            price FLOAT,
            `date` STRING,
            crawl_time STRING
        ) ROW FORMAT DELIMITED
        FIELDS TERMINATED BY ','
        STORED AS TEXTFILE
    """)

    cursor.execute(f"""
        CREATE TABLE {TABLE_PRODUCTS} (
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
    """)


def load_data_to_hive(cursor, table_name, csv_file):

    # 虚拟机上的文件路径
    vm_path = f"/tmp/{os.path.basename(csv_file)}"

    load_cmd = f"LOAD DATA LOCAL INPATH '{vm_path}' OVERWRITE INTO TABLE {table_name}"
    print(f"正在导入 {table_name} 数据...")
    cursor.execute(load_cmd)
    print(f"{table_name} 数据导入完成！")


def main():
    connection = create_connection()
    cursor = connection.cursor()

    try:
        # 创建表
        create_tables(cursor)

        # 导入数据
        print("请确保已先将以下文件上传到虚拟机的/tmp目录:")
        print(f"- {os.path.basename(CSV_PRICE_HISTORY)}")
        print(f"- {os.path.basename(CSV_PRODUCTS)}")
        input("按Enter键继续...")

        print("开始导入 ram_price_history.csv 数据...")
        load_data_to_hive(cursor, TABLE_PRICE_HISTORY, CSV_PRICE_HISTORY)

        print("开始导入 ram_products.csv 数据...")
        load_data_to_hive(cursor, TABLE_PRODUCTS, CSV_PRODUCTS)

        print("所有数据导入完成！")
    except Exception as e:
        print(f"导入数据时出错: {str(e)}")
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    main()