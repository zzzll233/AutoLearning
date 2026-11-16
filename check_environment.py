import argparse
from qa_settings import QA_BASE_URL
import requests

parser = argparse.ArgumentParser() 
# 定义命令行参数, 用于指定基础URL, 可选参数, 默认值为默认值, 类型为 str
parser.add_argument("base_url", nargs="?", default=QA_BASE_URL)
args = parser.parse_args() # 解析命令行参数, 获取基础URL, 如果没有指定基础URL, 则使用默认值

url = f"{args.base_url.rstrip('/')}/orders/1002" # 构建订单接口URL

try:
    response = requests.get(url, timeout=3)
except requests.exceptions.RequestException as exc:
    print(f"订单接口请求失败 {exc}")
    raise SystemExit(1) # 抛出异常, 退出程序

if response.status_code == 200:
    print("环境检查通过")
else:
    print(f"环境检查失败, 状态码 {response.status_code}")
    raise SystemExit(1)
# 你来补这里。
# HTTP 200 时打印「环境检查通过」。
# 其他状态码打印实际状态码，再用 raise SystemExit(1) 退出。