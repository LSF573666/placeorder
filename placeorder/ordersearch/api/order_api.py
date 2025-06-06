from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from placeorder.ordersearch.serializers import BulkOrderSerializer
from placeorder.ordersearch.service.order_service import OrderService

class BulkOrderAPI(APIView):
    """
    批量订单创建API
    POST /api/orders/bulk/
    {
        "user_id": 123,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    """
    
    def post(self, request):
        serializer = BulkOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = OrderService.create_bulk_order(
                user_id=serializer.validated_data['user_id'],
                items=serializer.validated_data['items']
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )