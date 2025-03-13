from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import RAM


# 主页面
def index(request):
    return render(request, 'index.html')


def index(request):
    """渲染主页"""
    return render(request, 'index.html')


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import RAM,GPU

def index(request):
    return render(request, 'index.html')

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import RAM, GPU

def index(request):
    return render(request, 'index.html')

@require_GET
def search(request):
    query = request.GET.get('q', '')
    component_type = request.GET.get('type', '')
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    sort_by = request.GET.get('sort_by', '')  # 排序字段: reference_price 或 jd_price
    sort_order = request.GET.get('sort_order', 'asc')  # 排序方向: asc 或 desc

    # 根据类型查询
    if component_type == 'ram':
        items = RAM.objects.all()
    elif component_type == 'gpu':
        items = GPU.objects.all()
    else:
        items = RAM.objects.none()

    # 应用搜索过滤
    if query:
        items = items.filter(title__icontains=query)

    # 应用排序
    if sort_by in ['reference_price', 'jd_price']:
        order_prefix = '' if sort_order == 'asc' else '-'
        items = items.order_by(f"{order_prefix}{sort_by}")
    # 处理 NULL 值（放到最后）
    items = items.order_by(f"{sort_by}__isnull" if sort_by else 'id')

    # 分页
    paginator = Paginator(items, per_page)
    try:
        page_obj = paginator.page(page_number)
    except:
        page_obj = paginator.page(1)

    # 构造返回数据
    results = [
        {
            'type': component_type or 'unknown',
            'title': item.title,
            'reference_price': item.reference_price if item.reference_price is not None else '暂无',
            'jd_price': item.jd_price if item.jd_price is not None else '暂无'
        } for item in page_obj
    ]

    # 返回分页信息
    return JsonResponse({
        'results': results,
        'total': paginator.count,
        'pages': paginator.num_pages,
        'current_page': page_obj.number,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
    })

# 价格涨幅 API
@require_GET
def price_changes(request):
    data = [
        {'name': 'RTX 4090', 'change': '价格上涨 15%', 'price': 12000},
        {'name': 'Ryzen 7 7800X3D', 'change': '价格下跌 5%', 'price': 2800},
    ]
    return JsonResponse(data, safe=False)


# 新品发布 API
@require_GET
def new_releases(request):
    data = [
        {'name': 'Intel Core i9-14900K', 'date': '2025-03-01', 'price': 4500},
        {'name': 'AMD RX 7900 XTX', 'date': '2025-02-20', 'price': 8000},
    ]
    return JsonResponse(data, safe=False)


# 生成配置单 API
@require_GET
def generate_config(request):
    budget = request.GET.get('budget', '')
    try:
        budget = int(budget)
        if budget < 1000:
            return JsonResponse({'error': '预算需至少 ¥1000'})

        configs = [
            {'name': 'CPU', 'item': 'Ryzen 5 5600X', 'price': 1500},
            {'name': 'GPU', 'item': 'RTX 3060', 'price': 2500},
            {'name': 'RAM', 'item': '16GB DDR4', 'price': 500},
            {'name': 'SSD', 'item': '1TB NVMe', 'price': 800},
            {'name': '主板', 'item': 'B550', 'price': 700},
            {'name': '电源', 'item': '650W', 'price': 400},
        ]

        total = 0
        selected_config = []
        for part in configs:
            if total + part['price'] <= budget:
                selected_config.append(part)
                total += part['price']

        if not selected_config:
            return JsonResponse({'error': '预算不足以生成配置'})

        return JsonResponse({'config': selected_config, 'total': total})
    except ValueError:
        return JsonResponse({'error': '请输入有效的预算'})



