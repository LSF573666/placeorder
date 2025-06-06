from celery import shared_task
from celery.utils.log import get_task_logger
from ordersearch.models import Order

logger = get_task_logger(__name__)

@shared_task(bind=True)
def process_order_async(self, order_id):
    """异步处理订单"""
    try:
        order = Order.objects.get(id=order_id)
        logger.info(f"Processing order {order_id}...")
        # 模拟耗时操作
        import time
        time.sleep(5)
        order.status = 'completed'
        order.save()
        return {"status": "success", "order_id": order_id}
    except Exception as e:
        logger.error(f"Failed to process order {order_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)  # 失败后自动重试