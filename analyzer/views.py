from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count, Avg


from . import models
from .models import RAM, GPU, CPU, Motherboard, SSD, Cooler, PowerSupply, Chassis

# 定义一个字典来映射组件类型到模型类
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


def index(request):
    return render(request, 'analyzer/index.html')


@require_GET
def search(request):
    try:
        query = request.GET.get('q', '')
        component_type = request.GET.get('type', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        sort_by = request.GET.get('sort_by', '')
        sort_order = request.GET.get('sort_order', 'asc')

        # 新增获取品牌和系列参数
        brand = request.GET.get('brand', '')
        series = request.GET.get('series', '')

        model = COMPONENT_MODELS.get(component_type)
        if model:
            items = model.objects.all()

            # CPU专用过滤
            if component_type == 'cpu':
                if component_type == 'cpu' and brand:
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

        # 排序
        valid_sort_fields = ['reference_price', 'jd_price']
        valid_sort_orders = ['asc', 'desc']
        if sort_by in valid_sort_fields and sort_order in valid_sort_orders:
            order_prefix = '' if sort_order == 'asc' else '-'
            items = items.order_by(f"{sort_by}__isnull")  # 先按 NULL 排序
            items = items.order_by(f"{order_prefix}{sort_by}")  # 再按值排序
        else:
            items = items.order_by('id')

        # 分页
        paginator = Paginator(items, per_page)
        page_obj = paginator.page(page_number)

        results = [
            {
                'id': item.id,
                'type': component_type or 'unknown',
                'title': item.title,
                'reference_price': item.reference_price if item.reference_price is not None else '暂无',
                'jd_price': item.jd_price if item.jd_price is not None else '暂无'
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
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def get_cpu_series(request):
    try:
        from django.db.models import Q
        import re

        brand = request.GET.get('brand', '').lower()

        if not brand:
            return JsonResponse({'error': 'Brand parameter is required'}, status=400)

        # 品牌匹配逻辑
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

        # 获取并清洗系列数据
        series = items.exclude(cpu_series__isnull=True).exclude(cpu_series__exact='') \
            .values_list('cpu_series', flat=True).distinct()

        # 系列名称标准化处理
        def normalize_series(name):
            # 统一替换中文和格式
            name = (name.replace('酷睿', 'Core')
                    .replace('赛扬', 'Celeron')
                    .replace('奔腾', 'Pentium')
                    .replace('系列', ''))
            # 修复Corei3 -> Core i3这样的格式
            name = re.sub(r'Corei(\d)', r'Core i\1', name)
            # 移除多余空格和特殊字符
            return re.sub(r'\s+', ' ', name).strip()

        normalized_series = sorted(list(set(
            normalize_series(s) for s in series if s
        )))

        return JsonResponse({
            'series': normalized_series,
            'brand': brand
        }, json_dumps_params={'ensure_ascii': False})  # 禁用ASCII转义

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def detail(request, component_type, id):
    try:
        model = COMPONENT_MODELS.get(component_type)
        if model:
            item = get_object_or_404(model, id=id)
        else:
            return JsonResponse({'error': 'Invalid component type'}, status=400)

        data = {
            'title': item.title,
            'reference_price': item.reference_price if item.reference_price is not None else '暂无',
            'jd_price': item.jd_price if item.jd_price is not None else '暂无',
            'jd_link': item.jd_link,
            'product_image': item.product_image,
            'product_parameters': item.product_parameters or ''
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def price_stats(request):
    try:
        component_type = request.GET.get('type', 'cpu').lower()
        model_mapping = {
            'cpu': CPU,
            'gpu': GPU,
            'ram': RAM,
            'ssd': SSD,
            # 添加其他模型...
        }

        model = model_mapping.get(component_type, CPU)

        # 价格区间定义
        price_bins = [0, 500, 1000, 1500, 2000, 3000, 5000, float('inf')]
        bin_labels = ['<500', '500-1000', '1000-1500', '1500-2000', '2000-3000', '3000-5000', '5000+']

        # 价格分布统计 - 修复NULL值问题
        price_data = []
        for i in range(len(price_bins) - 1):
            min_p, max_p = price_bins[i], price_bins[i + 1]

            # 构建查询条件
            filters = {
                'reference_price__gte': min_p,
            }
            if max_p != float('inf'):
                filters['reference_price__lt'] = max_p

            # 排除NULL值
            count = model.objects.filter(
                reference_price__isnull=False,
                **filters
            ).count()

            price_data.append({
                'range': bin_labels[i],
                'count': count
            })

        # 品牌分布统计 - 同样修复NULL值问题
        brand_data = []
        if hasattr(model, 'suitable_type'):
            excluded_brands = ['台式机', '企业级(服务器)', '企业级', 'PC/Tablet', '暂无数据']
            brands = model.objects.filter(
                suitable_type__isnull=False,
                reference_price__isnull=False
            ).exclude(
                suitable_type__in=excluded_brands
            ).values('suitable_type') \
                         .annotate(
                count=Count('id'),
                avg_price=Avg('reference_price')
            ).order_by('-count')[:8]  # 限制显示数量

            brand_data = [{
                'brand': b['suitable_type'],
                'count': b['count'],
                'avg_price': float(b['avg_price']) if b['avg_price'] else None
            } for b in brands if b['count'] > 0]  # 过滤掉数量为0的品牌

        return JsonResponse({
            'price_distribution': price_data,
            'brand_distribution': brand_data,
            'status': 'success'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)