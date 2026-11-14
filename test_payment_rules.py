import pytest

from payment_rules import check_payment


@pytest.mark.parametrize(
    "order_status, payments, expected",
    [
        (
            "paid",
            [{"payment_status": "failed"}],
            "有支付记录但无成功记录",
        ),
        (
            "paid",
            [],
            "无支付记录",
        ),
        (
            "unpaid",
            [{"payment_status": "failed"}],
            "不在检查范围",
        ),
        (
            "paid",
            [{"payment_status": "failed"}, {"payment_status": "success"}],
            "存在成功支付记录",
        )
    ],
    ids=["only_failed", "no_payment", "not_in_scope", "has_success"],
)
def test_check_payment(order_status, payments, expected):
    order = {"order_id": 1009, "order_status": order_status}
    actual = check_payment(order, payments)
    assert actual == expected

