from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from placeorder.ordersearch.service.search_service import SearchService

class ProductSearchAPI(APIView):
    """
    商品搜索API
    GET /api/products/search/?q=keyword
    """
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            products = SearchService.search_products(query)
            return Response({
                'query': query,
                'results': products
            })
        except Exception as e:
            return Response(
                {'error': 'Search failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )