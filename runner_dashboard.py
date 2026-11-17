from flask import Flask, render_template, send_from_directory, redirect, request, url_for
from list_runs import load_runs, reports_dir
import subprocess
import sys
from pathlib import Path
from threading import Lock

app = Flask(__name__)

quick_process = None # 快速测试进程, 默认 None
quick_lock = Lock() # 快速测试进程锁, 防止并发访问, 默认 None


@app.get("/runs") # 获取所有运行记录
def get_runs(): 
    """获取所有运行记录, 返回 JSON 格式"""
    items = []
    for run in load_runs(): # 加载所有运行记录
        items.append({
            "run_id": run["report_dir"].name,
            "mode": run["mode"],
            "finished_at": run["finished_at"],
            "exit_code": run["exit_code"],
        })
    return {"runs": items}

@app.get("/")
def dashboard():
    '''
    显示运行仪表盘
    '''
    with quick_lock:  # 加锁, 防止并发访问 quick_process
        process = quick_process # 获取当前快速测试进程
        run_exit = process.poll() if process is not None else None # 检查进程是否已完成
        running = process is not None and run_exit is None # 检查进程是否仍在运行

    return render_template(
        "runs.html",
        runs=load_runs(),
        running=running,
        run_exit=run_exit,
    )

@app.post("/runs/quick")
def start_quick_run():
    """启动快速测试"""
    global quick_process # 全局变量, 快速测试进程
    with quick_lock: # 加锁, 防止并发访问 quick_process
        if quick_process is None or quick_process.poll() is not None: # 检查进程是否已完成
            quick_process = subprocess.Popen( 
                # 启动快速测试进程, 并设置为全局变量 quick_process, 并在当前目录执行, 并在后台运行
                [sys.executable, "run_tests.py", "quick"],
                cwd=Path(__file__).resolve().parent,
            )

    return redirect(url_for("dashboard"), code=303) # 重定向到仪表盘, 刷新页面

@app.post("/runs/full")
def start_full_run():
    """启动完整测试"""
    global quick_process # 全局变量, 快速测试进程
    with quick_lock: # 加锁, 防止并发访问 quick_process
        if quick_process is None or quick_process.poll() is not None: # 检查进程是否已完成
            quick_process = subprocess.Popen( 
                # 启动完整测试进程, 并设置为全局变量 quick_process, 并在当前目录执行, 并在后台运行
                [sys.executable, "run_tests.py", "full"],
                cwd=Path(__file__).resolve().parent,
            )

    return redirect(url_for("dashboard"), code=303) # 重定向到仪表盘, 刷新页面

@app.get("/reports/<run_id>")
def view_report(run_id):
    """查看测试报告"""
        # 尝试发送报告文件
    return send_from_directory(reports_dir, f"{run_id}/order-api.html")
