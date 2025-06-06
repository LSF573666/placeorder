from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ordersearch.models import Order
from ordersearch.tasks import process_order_async

class AsyncOrderAPI(APIView):
    def post(self, request):
        user_id = request.data.get('user_id', 1) 
        
        # 创建订单
        order = Order.objects.create(
            user_id=user_id,
            status='pending',
            total_amount=0
        )
        
        # 异步处理订单
        task = process_order_async.delay(order.id)
        
        # 返回响应
        return Response({
            "order_id": order.id,
            "task_id": task.id,
            "message": "Order is being processed asynchronously"
        }, status=status.HTTP_202_ACCEPTED)