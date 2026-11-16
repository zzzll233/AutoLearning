import json
from pathlib import Path

reports_dir = Path(__file__).resolve().parent / "reports"

def load_runs():
    """加载所有运行记录, 返回运行记录列表"""
    runs = []
    for info_path in reports_dir.glob("*/run.json"):
        with info_path.open(encoding="utf-8") as file:
            run = json.load(file)
        run["report_dir"] = info_path.parent
        runs.append(run)

    runs.sort(key=lambda run: run["finished_at"], reverse=True)
    return runs

if __name__ == "__main__":
    for run in load_runs(): # 加载所有运行记录
        status = "通过" if run["exit_code"] == 0 else "未通过"
        print(run["finished_at"], run["mode"], status)

    # 你来补这里。html_report 有值时，打印 HTML 报告的完整路径。
    if run["html_report"] is not None:
        print(f"HTML 报告: {run['report_dir'] / run['html_report']}")