import pandas as pd
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q, Avg, StdDev
import numpy as np  # 添加 numpy 导入
import re
from django.db.models import IntegerField
from .models import RAM, GPU, CPU, Motherboard, SSD, Cooler, PowerSupply, Chassis, PriceHistory, CPUPriceHistory, \
    RAMPriceHistory, SSDPriceHistory, MotherboardPriceHistory, GPUPriceHistory, CoolerPriceHistory, ChassisPriceHistory, \
    PowerSupplyPriceHistory
from django.db.models import F, FloatField, Case, When, Value
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from .models import Favorite
import json
from django.middleware.csrf import get_token

# 设置日志
logger = logging.getLogger(__name__)

# 定义组件类型到模型类的映射
COMPONENT_MODELS = {
    'ram': RAM,
    'gpu': GPU,
    'cpu': CPU,
    'motherboard': Motherboard,
    'ssd': SSD,
    'cooler': Cooler,
    'power_supply': PowerSupply,
    'chassis': Chassis,
}

# 定义组件类型到历史价格模型的映射
COMPONENT_PRICE_HISTORY_MODELS = {
    'cpu': CPUPriceHistory,
    'ram': RAMPriceHistory,
    'gpu': GPUPriceHistory,
    'motherboard': MotherboardPriceHistory,
    'ssd': SSDPriceHistory,
    'cooler': CoolerPriceHistory,
    'power_supply': PowerSupplyPriceHistory,
    'chassis': ChassisPriceHistory,
}

# 主页视图
@require_GET
def index(request):
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
    return render(request, 'analyzer/index.html', {'user': request.user})


