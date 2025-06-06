# analyzer/admin.py
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from .models import (
    Motherboard, MotherboardPriceHistory,
    CPU, CPUPriceHistory,
    GPU, GPUPriceHistory,
    RAM, RAMPriceHistory,
    SSD, SSDPriceHistory,
    Cooler, CoolerPriceHistory,
    PowerSupply, Chassis, ChassisPriceHistory,
    Favorite, PriceAlert, PriceChangeNotification
)

# 自定义过滤器：按价格范围
class PriceRangeFilter(SimpleListFilter):
    title = _('价格范围')
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('0_100', _('0-100')),
            ('100_500', _('100-500')),
            ('500_1000', _('500-1000')),
            ('1000_plus', _('1000以上')),
        )

    def queryset(self, request, queryset):
        if self.value() == '0_100':
            return queryset.filter(price__gte=0, price__lte=100)
        if self.value() == '100_500':
            return queryset.filter(price__gt=100, price__lte=500)
        if self.value() == '500_1000':
            return queryset.filter(price__gt=500, price__lte=1000)
        if self.value() == '1000_plus':
            return queryset.filter(price__gt=1000)
        return queryset
@admin.register(Motherboard)
class MotherboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price', 'chipset', 'form_factor')
    search_fields = ('title', 'product_id', 'chipset')
    list_filter = ('chipset', 'form_factor', 'jd_store')
    ordering = ('title',)

@admin.register(MotherboardPriceHistory)
class MotherboardPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('motherboard', 'price', 'date', 'created_at')
    list_filter = ('date', 'motherboard')
    search_fields = ('motherboard__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['motherboard']

@admin.register(CPU)
class CPUAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price', 'cpu_series', 'core_count')
    search_fields = ('title', 'product_id', 'cpu_series')
    list_filter = ('cpu_series', 'socket_type', 'jd_store')
    ordering = ('title',)

@admin.register(CPUPriceHistory)
class CPUPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('cpu', 'price', 'date', 'created_at', 'price_change')
    list_filter = ('date', PriceRangeFilter, 'cpu__cpu_series')
    search_fields = ('cpu__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['cpu']
    list_per_page = 20

    def price_change(self, obj):
        previous = CPUPriceHistory.objects.filter(
            cpu=obj.cpu,
            date__lt=obj.date
        ).order_by('-date').first()
        if previous:
            change = obj.price - previous.price
            return f"{'+' if change > 0 else ''}{change:.2f}"
        return 'N/A'

@admin.register(GPU)
class GPUAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price', 'chip_manufacturer', 'gpu_chip')
    search_fields = ('title', 'product_id', 'gpu_chip')
    list_filter = ('chip_manufacturer', 'chip_series', 'jd_store')
    ordering = ('title',)

@admin.register(GPUPriceHistory)
class GPUPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('gpu', 'price', 'date', 'created_at')
    list_filter = ('date', 'gpu')
    search_fields = ('gpu__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['gpu']

@admin.register(RAM)
class RAMAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price', 'capacity', 'memory_type')
    search_fields = ('title', 'product_id', 'memory_type')
    list_filter = ('memory_type', 'capacity', 'jd_store')
    ordering = ('title',)

@admin.register(RAMPriceHistory)
class RAMPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('ram', 'price', 'date', 'created_at')
    list_filter = ('date', 'ram')
    search_fields = ('ram__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['ram']

@admin.register(SSD)
class SSDAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price', 'capacity', 'interface')
    search_fields = ('title', 'product_id', 'interface')
    list_filter = ('interface', 'capacity', 'jd_store')
    ordering = ('title',)

@admin.register(SSDPriceHistory)
class SSDPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('ssd', 'price', 'date', 'created_at')
    list_filter = ('date', 'ssd')
    search_fields = ('ssd__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['ssd']

@admin.register(Cooler)
class CoolerAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price')
    search_fields = ('title', 'product_id')
    list_filter = ('jd_store',)
    ordering = ('title',)

@admin.register(CoolerPriceHistory)
class CoolerPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('cooler', 'price', 'date', 'created_at')
    list_filter = ('date', 'cooler')
    search_fields = ('cooler__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['cooler']

@admin.register(PowerSupply)
class PowerSupplyAdmin(admin.ModelAdmin):
    list_display = ('title', 'jd_price', 'reference_price', 'rated_power', 'psu_type')
    search_fields = ('title', 'rated_power')
    list_filter = ('psu_type', 'jd_store')
    ordering = ('title',)

@admin.register(Chassis)
class ChassisAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_id', 'jd_price', 'reference_price', 'chassis_type', 'compatible_motherboard')
    search_fields = ('title', 'product_id', 'chassis_type')
    list_filter = ('chassis_type', 'compatible_motherboard', 'jd_store')
    ordering = ('title',)

@admin.register(ChassisPriceHistory)
class ChassisPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('chassis', 'price', 'date', 'created_at')
    list_filter = ('date', 'chassis')
    search_fields = ('chassis__title', 'price')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ['chassis']

# @admin.register(Favorite)
# class FavoriteAdmin(admin.ModelAdmin):
#     list_display = ('user', 'content_type', 'object_id', 'content_object', 'created_at')
#     list_filter = ('content_type', 'created_at')
#     search_fields = ('user__username', 'content_object__title')
#     readonly_fields = ('created_at',)
#     raw_id_fields = ('user',)
#     list_select_related = ('user', 'content_type')

@admin.register(PriceAlert)
class PriceAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorite', 'previous_price', 'current_price', 'sent_at', 'method', 'is_read')
    list_filter = ('method', 'is_read', 'sent_at')
    search_fields = ('user__username', 'favorite__content_object__title')
    readonly_fields = ('sent_at',)
    raw_id_fields = ('user', 'favorite')
    list_select_related = ('user', 'favorite')

@admin.register(PriceChangeNotification)
class PriceChangeNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_type', 'object_id', 'component', 'current_price', 'previous_price', 'notified_at')
    list_filter = ('content_type', 'notified_at')
    search_fields = ('user__username', 'component__title')
    readonly_fields = ('notified_at',)
    raw_id_fields = ('user',)
    list_select_related = ('user', 'content_type')

