from django.contrib import admin
from ordersearch.models import Order, OrderItem, Product
from django_celery_results.models import TaskResult
from django_celery_results.admin import TaskResultAdmin

admin.site.unregister(TaskResult)

@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'status', 'date_done', 'task_name')
    list_filter = ('status', 'date_done')
    search_fields = ('task_id', 'task_name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user_id', 'status', 'total_amount', 'created_at')
    search_fields = ('order_id', 'user_id')
    list_filter = ('status', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'status')
    search_fields = ('order__order_id', 'product__name')
    list_filter = ('status',)