#
@require_GET
def search(request):
    try:
        query = request.GET.get('q', '')
        component_type = request.GET.get('type', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        sort_by = request.GET.get('sort_by', '')
        sort_order = request.GET.get('sort_order', 'asc')
        brand = request.GET.get('brand', '')
        series = request.GET.get('series', '')

        model = COMPONENT_MODELS.get(component_type)
        if model:
            items = model.objects.all()
            if component_type == 'cpu':
                if brand:
                    if brand.lower() == 'amd':
                        items = items.filter(title__icontains='AMD')
                    elif brand.lower() == 'intel':
                        items = items.filter(title__icontains='Intel')
                if series:
                    items = items.filter(cpu_series__icontains=series)
        else:
            items = RAM.objects.none()

        if query:
            items = items.filter(title__icontains=query)

        valid_sort_fields = ['reference_price', 'jd_price']
        valid_sort_orders = ['asc', 'desc']
        if sort_by in valid_sort_fields and sort_order in valid_sort_orders:
            order_prefix = '' if sort_order == 'asc' else '-'
            # 使用 annotate 和 Case 处理 NULL 值
            items = items.annotate(
                is_null=Case(
                    When(**{f"{sort_by}__isnull": True}, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('is_null', f"{order_prefix}{sort_by}")
        else:
            items = items.order_by('id')

        paginator = Paginator(items, per_page)
        page_obj = paginator.page(page_number)

        results = [
            {
                'id': item.id,
                'type': component_type or 'unknown',
                'title': item.title,
                'reference_price': float(item.reference_price) if item.reference_price is not None else '暂无',
                'jd_price': float(item.jd_price) if item.jd_price is not None else '暂无',
                # 检查是否已收藏
                'is_favorited': request.user.is_authenticated and Favorite.objects.filter(
                    user=request.user,
                    content_type=ContentType.objects.get_for_model(model),
                    object_id=item.id
                ).exists()
            } for item in page_obj
        ]

        return JsonResponse({
            'results': results,
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'csrf_token': get_token(request)
        })
    except ValueError as ve:
        logger.error(f"Search error: {str(ve)}", exc_info=True)
        return JsonResponse({'error': f'参数错误: {str(ve)}'}, status=400)
    except Exception as e:
        logger.error(f"Search error for type {component_type}: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

# 获取 CPU 系列视图
@require_GET
def get_cpu_series(request):
    try:
        brand = request.GET.get('brand', '').lower()
        if not brand:
            return JsonResponse({'error': 'Brand parameter is required'}, status=400)

        if brand == 'amd':
            items = CPU.objects.filter(Q(title__icontains='AMD') | Q(title__icontains='锐龙'))
        elif brand == 'intel':
            items = CPU.objects.filter(
                Q(title__icontains='Intel') |
                Q(title__icontains='英特尔') |
                Q(title__icontains='酷睿')
            )
        else:
            return JsonResponse({'error': 'Invalid brand'}, status=400)

        series = items.exclude(cpu_series__isnull=True).exclude(cpu_series__exact='') \
            .values_list('cpu_series', flat=True).distinct()

        def normalize_series(name):
            name = (name.replace('酷睿', 'Core')
                    .replace('赛扬', 'Celeron')
                    .replace('奔腾', 'Pentium')
                    .replace('系列', ''))
            name = re.sub(r'Corei(\d)', r'Core i\1', name)
            return re.sub(r'\s+', ' ', name).strip()

        normalized_series = sorted(list(set(normalize_series(s) for s in series if s)))
        return JsonResponse({'series': normalized_series, 'brand': brand}, json_dumps_params={'ensure_ascii': False})
    except Exception as e:
        logger.error(f"Error in get_cpu_series: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import timedelta
import logging
from .models import RAM, GPU, CPU, Motherboard, SSD, Cooler, PowerSupply, Chassis, CPUPriceHistory, PriceHistory

logger = logging.getLogger(__name__)



@require_GET
def detail(request, component_type, id):
    """获取配件详情，包含历史价格"""
    try:
        # 验证组件类型
        if component_type not in COMPONENT_MODELS:
            return JsonResponse({'error': f'不支持的配件类型: {component_type}'}, status=400)

        # 获取模型
        model = COMPONENT_MODELS[component_type]
        item = model.objects.filter(id=id).first()
        if not item:
            return JsonResponse({'error': '配件不存在'}, status=404)

        # 获取历史价格
        price_history_model = COMPONENT_PRICE_HISTORY_MODELS.get(component_type)
        if price_history_model:
            # 动态查询历史价格，假设每个模型有外键字段名为小写组件类型（例如 'ram', 'cpu'）
            filter_kwargs = {component_type: item}
            price_history = price_history_model.objects.filter(
                **filter_kwargs,
                date__gte=timezone.now().date() - timedelta(days=90)
            ).order_by('date')
        else:
            return JsonResponse({'error': f'历史价格模型未定义: {component_type}'}, status=500)

        logger.info(f"Price history for {component_type}/{id}: {price_history.count()} records")

        # 准备价格历史数据
        price_history_data = [
            {
                'date': item.date.strftime('%Y-%m-%d'),
                'price': float(item.price)
            } for item in price_history
        ]
        if not price_history_data:
            # 使用 reference_price 或 jd_price，优先选择 reference_price
            price = item.reference_price if item.reference_price is not None else item.jd_price
            if price is None:
                price = 0.0  # 防止价格为 None
            current_date = timezone.now().date()
            # 生成 90 天的恒定价格数据（每天一条记录）
            price_history_data = [
                {
                    'date': (current_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'price': float(price)
                } for i in range(90, -1, -1)  # 从 90 天前到今天
            ]

        # 构建响应数据
        data = {
            'title': item.title,
            'reference_price': float(item.reference_price) if item.reference_price is not None else '暂无',
            'jd_price': float(item.jd_price) if item.jd_price is not None else '暂无',
            'jd_link': item.jd_link or '',
            'product_image': item.product_image,
            'product_parameters': item.product_parameters or '',
            'price_history': price_history_data
        }

        # 添加组件特定字段
        if component_type == 'cpu':
            data.update({
                'cpu_series': item.cpu_series or '',
                'core_count': item.core_count or '',
                'thread_count': item.thread_count or '',
                'cpu_frequency': item.cpu_frequency or '',
            })
        elif component_type == 'gpu':
            data.update({
                'chip_manufacturer': item.chip_manufacturer or '',
                'memory_size': item.memory_size or '',
                'core_clock': item.core_clock or '',
            })
        elif component_type == 'motherboard':
            data.update({
                'chipset': item.chipset or '',
                'memory_type': item.memory_type or '',
                'form_factor': item.form_factor or '',
            })

        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Detail error for {component_type}/{id}: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
# 价格统计视图


@require_GET
def price_stats(request):
    """获取价格和销量统计"""
    try:
        component_type = request.GET.get('type', 'cpu')
        if component_type not in COMPONENT_MODELS:
            return JsonResponse({'error': f'不支持的配件类型: {component_type}'}, status=400)

        cache_key = f'price_stats_{component_type}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached data for {cache_key}")
            return JsonResponse(cached_data)

        model = COMPONENT_MODELS[component_type]
        # 查询价格、评论数、标题
        products = model.objects.filter(reference_price__isnull=False, reference_price__gt=0).values(
            'reference_price', 'comment_count', 'title'
        )

        if not products:
            return JsonResponse({
                'price_distribution': [],
                'sales_distribution': [],
                # 'price_comment_scatter': [],
                'sales_ranking': [],
                'total_count': 0,
                'median_price': None,
                'avg_price': None,
                'std_dev_price': None,
                'total_comments': 0,
                'avg_comments': None,
                'max_comments': None,
                'message': f'暂无 {component_type} 的价格或销量数据'
            })

        # 转换为 DataFrame
        df = pd.DataFrame.from_records(products)

        # 清洗 comment_count
        def clean_comment_count(x):
            if pd.isna(x) or not x:
                return 0
            x = str(x).lower().strip()
            try:
                if x.endswith('k'):
                    return float(x[:-1]) * 1000
                if x.endswith('w'):
                    return float(x[:-1]) * 10000
                return int(x) if x.replace('.', '').isdigit() else 0
            except (ValueError, TypeError):
                return 0

        df['comment_count'] = df['comment_count'].apply(clean_comment_count)

        # 价格统计
        prices = df['reference_price'].astype(float)
        total_count = len(prices)
        median_price = float(np.median(prices)) if total_count > 0 else None
        avg_price = float(np.mean(prices)) if total_count > 0 else None
        std_dev_price = float(np.std(prices)) if total_count > 1 else 0.0

        # 价格分布
        min_price = np.floor(prices.min() / 10) * 10
        max_price = np.ceil(prices.max() / 10) * 10
        target_bins = 10
        price_range = max_price - min_price
        bin_width = max(10, np.ceil(price_range / target_bins / 10) * 10)
        bins = np.arange(min_price, max_price + bin_width, bin_width)
        hist, bin_edges = np.histogram(prices, bins=bins, density=False)
        price_distribution = [
            {'range': f'{int(bin_edges[i])}-{int(bin_edges[i + 1])}', 'count': int(hist[i])}
            for i in range(len(hist)) if hist[i] > 0
        ]

        # 销量分布
        comments = df['comment_count'].astype(float)
        max_comments = comments.max() if total_count > 0 else 0
        bin_width_comments = max(100, np.ceil(max_comments / target_bins / 100) * 100)
        bins_comments = np.arange(0, max_comments + bin_width_comments, bin_width_comments)
        hist_comments, bin_edges_comments = np.histogram(comments, bins=bins_comments, density=False)
        sales_distribution = [
            {'range': f'{int(bin_edges_comments[i])}-{int(bin_edges_comments[i + 1])}', 'count': int(hist_comments[i])}
            for i in range(len(hist_comments)) if hist_comments[i] > 0
        ]

        # # 价格与销量散点图
        # price_comment_scatter = [
        #     {'price': float(row['reference_price']), 'comment_count': float(row['comment_count'])}
        #     for _, row in df.iterrows() if row['comment_count'] > 0
        # ]

        # 销量排名
        sales_ranking = (
            df[df['comment_count'] > 0][['title', 'comment_count']]
            .sort_values('comment_count', ascending=False)
            .head(10)
            .to_dict('records')
        )

        # 销量统计
        total_comments = int(comments.sum()) if total_count > 0 else 0
        avg_comments = float(comments.mean()) if total_count > 0 else None

        data = {
            'price_distribution': price_distribution,
            'sales_distribution': sales_distribution,
            # 'price_comment_scatter': price_comment_scatter,
            'sales_ranking': sales_ranking,
            'total_count': total_count,
            'median_price': median_price,
            'avg_price': avg_price,
            'std_dev_price': std_dev_price,
            'total_comments': total_comments,
            'avg_comments': avg_comments,
            'max_comments': max_comments,
            'message': ''
        }
        cache.set(cache_key, data, timeout=3600)
        logger.debug(f"Caching response for {cache_key}")
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error in price_stats: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def average_price_trend(request):
    """获取平均价格趋势"""
    try:
        component_type = request.GET.get('type', 'cpu')
        if component_type not in COMPONENT_MODELS:
            return JsonResponse({'error': f'不支持的配件类型: {component_type}'}, status=400)

        cache_key = f'average_price_trend_{component_type}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached data for {cache_key}")
            return JsonResponse(cached_data)

        ninety_days_ago = timezone.now().date() - timedelta(days=90)
        price_history_model = COMPONENT_PRICE_HISTORY_MODELS.get(component_type)
        if not price_history_model:
            return JsonResponse({'error': f'未定义 {component_type} 的历史价格模型'}, status=400)

        trend_data = price_history_model.objects.filter(
            date__gte=ninety_days_ago
        ).values('date').annotate(avg_price=Avg('price')).order_by('date')

        data = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'avg_price': float(item['avg_price']) if item['avg_price'] is not None else 0.0
            } for item in trend_data
        ]

        if not data:
            model = COMPONENT_MODELS[component_type]
            avg_price = model.objects.filter(
                reference_price__isnull=False, reference_price__gt=0
            ).aggregate(Avg('reference_price'))['reference_price__avg']
            if avg_price is None:
                return JsonResponse({
                    'data': [],
                    'message': f'暂无 {component_type} 的历史价格数据'
                })
            current_date = timezone.now().date()
            data = [
                {
                    'date': (current_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'avg_price': float(avg_price)
                } for i in range(90, -1, -1)
            ]

        response = {'data': data, 'message': ''}
        cache.set(cache_key, response, timeout=3600)
        logger.debug(f"Caching response for {cache_key}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in average_price_trend: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
@require_GET
def average_price_trend(request):
    """获取平均价格趋势"""
    try:
        component_type = request.GET.get('type', 'cpu')
        if component_type not in COMPONENT_MODELS:
            return JsonResponse({'error': f'不支持的配件类型: {component_type}'}, status=400)

        cache_key = f'average_price_trend_{component_type}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached data for {cache_key}")
            return JsonResponse(cached_data)

        ninety_days_ago = timezone.now().date() - timedelta(days=90)
        price_history_model = COMPONENT_PRICE_HISTORY_MODELS.get(component_type)
        if not price_history_model:
            return JsonResponse({'error': f'未定义 {component_type} 的历史价格模型'}, status=400)

        trend_data = price_history_model.objects.filter(
            date__gte=ninety_days_ago
        ).values('date').annotate(avg_price=Avg('price')).order_by('date')

        data = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'avg_price': float(item['avg_price']) if item['avg_price'] is not None else 0.0
            } for item in trend_data
        ]

        if not data:
            # 生成模拟数据
            model = COMPONENT_MODELS[component_type]
            avg_price = model.objects.filter(
                reference_price__isnull=False, reference_price__gt=0
            ).aggregate(Avg('reference_price'))['reference_price__avg']
            if avg_price is None:
                return JsonResponse({
                    'data': [],
                    'message': f'暂无 {component_type} 的历史价格数据'
                })
            current_date = timezone.now().date()
            data = [
                {
                    'date': (current_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'avg_price': float(avg_price)
                } for i in range(90, -1, -1)
            ]

        response = {'data': data, 'message': ''}
        cache.set(cache_key, response, timeout=3600)
        logger.debug(f"Caching response for {cache_key}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in average_price_trend: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)

logger = logging.getLogger(__name__)


from django.http import JsonResponse

# 收藏
@csrf_exempt
def favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '请登录'}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content_type = ContentType.objects.get(model=data['type'])
            Favorite.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=data['id']
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Favorite add error: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            content_type = ContentType.objects.get(model=data['type'])
            Favorite.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=data['id']
            ).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Favorite delete error: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': '不支持的请求方法'}, status=405)


@require_GET
def favorites_list(request):
    """获取用户收藏列表"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '请登录'}, status=401)
    try:
        # 查询用户收藏
        favorites = Favorite.objects.filter(user=request.user).select_related('content_type')
        results = []
        for fav in favorites:
            # 获取硬件对象
            model = ContentType.objects.get(id=fav.content_type_id).model_class()
            item = model.objects.filter(id=fav.object_id).first()
            if item:
                results.append({
                    'id': item.id,
                    'type': fav.content_type.model,
                    'title': item.title,
                    'reference_price': float(item.reference_price) if item.reference_price else '暂无',
                    'jd_price': float(item.jd_price) if item.jd_price else '暂无'
                })
        # 返回结果
        return JsonResponse({
            'results': results,
            'total': len(results),
            'csrf_token': get_token(request)
        })
    except Exception as e:
        logger.error(f"Favorites list error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)