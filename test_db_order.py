import pytest
from order_queries import get_order
from decimal import Decimal

@pytest.mark.parametrize("order_id, expected_order", [
    (1002, {
            "order_id": 1002,
            "order_status": "unpaid",
            "amount": Decimal("50.00"),
        }), 
        (9999, None),])
def test_get_existing_order(db_conn, order_id, expected_order):
    '''
    测试获取存在的订单, 检查订单是否存在与预期一致
    '''
    order = get_order(db_conn, order_id)

    assert order == expected_order
@pytest.mark.parametrize("order_id, expected_status", [
    (1002, 200), # 检查订单是否存在与预期一致
    (9999, 404), # 检查订单是否存在与预期一致
])
def test_order_api_matches_database(db_conn, qa_training_url, api_session, order_id, expected_status):
    '''
    测试订单 API 是否与数据库匹配, 检查订单是否存在与预期一致
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
    assert db_order["order_id"] == order_id == api_order["order_id"] # 检查订单ID是否与预期一致
    assert db_order["order_status"] == api_order["order_status"] # 检查订单状态是否与预期一致
    assert db_order["amount"] == Decimal(api_order["amount"]) # 检查订单金额是否与预期一致

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
    '''
    测试创建订单失败的情况, 检查数据库是否未被修改
    '''
    before = get_order(db_conn, order_id)

    # 检查数据库订单状态是否未被修改
    # 检查数据库订单状态是否未被修改
    if expected_status == 409:
        assert before is not None
        assert before["amount"] == Decimal("59.90")
    else:
        assert before is None

    db_conn.rollback() # 回滚数据库事务

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
    
    assert response.status_code == expected_status # 检查响应状态码与预期状态码一致
    if expected_status == 400:
        assert response.json()["errno"] == 1452 # 检查响应错误码为 1452
    after = get_order(db_conn, order_id)
    assert after == before # 检查数据库订单状态未被修改

@pytest.mark.parametrize(
    "amount, expected_message",
    [
        pytest.param("abc", "金额必须是数字", id="non-numeric"),
        pytest.param("NaN","amount 必须是大于 0 的有限金额", id = "not-finite-number" ),
        pytest.param("0", "amount 必须是大于 0 的有限金额", id="zero"),
        pytest.param("59.901", "amount 最多保留两位小数", id="too-many-decimals"),
        pytest.param("100000000.00", "amount 超出允许范围", id="over-limit"),
    ]
)
def test_create_order_rejects_invalid_amount(
    db_conn, qa_training_url, api_session, 
    amount, expected_message):
    '''
    金额校验测试, 测试创建订单时金额是否符合要求
    '''
    order = {
        "order_id": 900003,
        "customer_id": 1,
        "amount": amount,
        "order_status": "unpaid",
    } # 创建订单请求体

    order_id = order["order_id"]
    check_order = get_order(db_conn, order_id) # 检查订单是否存在
    assert check_order is None # 检查订单不存在

    db_conn.rollback() # 回滚数据库事务

    response = api_session.post( # 发送 POST 请求创建订单
        f"{qa_training_url}/orders",
        json = order,
        timeout = 10,
    )

    assert response.status_code == 400 # 检查响应状态码为 400
    assert response.json()["message"] == expected_message # 检查响应消息与预期消息一致
    assert get_order(db_conn, order_id) is None # 检查订单不存在数据库中

def test_create_order_persists(db_conn, qa_training_url, api_session):
    '''
    测试创建订单成功的情况, 检查数据库是否包含新订单
    '''
    order = {
        "order_id": 900004,
        "customer_id": 1,
        "amount": "59.90",
        "order_status": "unpaid",
    } # 创建订单请求体

    order_id = order["order_id"] 
    check_order = get_order(db_conn, order_id) # 检查订单是否存在
    assert check_order is None, f"订单 {order_id} 存在"  # 检查订单存在

    db_conn.rollback() # 回滚数据库事务

    try:
        response = api_session.post(
            f"{qa_training_url}/orders",
            json = order,
            timeout = 10
        )
        assert response.status_code == 201 # 检查响应状态码为 201
        assert response.json()["order_id"] == order_id # 检查响应订单ID与请求订单ID一致

        new_order = get_order(db_conn, order_id) # 检查数据库订单是否存在
        assert new_order is not None, f"订单 {order_id} 不存在"  # 检查订单存在
        assert new_order["order_status"] == order["order_status"] # 检查订单状态是否与预期一致
        assert new_order["amount"] == Decimal(order["amount"]) # 检查订单金额是否与预期一致
    finally:
        with db_conn.cursor() as cursor:
            cursor.execute(f"DELETE FROM orders WHERE order_id = {order_id}")# 删除测试订单
            db_conn.commit() # 提交事务
    
