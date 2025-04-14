from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db.models import Q, Avg, StdDev
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
import statistics
import math
import re
from django.db.models import IntegerField
from .models import RAM, GPU, CPU, Motherboard, SSD, Cooler, PowerSupply, Chassis, PriceHistory
from django.db.models import F, FloatField, Case, When, Value
from django.http import JsonResponse
import logging

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
    'case': Chassis,
}

# 主页视图
def index(request):
    return render(request, 'analyzer/index.html')

# 搜索视图from django.db.models import Case, When, Value, IntegerField
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
                'jd_price': float(item.jd_price) if item.jd_price is not None else '暂无'
            } for item in page_obj
        ]

        return JsonResponse({
            'results': results,
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
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


@require_GET
def detail(request, component_type, id):
    try:
        model = COMPONENT_MODELS.get(component_type)
        if not model:
            logger.error(f"Invalid component type: {component_type}")
            return JsonResponse({'error': f'无效的配件类型: {component_type}'}, status=400)

        item = model.objects.get(id=id)
        data = {
            'title': item.title,
            'reference_price': float(item.reference_price) if item.reference_price is not None else '暂无',
            'jd_price': float(item.jd_price) if item.jd_price is not None else '暂无',
            'jd_link': item.jd_link,
            'product_image': item.product_image,
            'product_parameters': item.product_parameters or ''
        }
        return JsonResponse(data)

    except model.ObjectDoesNotExist:
        logger.error(f"Component not found: {component_type} ID {id}")
        return JsonResponse({'error': f'未找到配件: {component_type} ID {id}'}, status=404)
    except Exception as e:
        logger.error(f"Detail error for {component_type} {id}: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'服务器错误: {str(e)}'}, status=500)
# 价格统计视图
@require_GET
def price_stats(request):
    try:
        component_type = request.GET.get('type', 'cpu').lower()
        cache_key = f'price_stats_{component_type}'
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.debug(f"Returning cached data for {cache_key}")
            return JsonResponse(cached_data)

        logger.info(f"Fetching price stats for {component_type}")
        model = COMPONENT_MODELS.get(component_type, CPU)
        prices = list(model.objects.filter(reference_price__isnull=False)
                      .values_list('reference_price', flat=True))
        price_data = []
        total_count = len(prices)

        if prices:
            prices = sorted(prices)
            num_bins = min(6, max(2, total_count // 5))  # 动态分箱，至少2个
            if total_count >= num_bins:
                # 使用分位数分箱
                quantiles = [i / num_bins for i in range(num_bins + 1)]
                bins = []
                for q in quantiles:
                    index = int(total_count * q)
                    if index >= total_count:  # 防止索引越界
                        index = total_count - 1
                    bins.append(prices[index])
                bins = sorted(list(set([math.floor(b) for b in bins])))
                if len(bins) < 2:
                    bins = [min(prices), max(prices) + 1]
                bin_labels = [f'{int(bins[i])}-{int(bins[i+1]-1)}' for i in range(len(bins)-1)]

                for i in range(len(bins) - 1):
                    min_p = bins[i]
                    max_p = bins[i + 1]
                    count = sum(1 for p in prices if min_p <= p < max_p)
                    if count > 0:  # 仅包含非空区间
                        price_data.append({'range': bin_labels[i], 'count': count})
            else:
                # 数据量少时，使用单一区间
                price_data.append({
                    'range': f'{int(min(prices))}-{int(max(prices))}',
                    'count': total_count
                })

        # 计算统计指标
        stats = model.objects.filter(reference_price__isnull=False).aggregate(
            avg_price=Avg('reference_price'),
            std_dev_price=StdDev('reference_price')
        )
        median_price = statistics.median(prices) if prices else None

        response_data = {
            'price_distribution': price_data,
            'total_count': total_count,
            'median_price': float(median_price) if median_price is not None else None,
            'std_dev_price': float(stats['std_dev_price']) if stats['std_dev_price'] else None,
            'avg_price': float(stats['avg_price']) if stats['avg_price'] else None,
            'status': 'success',
            'message': 'No price data available' if not prices else ''
        }
        cache.set(cache_key, response_data, timeout=3600)  # 缓存1小时
        logger.debug(f"Price stats response: {response_data}")
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error in price_stats: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

# 价格趋势视图
@require_GET
def average_price_trend(request):
    try:
        component_type = request.GET.get('type', 'cpu').lower()
        logger.info(f"Fetching price trend for {component_type}")
        model = COMPONENT_MODELS.get(component_type, CPU)
        component_ids = list(model.objects.values_list('id', flat=True))

        # 限制最近 90 天数据以提高性能
        ninety_days_ago = timezone.now() - timedelta(days=90)
        history = (PriceHistory.objects
                   .filter(
                       component_type=component_type,
                       component_id__in=component_ids,
                       date__gte=ninety_days_ago
                   )
                   .order_by('date'))

        trend_data = (history
                      .annotate(date_only=TruncDate('date'))
                      .values('date_only')
                      .annotate(avg_price=Avg('price'))
                      .order_by('date_only'))

        data = [{
            'date': entry['date_only'].strftime('%Y-%m-%d'),
            'avg_price': float(entry['avg_price'])
        } for entry in trend_data]

        response = {
            'data': data,
            'message': 'No price history data available' if not data else ''
        }
        logger.debug(f"Price trend response: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in average_price_trend: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)



logger = logging.getLogger(__name__)


from django.http import JsonResponse

@require_GET
def generate_configuration(request):
    try:
        # 获取用户输入
        budget = float(request.GET.get('budget', 5000))
        usage = request.GET.get('usage', 'general')  # 默认用途为通用
        brand_preference = request.GET.get('brand_preference', '').lower()  # 品牌偏好

        # 配件预算比例（可根据用途调整）
        component_weights = {
            'cpu': 0.3,
            'gpu': 0.3,
            'ram': 0.1,
            'motherboard': 0.1,
            'ssd': 0.1,
            'power_supply': 0.05,
            'case': 0.05,
            'cooler': 0.05
        }

        # 计算每种配件的预算
        component_budgets = {k: v * budget for k, v in component_weights.items()}

        # 初始化配置单
        configuration = []
        total_price = 0

        # 定义每种配件的选择逻辑
        for component, comp_budget in component_budgets.items():
            model = COMPONENT_MODELS[component]
            queryset = model.objects.filter(reference_price__lte=comp_budget).order_by('reference_price')

            # 品牌过滤
            if brand_preference:
                queryset = queryset.filter(title__icontains=brand_preference)

            # 获取最优配件
            selected = queryset.first()
            if selected:
                configuration.append({
                    'type': component,
                    'title': selected.title,
                    'price': float(selected.reference_price),
                })
                total_price += selected.reference_price

        # 检查总价是否超出预算
        if total_price > budget:
            return JsonResponse({'error': '无法在预算内生成配置单，请增加预算或减少需求'}, status=400)

        return JsonResponse({
            'configuration': configuration,
            'total_price': float(total_price),
            'budget': budget,
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


