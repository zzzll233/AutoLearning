import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# 检查环境 → 运行 pytest → 保存本次报告 → 打印摘要。

parser = argparse.ArgumentParser(description="运行订单接口测试")
# 定义命令行参数, 用于指定测试模式, 可选参数, 默认值为默认值, 类型为 str, 可选值为 quik 或 full
parser.add_argument("mode", nargs="?", default="quick", choices=["quick", "full"],
                    help="quick: 快速查单（2 条用例）; full: test_db_order.py 全部用例")  # 快速模式或全量模式
args = parser.parse_args()

targets = {
    "quick": "test_db_order.py::test_order_api_matches_database",
    "full": "test_db_order.py",
}
project_dir = Path(__file__).resolve().parent

check = subprocess.run([sys.executable, "check_environment.py"], 
                        cwd=project_dir) # 检查环境
if check.returncode != 0: # 如果环境检查失败, 则退出程序
    raise SystemExit(check.returncode)

run_time = datetime.now().strftime("%Y%m%d_%H%M%S-%f") # 获取当前时间, 格式为 YYYYMMDD_HHMMSS-ffffff
report_dir = project_dir / "reports" / f"order-api_{run_time}" # 构建报告路径
report_dir.mkdir(parents=True) # 确保报告目录存在, 如果不存在则创建, 递归创建父目录
xml_report = report_dir / "order-api.xml" # 构建 XML 报告路径
html_report = report_dir / "order-api.html" # 构建 HTML 报告路径

command = [sys.executable, "-m", "pytest", "-v", targets[args.mode],
           f"--junitxml={xml_report}", # 生成 XML 报告
           f"--html={html_report}", # 生成 HTML 报告
           "--self-contained-html"] # 确保 HTML 报告自包含, 不依赖外部资源, 如 CSS, JS 等, 直接在 HTML 中嵌入

result = subprocess.run(command, cwd=project_dir) # 运行 pytest 测试, 并获取测试结果

if xml_report.is_file():
    test_results = subprocess.run([sys.executable, "summarize_results.py", str(xml_report)], 
                                cwd=project_dir)
    if test_results.returncode != 0:
        print("报告摘要生成失败")

raise SystemExit(result.returncode)



