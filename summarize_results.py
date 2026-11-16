from pathlib import Path
import xml.etree.ElementTree as ET
import argparse # 用于解析命令行参数



# 解析命令行参数, 如果没有指定报告路径, 则使用默认路径
default_report = Path(__file__).parent / "reports" / "order-api.xml" 
# 定义命令行参数解析器, 用于解析命令行参数
parser = argparse.ArgumentParser(description="汇总Pytest测试报告")
# 定义命令行参数, 用于指定测试报告路径, 可选参数, 默认值为默认路径, 类型为 Path
parser.add_argument("report", nargs="?", type=Path, default=default_report)
# 解析命令行参数, 获取报告路径, 如果没有指定报告路径, 则使用默认路径
report_path = parser.parse_args().report # 解析命令行参数，获取报告路径

root = ET.parse(report_path).getroot()
suite = root.find("testsuite")

if suite is None:
    raise ValueError("报告中找不到 testsuite")

print("用例总数", suite.get("tests"))
print("	失败数", suite.get("failures"))
print("	错误数", suite.get("errors"))
print("	跳过数", suite.get("skipped"))
print("	总耗时（秒）", suite.get("time"))

for testcase in suite.findall("testcase"):
    failure = testcase.find("failure")
    if failure is not None:
        print("失败用例", testcase.get("name"))
