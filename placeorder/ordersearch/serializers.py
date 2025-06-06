from rest_framework import serializers

class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

class BulkOrderSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)
    items = serializers.ListField(
        child=OrderItemSerializer(),
        min_length=1
    )

    def validate_items(self, value):
        """验证items列表不为空"""
        if not value:
            raise serializers.ValidationError("Items list cannot be empty")
        return value