import json
from pathlib import Path
from decimal import Decimal, InvalidOperation
import mysql.connector
from flask import Flask, request
from order_queries import get_order, insert_order
from time import perf_counter

app = Flask(__name__) # 创建 Flask 应用实例，__name__ 是当前模块的名称
app.json.ensure_ascii = False

config_path = Path(__file__).with_name("db_config.local.json")
with open(config_path, encoding="utf-8") as file:
    config = json.load(file)

@app.get("/orders/<int:order_id>") # 定义路由，/orders/<order_id> 是动态路由，order_id 是一个整数参数
def read_order(order_id):
    start = perf_counter()
    with mysql.connector.connect(**config) as connection:
        connected = perf_counter()
        order = get_order(connection, order_id)
        queried = perf_counter()
    
    print(
    f"order_id={order_id} "
    f"db_connect_ms={(connected - start) * 1000:.1f} "
    f"query_fetch_ms={(queried - connected) * 1000:.1f}"
)

    if order is None:
        return {"message": "Order not found"}, 404

    return {
        "order_id": order["order_id"],
        "order_status": order["order_status"],
        "amount": str(order["amount"]),
    }

@app.post("/orders") # 定义路由，/orders 是静态路由, 用于创建订单
def create_order():
    data = request.get_json(silent=True) # 获取请求体 JSON 数据，不抛出异常, 如果请求体为空 JSON 字符串, 则返回 None

    if not isinstance(data, dict):
        return {"message": "请求体必须是 JSON 对象"}, 400

    for key in ["order_id", "customer_id", "amount", "order_status"]:
        if key not in data:
            return {"message": f"缺少必填字段 {key}"}, 400
    order_id = data["order_id"]
    
    try:
        amount = Decimal(str(data["amount"]))
    except InvalidOperation:
        return {"message": "金额必须是数字"}, 400
    
    if not amount.is_finite() or amount <= 0: # 检查金额是否为有限数字且大于 0
        return {"message": "amount 必须是大于 0 的有限金额"}, 400

    if amount.as_tuple().exponent < -2: # 检查金额是否小于 0.01
        return {"message": "amount 最多保留两位小数"}, 400

    if amount > Decimal("99999999.99"):
        return {"message": "amount 超出允许范围"}, 400
    
    with mysql.connector.connect(**config) as connection:
        try:
            insert_order(connection, order_id, data["customer_id"], amount, data["order_status"])
            connection.commit()
        except mysql.connector.errors.IntegrityError as exc: # 捕获数据库完整性错误, 例如重复订单 ID
            connection.rollback()
            if exc.errno == 1062:
                return {"message": f"{order_id} 已存在"}, 409
            return {"message": "数据不满足表约束", "errno": exc.errno, "detail": exc.msg}, 400
        except mysql.connector.errors.DatabaseError as exc: # 捕获数据库错误, 例如连接超时
            connection.rollback()
            if exc.errno == 1205:
                return {"message": "数据库繁忙，请稍后重试"}, 503
            raise
    return {"order_id": order_id}, 201 
