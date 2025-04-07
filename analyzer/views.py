from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import RAM, GPU, CPU, Motherboard, SSD, Cooler, PowerSupply,Chassis

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

        model = COMPONENT_MODELS.get(component_type)
        if model:
            items = model.objects.all()
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