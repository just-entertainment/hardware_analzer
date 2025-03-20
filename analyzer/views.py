from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from .models import RAM, GPU

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

        print(f"Params: type={component_type}, q={query}, sort_by={sort_by}, sort_order={sort_order}")

        if component_type == 'ram':
            items = RAM.objects.all()
        elif component_type == 'gpu':
            items = GPU.objects.all()
        else:
            items = RAM.objects.none()

        if query:
            items = items.filter(title__icontains=query)

        # 排序
        valid_sort_fields = ['reference_price', 'jd_price']
        valid_sort_orders = ['asc', 'desc']
        if sort_by in valid_sort_fields and sort_order in valid_sort_orders:
            order_prefix = '' if sort_order == 'asc' else '-'
            print(f"Applying sort: {order_prefix}{sort_by}")
            # 分步执行排序，捕获具体错误
            items = items.order_by(f"{sort_by}__isnull")  # 先按 NULL 排序
            items = items.order_by(f"{order_prefix}{sort_by}")  # 再按值排序
        else:
            print("Using default sort by id")
            items = items.order_by('id')

        # 分页
        paginator = Paginator(items, per_page)
        page_obj = paginator.page(page_number)

        # 调试输出排序结果
        print("Top 5 results after sorting:")
        for item in page_obj.object_list[:5]:
            print(f"Title: {item.title}, Ref Price: {item.reference_price}, JD Price: {item.jd_price}")

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
        print(f"Error during search: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)