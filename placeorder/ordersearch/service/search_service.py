from django.db.models import Q
from django.core.cache import cache

from placeorder.ordersearch.models import Product
# from .models import Product

class SearchService:
    
    @classmethod
    def search_products(cls, query, limit=20, use_cache=True):
        """
        商品搜索
        :param query: 搜索关键词
        :param limit: 返回结果数量
        :param use_cache: 是否使用缓存
        :return: 商品列表
        """
        if not query or not query.strip():
            return []
        
        query = query.strip().lower()
        cache_key = f'search:keywords:{query}'
        
        # 尝试从缓存获取
        if use_cache:
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
        
        # 执行搜索
        results = cls._perform_search(query, limit)
        
        # 更新缓存
        if use_cache:
            try:
                cache.set(cache_key, results, timeout=60*30)  # 缓存30分钟
            except Exception as e:
                # 缓存设置失败不影响主流程
                pass
        
        return results
    
    @classmethod
    def _perform_search(cls, query, limit):
        """实际执行搜索逻辑"""
        # 使用PostgreSQL的全文搜索
        products = Product.objects.filter(
            Q(search_vector=query) | 
            Q(name__icontains=query),
            is_active=True
        ).select_related(None).only(
            'id', 'name', 'price'
        )[:limit]
        
        return list(products)
    
    @classmethod
    def update_product_search_index(cls, product_id):
        """
        更新单个商品的搜索索引
        :param product_id: 商品ID
        """
        from django.db import connection
        from django.contrib.postgres.search import SearchVector
        
        # 更新数据库中的搜索向量
        Product.objects.filter(id=product_id).update(
            search_vector=SearchVector('name', 'description')
        )
        
        # 清除相关缓存
        cls._clear_product_cache(product_id)
    
    @classmethod
    def _clear_product_cache(cls, product_id):
        """清除商品相关缓存"""
        cache.delete(f'product:detail:{product_id}')