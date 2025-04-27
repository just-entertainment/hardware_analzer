from django.contrib import admin

# Register your models here.
from django.contrib import admin
# analyzer/admin.py

from django.contrib import admin
from .models import SSDPriceHistory, Favorite, RAM, SSD

@admin.register(SSDPriceHistory)
class SSDPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('ssd', 'price', 'date', 'created_at')  # 显示字段
    list_filter = ('date', 'ssd')  # 过滤器
    search_fields = ('ssd__title', 'price')  # 搜索 SSD 标题和价格
    date_hierarchy = 'date'  # 按日期导航
    ordering = ('-date',)  # 默认排序
    readonly_fields = ('created_at',)  # 只读字段

    # 优化外键选择
    autocomplete_fields = ['ssd']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            queryset |= self.model.objects.filter(ssd__title__icontains=search_term)
        except:
            pass
        return queryset, use_distinct

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'content_object', 'created_at')
    list_filter = ('content_type', 'created_at')
    search_fields = ('user__username', 'content_object__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)  # 优化用户选择
    list_select_related = ('user', 'content_type')  # 优化查询

@admin.register(RAM)
class RAMAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price')
    search_fields = ('title', 'product_id')
    list_filter = ('jd_price',)
    ordering = ('title',)

@admin.register(SSD)
class SSDAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price')
    search_fields = ('title', 'product_id')
    list_filter = ('jd_price',)
    ordering = ('title',)