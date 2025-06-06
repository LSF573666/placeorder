import requests
import json

# 1. 定义 API 地址和订单数据
API_URL = "http://localhost:8001/api/orders/bulk/"
ORDER_DATA = {
    "user_id": 1,
    "items": [
        {"product_id": 1, "quantity": 666},
        {"product_id": 2, "quantity": 888}
    ]
}

# 2. 发送 POST 请求
response = requests.post(
    API_URL,
    headers={"Content-Type": "application/json"},
    data=json.dumps(ORDER_DATA)
)

# 3. 解析响应
if response.status_code == 201:
    print("✅ 订单提交成功！")
    print(json.dumps(response.json(), indent=2))
else:
    print("❌ 订单提交失败！")
    print(f"状态码: {response.status_code}, 错误: {response.text}")