from pyhive import hive
import pandas as pd


def test_hive_connection():
    # 连接参数 - 替换为你的虚拟机实际信息
    host = '192.168.80.128'  # 虚拟机IP地址
    port = 10000  # HiveServer2端口，默认10000
    username = 'noode1'  # 你的用户名
    password = 'root'  # 如果有密码
    database = 'default'  # 默认数据库
    auth = 'NOSASL',
    try:
        # 建立连接
        connection = hive.connect(
            host=host,
            port=port,
            username=username,

            database=database,
            auth='NOSASL'  # 根据你的认证方式调整，如 'NOSASL' 或 'LDAP'
        )

        print("成功连接到Hive服务器!")

        # 创建游标
        cursor = connection.cursor()

        # 执行测试查询
        test_query = "" \
                     "SHOW DATABASES" \
                     ""  # 或使用简单查询 "SELECT 1"

        cursor.execute(test_query)

        # 获取结果
        results = cursor.fetchall()

        # 打印结果
        print("\n查询结果:")
        for row in results:
            print(row)

        # 可选：将结果转为Pandas DataFrame
        df = pd.DataFrame(results, columns=[desc[0] for desc in cursor.description])
        print("\nDataFrame格式:")
        print(df)

    except Exception as e:
        print(f"连接或查询失败: {e}")
    finally:
        # 关闭连接
        if 'connection' in locals():
            connection.close()
            print("\n连接已关闭")


if __name__ == "__main__":
    test_hive_connection()