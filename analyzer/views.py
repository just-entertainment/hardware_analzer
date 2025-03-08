from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render
from .models import CPU


# 主页面
def index(request):
    return render(request, 'index.html')

@require_GET
def search(request):
    query = request.GET.get('q', '')
    brand = request.GET.get('brand', '')
    series = request.GET.get('series', '')
    type = request.GET.get('type', '')

    cpus = CPU.objects.all()
    if query:
        cpus = cpus.filter(name__icontains=query)
    if brand:
        cpus = cpus.filter(brand=brand)
    if series:
        cpus = cpus.filter(series=series)
    if type:
        cpus = cpus.filter(type=type)

    results = [
        {
            'name': cpu.name,
            'brand': cpu.brand,
            'series': cpu.series,
            'type': cpu.type,
            'price': str(cpu.price)
        } for cpu in cpus
    ]
    return JsonResponse({'results': results})

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

