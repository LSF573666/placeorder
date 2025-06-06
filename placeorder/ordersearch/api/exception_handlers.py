from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging
from placeorder.ordersearch.exceptions import BaseServiceException

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # 调用DRF默认异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        return response
    
    # 处理自定义异常
    if isinstance(exc, BaseServiceException):
        logger.warning(f'Service exception: {str(exc)}')
        return Response(
            {'error': str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 处理其他未捕获异常
    logger.error(f'Unhandled exception: {str(exc)}', exc_info=True)
    return Response(
        {'error': 'Internal server error'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )