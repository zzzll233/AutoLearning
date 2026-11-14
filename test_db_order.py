import pytest
import requests
import mysql.connector
from order_queries import get_order
import json
from pathlib import Path
from decimal import Decimal
from getpass import getpass
@pytest.fixture
def qa_training_url():
    return "http://localhost:5051"

@pytest.fixture
def api_session():
    with requests.Session() as session:
        yield session

@pytest.fixture(scope="module") # 该 fixture 作用域为 module，即在每个测试模块执行前执行一次
def db_conn(): # 该 fixture 返回一个数据库连接对象
    '''
    连接数据库并返回连接对象
    '''
    config_path = Path(__file__).with_name("db_config.local.json"
    )
    with config_path.open(encoding="utf-8") as file:
        config = json.load(file)
    with mysql.connector.connect(**config) as connection:
        yield connection

@pytest.mark.parametrize("order_id, expected_order", [
    (1002, {
            "order_id": 1002,
            "order_status": "unpaid",
            "amount": Decimal("50.00"),
        }), 
        (9999, None),])
def test_get_existing_order(db_conn, order_id, expected_order):
    '''
    测试获取存在的订单
    '''
    order = get_order(db_conn, order_id)

    assert order == expected_order
@pytest.mark.parametrize("order_id, expected_status", [
    (1002, 200),
    (9999, 404),
])
def test_order_api_matches_database(db_conn, qa_training_url, api_session, order_id, expected_status):
    '''
    测试订单 API 是否与数据库匹配
    '''
    response = api_session.get(
        f"{qa_training_url}/orders/{order_id}",
        timeout=10,
    )

    api_order = response.json()
    db_order = get_order(db_conn, order_id)

    assert response.status_code == expected_status
    if expected_status == 404:
        assert db_order is None
        assert api_order == {"message": "Order not found"}
        return

    assert db_order is not None
    assert db_order["order_id"] == order_id == api_order["order_id"] 
    assert db_order["order_status"] == api_order["order_status"]
    assert db_order["amount"] == Decimal(api_order["amount"])

@pytest.mark.parametrize(
    "order_id, customer_id, amount, order_status, expected_status",
    [
        (900001, 1, "60.90", "unpaid", 409),
        (900002, 10, "59.90", "unpaid", 400),

    ]
)
def test_create_order_rejected(
    db_conn, qa_training_url, api_session, order_id, customer_id, amount, order_status, expected_status
    ):
    before = get_order(db_conn, order_id)

    if expected_status == 409:
        assert before is not None
        assert before["amount"] == Decimal("59.90")
    else:
        assert before is None
    
    db_conn.rollback()

    payload = {
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "order_status": order_status,
    }

    response = api_session.post(
         f"{qa_training_url}/orders",
         json = payload,
         timeout = 10
        )
    
    assert response.status_code == expected_status
    if expected_status == 400:
        assert response.json()["errno"] == 1452
    after = get_order(db_conn, order_id)
    assert after == before