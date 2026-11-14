def check_payment(order, payments):
    '''
    检查订单支付状态
    '''
    if order["order_status"] != "paid":
        return "不在检查范围"

    has_success = False
    for payment in payments:
        if payment["payment_status"] == "success":
            has_success = True

    if payments:
        if has_success:
            return("存在成功支付记录")
        else:
            return("有支付记录但无成功记录")
    elif payments == []:
        return("无支付记录")