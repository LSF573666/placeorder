import uuid
from django.db import transaction
from django.core.cache import cache
from django.db.utils import IntegrityError

from placeorder.ordersearch import models
from placeorder.ordersearch.exceptions import InsufficientStockException, ProductNotAvailableException
from placeorder.ordersearch.models import Order, OrderItem, Product

class OrderService:
    
    @classmethod
    def create_bulk_order(cls, user_id, items):
        order_id = uuid.uuid4().hex
        success_items = []
        failed_items = []
        
        # 预检查商品可用性
        products = cls._precheck_products(items)
        
        # 创建订单主记录
        order = Order.objects.create(
            order_id=order_id,
            user_id=user_id,
            status='processing'
        )
        
        # 处理每个订单项
        for item in items:
            product_id = item['product_id']
            quantity = item['quantity']
            product = products.get(product_id)
            
            if not product:
                failed_items.append({
                    'product_id': product_id,
                    'error': 'Product not found'
                })
                continue
                
            try:
                order_item = cls._process_order_item(order, product, quantity)
                success_items.append({
                    'product_id': product_id,
                    'quantity': quantity,
                    'item_id': order_item.id
                })
            except (InsufficientStockException, ProductNotAvailableException) as e:
                failed_items.append({
                    'product_id': product_id,
                    'error': str(e)
                })
            except Exception as e:
                failed_items.append({
                    'product_id': product_id,
                    'error': f'System error: {str(e)}'
                })
        
        # 更新订单总金额
        cls._update_order_total(order)
        
        return {
            'order_id': order_id,
            'success_items': success_items,
            'failed_items': failed_items
        }
    
    @classmethod
    def _precheck_products(cls, items):
        """预检查商品是否存在和可用"""
        product_ids = [item['product_id'] for item in items]
        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True
        ).in_bulk()
        return products
    
    @classmethod
    def _process_order_item(cls, order, product, quantity):
        """
        处理单个订单项，包含库存扣减
        使用分布式锁+乐观锁确保并发安全
        """
        # 获取分布式锁
        lock_key = f'lock:product:{product.id}'
        with cache.lock(lock_key, timeout=10, blocking_timeout=5):
            # 检查库存是否充足
            if product.stock < quantity:
                raise InsufficientStockException(
                    f'Insufficient stock for product {product.id}. '
                    f'Available: {product.stock}, Requested: {quantity}'
                )
            
            # 创建订单项
            try:
                with transaction.atomic():
                    # 使用乐观锁扣减库存
                    updated = Product.objects.filter(
                        id=product.id,
                        stock__gte=quantity
                    ).update(
                        stock=models.F('stock') - quantity
                    )
                    
                    if not updated:
                        raise InsufficientStockException(
                            f'Stock update failed for product {product.id}'
                        )
                    
                    # 创建订单项
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        status='completed'
                    )
                    
                    # 更新缓存库存
                    cache_key = f'product:stock:{product.id}'
                    cache.decr(cache_key, quantity)
                    
                    return order_item
                    
            except IntegrityError as e:
                raise Exception(f'Failed to create order item: {str(e)}')
    
    @classmethod
    def _update_order_total(cls, order):
        """更新订单总金额"""
        total = order.items.aggregate(
            total=models.Sum(models.F('quantity') * models.F('price'))
        )['total'] or 0
        
        order.total_amount = total
        order.save()