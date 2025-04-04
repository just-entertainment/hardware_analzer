from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import RAM, GPU, CPU, Motherboard, SSD, Cooler, PowerSupply

def index(request):
    return render(request, 'index.html')

@require_GET
def search(request):
    try:
        query = request.GET.get('q', '')
        component_type = request.GET.get('type', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        sort_by = request.GET.get('sort_by', '')
        sort_order = request.GET.get('sort_order', 'asc')

        if component_type == 'ram':
            items = RAM.objects.all()
        elif component_type == 'gpu':
            items = GPU.objects.all()
        elif component_type == 'cpu':
            items = CPU.objects.all()
        elif component_type == 'motherboard':
            items = Motherboard.objects.all()
        elif component_type == 'ssd':
            items = SSD.objects.all()
        elif component_type == 'cooler':
            items = Cooler.objects.all()
        elif component_type == 'power_supply':
            items = PowerSupply.objects.all()
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