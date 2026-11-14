import json
from payment_rules import check_payment

try:
    with open("payment_case.json", encoding="utf-8") as file:
        cases = json.load(file)
except FileNotFoundError:
    print("文件不存在")
except json.JSONDecodeError:
    print("JSON 格式错误")
else:
    for case in cases:
        result = check_payment(case["order"], case["payments"])
        print(case["order"]["order_id"], result)




