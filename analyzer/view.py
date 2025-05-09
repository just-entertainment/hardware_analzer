from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.cache import cache
from django.shortcuts import render
import logging
from pyhive import hive
from thrift.transport import TTransport

logger = logging.getLogger(__name__)

# Hive 连接配置
HIVE_HOST = 'localhost'
HIVE_PORT = 10000
HIVE_DATABASE = 'default'

# 硬件类型映射
COMPONENT_TABLES = {
    'broad': 'broad_products',
    'chassis': 'chassis_products',
}

def index(request):
    """渲染主页面"""
    logger.debug("Rendering index page")
    return render(request, 'analyzer/index.html')

@require_GET
def price_stats(request):
    """价格分布统计"""
    try:
        component_type = request.GET.get('type', 'broad').lower()
        logger.debug(f"Price stats requested for type={component_type}")

        if component_type not in COMPONENT_TABLES:
            logger.warning(f"Unsupported component type: {component_type}. Available: {list(COMPONENT_TABLES.keys())}")
            return JsonResponse({'error': f'不支持的配件类型: {component_type}'}, status=400)

        cache_key = f'price_stats_{component_type}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached data for {cache_key}")
            return JsonResponse(cached_data)

        table = COMPONENT_TABLES[component_type]
        logger.debug(f"Querying Hive table: {table}")

        # 连接 Hive
        conn = hive.connect(host=HIVE_HOST, port=HIVE_PORT, database=HIVE_DATABASE, auth='NOSASL')
        cursor = conn.cursor()

        # 设置 Hive 配置
        cursor.execute('SET hive.support.concurrency=false')
        cursor.execute('SET hive.exec.dynamic.partition=true')
        cursor.execute('SET hive.exec.dynamic.partition.mode=nonstrict')
        cursor.execute('SET mapreduce.job.reduces=2')
        logger.debug("Applied Hive configurations")

        # 验证表存在
        cursor.execute(f"DESCRIBE {table}")
        if not cursor.fetchall():
            logger.error(f"Table {table} does not exist")
            cursor.close()
            conn.close()
            return JsonResponse({'error': f'数据表 {table} 不存在'}, status=500)

        # 查询价格统计
        cursor.execute(f"""
            WITH price_data AS (
                SELECT
                    refer_ence_price,
                    FLOOR(reference_price / 100) * 100 AS price_bin
                FROM {table}
                WHERE reference_price IS NOT NULL AND reference_price > 0
            )
            SELECT
                CONCAT(CAST(price_bin AS STRING), '-', CAST(price_bin + 100 AS STRING)) AS price_range,
                COUNT(*) AS count
            FROM price_data
            GROUP BY price_bin
            ORDER BY price_bin
        """)
        price_distribution = [
            {'price_range': row[0], 'count': int(row[1])}
            for row in cursor.fetchall()
        ]

        # 总体统计
        cursor.execute(f"""
            SELECT
                COUNT(*) AS total_count,
                AVG(reference_price) AS avg_price,
                STDDEV(reference_price) AS std_dev_price,
                PERCENTILE_APPROX(reference_price, 0.5) AS median_price
            FROM {table}
            WHERE reference_price IS NOT NULL AND reference_price > 0
        """)
        stats = cursor.fetchone()
        total_count, avg_price, std_dev_price, median_price = (
            int(stats[0]), float(stats[1]), float(stats[2]), float(stats[3])
        ) if stats else (0, 0, 0, 0)

        cursor.close()
        conn.close()

        if not price_distribution:
            response = {
                'total_count': 0,
                'median_price': 0,
                'avg_price': 0,
                'std_dev_price': 0,
                'price_distribution': [],
                'message': f'暂无 {component_type} 的价格数据'
            }
        else:
            response = {
                'total_count': total_count,
                'median_price': median_price,
                'avg_price': avg_price,
                'std_dev_price': std_dev_price,
                'price_distribution': price_distribution,
                'message': ''
            }

        cache.set(cache_key, response, timeout=3600)
        logger.debug(f"Caching response for {cache_key}")
        return JsonResponse(response)
    except TTransport.TTransportException as e:
        logger.error(f"Hive connection error: {str(e)}", exc_info=True)
        return JsonResponse({'error': '无法连接到 Hive 集群'}, status=500)
    except Exception as e:
        logger.error(f"Error in price_stats: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def average_price_trend(request):
    """价格趋势分析"""
    try:
        component_type = request.GET.get('type', 'broad').lower()
        logger.debug(f"Price trend requested for type={component_type}")

        if component_type not in COMPONENT_TABLES:
            logger.warning(f"Unsupported component type: {component_type}")
            return JsonResponse({'error': f'不支持的配件类型: {component_type}'}, status=400)

        cache_key = f'average_price_trend_{component_type}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached data for {cache_key}")
            return JsonResponse(cached_data)

        table = COMPONENT_TABLES[component_type]
        logger.debug(f"Querying Hive table: {table}")

        # 连接 Hive
        conn = hive.connect(host=HIVE_HOST, port=HIVE_PORT, database=HIVE_DATABASE, auth='NOSASL')
        cursor = conn.cursor()

        # 设置 Hive 配置
        cursor.execute('SET hive.support.concurrency=false')
        cursor.execute('SET hive.exec.dynamic.partition=true')
        cursor.execute('SET hive.exec.dynamic.partition.mode=nonstrict')
        cursor.execute('SET mapreduce.job.reduces=2')
        logger.debug("Applied Hive configurations")

        # 验证表存在
        cursor.execute(f"DESCRIBE {table}")
        if not cursor.fetchall():
            logger.error(f"Table {table} does not exist")
            cursor.close()
            conn.close()
            return JsonResponse({'error': f'数据表 {table} 不存在'}, status=500)

        # 查询价格趋势
        cursor.execute(f"""
            SELECT
                crawl_time AS date,
                AVG(reference_price) AS avg_price
            FROM {table}
            WHERE reference_price IS NOT NULL AND reference_price > 0
            GROUP BY crawl_time
            ORDER BY crawl_time
            LIMIT 90
        """)
        trend_data = [
            {'date': row[0], 'avg_price': float(row[1])}
            for row in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        response = {
            'data': trend_data,
            'message': '' if trend_data else f'暂无 {component_type} 的价格趋势数据'
        }

        cache.set(cache_key, response, timeout=3600)
        logger.debug(f"Caching response for {cache_key}")
        return JsonResponse(response)
    except TTransport.TTransportException as e:
        logger.error(f"Hive connection error: {str(e)}", exc_info=True)
        return JsonResponse({'error': '无法连接到 Hive 集群'}, status=500)
    except Exception as e:
        logger.error(f"Error in average_price_trend: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

# 占位视图
