from pyhive import hive
import csv

# 配置信息
HIVE_HOST = '192.168.80.128'
HIVE_PORT = 10000
HIVE_USERNAME = 'node1'
DATABASE_NAME = 'default'

# Hive 表定义
TABLE_PRICE_HISTORY = 'ram_price_history'
TABLE_PRODUCTS = 'ram_products'

# CSV 文件路径
CSV_PRICE_HISTORY = '../spider/csv/RAM_price_history.csv'
CSV_PRODUCTS = '../spider/csv/RAM_products.csv'


# 创建 Hive 连接
def create_connection():
    conn = hive.Connection(
        host=HIVE_HOST,
        port=HIVE_PORT,
        username=HIVE_USERNAME,
        auth='NOSASL',
        database=DATABASE_NAME
    )
    cursor = conn.cursor()
    # 设置 Hive 参数
    cursor.execute('SET hive.support.concurrency=false')
    cursor.execute('SET hive.exec.mode.local.auto=true')
    return conn


# 删除 Hive 表
def drop_table_if_exists(cursor, table_name):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")


# 创建 Hive 表
def create_tables(cursor):
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


# 导入数据到 Hive
def load_data_to_hive(cursor, table_name, csv_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)  # 保持 reader 是一个迭代器
        total_rows = sum(1 for _ in open(csv_file, 'r', encoding='utf-8')) - 1  # 减去表头行
        file.seek(0)  # 重置文件指针
        next(reader)  # 跳过表头

        for index, row in enumerate(reader, start=1):
            # 转换为 Hive 的 INSERT INTO 语句
            values = ', '.join(["'" + str(value).replace("'", "''") + "'" for value in row])
            query = f"INSERT INTO TABLE {table_name} VALUES ({values})"

            # 打印插入的 SQL 内容
            print(f"[DEBUG] 插入数据: {query}")

            # 执行 SQL 插入
            cursor.execute(query)

            # 显示进度
            print(f"正在导入 {table_name} 数据：{index}/{total_rows} 行完成", end='\r')

        print()  # 换行以清理进度显示

# 主函数
def main():
    connection = create_connection()
    cursor = connection.cursor()
    try:
        # 创建表
        create_tables(cursor)

        # 导入数据
        print("开始导入 ram_price_history.csv 数据...")
        load_data_to_hive(cursor, TABLE_PRICE_HISTORY, CSV_PRICE_HISTORY)
        print("ram_price_history.csv 数据导入完成！")

        print("开始导入 ram_products.csv 数据...")
        load_data_to_hive(cursor, TABLE_PRODUCTS, CSV_PRODUCTS)
        print("ram_products.csv 数据导入完成！")
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    main()