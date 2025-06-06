class BaseServiceException(Exception):
    """服务层异常基类"""
    default_message = 'Service error'
    
    def __init__(self, message=None):
        self.message = message or self.default_message
        super().__init__(self.message)

class InsufficientStockException(BaseServiceException):
    default_message = 'Insufficient stock'

class ProductNotAvailableException(BaseServiceException):
    default_message = 'Product not available'

class InvalidOrderException(BaseServiceException):
    default_message = 'Invalid order data'

class CacheException(BaseServiceException):
    default_message = 'Cache operation failed'