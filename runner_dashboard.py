from flask import Flask, render_template
from list_runs import load_runs

app = Flask(__name__)

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
    return render_template("runs.html", runs=load_runs())