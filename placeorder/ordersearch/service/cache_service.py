from django.core.cache import cache
import logging
from placeorder.ordersearch.models import Product

logger = logging.getLogger(__name__)

class CacheService:
    
    @classmethod
    def get_product_detail(cls, product_id, use_cache=True):
        """获取商品详情，带缓存"""
        cache_key = f'product:detail:{product_id}'
        
        if use_cache:
            try:
                cached_data = cache.get(cache_key)
                if cached_data is not None:
                    return cached_data
            except Exception as e:
                logger.warning(f'Cache access failed: {str(e)}', exc_info=True)
                # 缓存访问失败，降级到直接查询数据库
        
        # 从数据库获取
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'stock': product.stock
            }
            
            # 回填缓存
            if use_cache:
                try:
                    cache.set(cache_key, data, timeout=60*60)  # 缓存1小时
                except Exception as e:
                    logger.warning(f'Cache set failed: {str(e)}', exc_info=True)
            
            return data
        except Product.DoesNotExist:
            return None
    
    @classmethod
    def update_product_cache(cls, product_id):
        """更新商品缓存"""
        cache_key = f'product:detail:{product_id}'
        stock_key = f'product:stock:{product_id}'
        
        try:
            product = Product.objects.get(id=product_id)
            
            # 更新详情缓存
            detail_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'stock': product.stock
            }
            cache.set(cache_key, detail_data, timeout=60*60)
            
            # 更新库存缓存
            cache.set(stock_key, product.stock, timeout=60*60)
            
        except Product.DoesNotExist:
            # 商品不存在，清除缓存
            cache.delete(cache_key)
            cache.delete(stock_key)
        except Exception as e:
            logger.error(f'Failed to update product cache: {str(e)}', exc_info=True)