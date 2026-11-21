import json
import os
from datetime import datetime
import FreeSimpleGUI as sg

DATA_FILE = 'data.txt'

# 仅在数据文件不存在时写入初始数据，避免每次启动覆盖用户已保存的账目
if not os.path.exists(DATA_FILE):
    d = '[{"日期":"2022/05/07 14:20:21", "分类":"收入", "金额":2000, "项目":"生活费"}]'
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        f.write(d)

def readData():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError):
        return []                           # 文件缺失或损坏时返回空列表，避免崩溃
    
def writeData(dataList):
    jsonData = json.dumps(dataList, ensure_ascii=False)
    with open('data.txt', 'w', encoding='utf-8') as f:
        f.write(jsonData)
        sg.popup('保存成功')        # 写入数据并弹出提示框

def showData():
    data = readData()
    rows = []
    for d in data:
        if d["分类"] == "收入":
            row = [d["日期"], d["分类"], d["金额"], d["项目"]]
        else:
            row = [d["日期"], d["分类"], d["金额"]*-1, d["项目"]]
        rows.append(row)
    return rows

def sumin():
    total = 0
    for d in readData():
        if d["分类"] == "收入":
            total += d["金额"]
    return total

def sumout():
    total = 0
    for d in readData():
        if d["分类"] == "支出":
            total += d["金额"]
    return total

def addData(content,amount,cla):
    data = readData()
    new_entry = {
        "日期": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "分类": cla,
        "金额": amount,
        "项目": content
    }
    data.append(new_entry)
    writeData(data)

def deleteData(indices):
    # 删除表格中选中的账目，indices 为行号元组（与数据列表下标一一对应），返回删除条数
    data = readData()
    left = [d for i, d in enumerate(data) if i not in indices]
    deleted = len(data) - len(left)
    writeData(left)
    sg.popup(f"已删除 {deleted} 条账单")
    return deleted

def build_layout():
    rows = showData()
    layout = [
        [sg.T("账目清单：")],
        [sg.Table(rows,headings=["日期","分类","金额","项目"],
                  key = "-show-",
                  justification = "c",
                  auto_size_columns = False,
                  def_col_width = 15,
                  enable_events = True,               # 允许选中行，右键删除时能拿到选中行号
                  right_click_menu = ["", ["删除"]],  # 右键弹出“删除”菜单
                  )],
        [sg.T("", key="-sum-", enable_events=False)],
        [sg.T("请输入账单项目："), sg.In(key="-content-")],
        [sg.T("请输入账单金额："), sg.In(key="-amount-")],
        [sg.T("请输入账单分类：")]+[sg.Radio(i, group_id="cla", key=i, default=(i == "收入")) for i in ["收入", "支出"]],
        [sg.Button("添加"), sg.Button("退出")]
    ]
    return layout


def refresh(window):
    # 刷新表格与汇总信息
    window["-show-"].update(showData())
    window["-sum-"].update(
        f"总收入：{sumin()}元，总支出：{sumout()}元，结余：{sumin()-sumout()}元")


def main():
    layout = build_layout()
    window = sg.Window("记账本", layout, size=(600, 400), finalize=True)
    refresh(window)
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED or event == "退出":
            break
        elif event == "添加":
            content = values["-content-"]
            try:
                amount = float(values["-amount-"])
            except (ValueError, TypeError):
                sg.popup_error("金额必须为数字，请重新输入")
                continue
            cla = "收入" if values["收入"] else "支出"
            addData(content, amount, cla)
            refresh(window)
        elif event == "删除":                           # 右键菜单触发
            rows = values["-show-"]
            if not rows:
                sg.popup_error("请先在表格中选中要删除的账单，再右键选择删除")
            else:
                deleteData(rows)
                refresh(window)
    window.close()


if __name__ == "__main__":
    main()