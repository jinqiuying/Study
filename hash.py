promote = """
===== 记账小程序 =====
1. 添加收入
2. 添加支出
3. 查看记录
4. 查看统计
5. 退出
"""
#请选择: 1;请输入金额: 5000;请输入类型: 工资;请输入备注: 月薪;✓ 添加成功！
#请选择: 4,【财务统计】:总收入: 5000元:总支出: 0元:当前余额: 5000元
print(promote)
bookkeeper = []

# 添加收入
def add_income():
    in_amount = float(input("请输入收入金额："))
    if in_amount < 0:
        print("金额无效，请重新输入")
        return
    in_type = input("请输入收入类型：")
    in_remark = input("请输入收入备注：")
    bookkeeper.append({"in_amount":in_amount, "in_type":in_type, "in_remark":in_remark})
    print("✓添加收入成功")
    return

#添加支出
def add_expenditure():
    out_amount = float(input("请输入支出金额："))
    if out_amount < 0:
        print("金额无效，请重新输入")
        return
    out_type = input("请输入支出类型：")
    out_remark =input("请输入支出备注：")
    bookkeeper.append({"out_amount":out_amount, "out_type":out_type, "out_remark":out_remark})
    print("✓添加支出成功")
    return bookkeeper[-1]

#查看记录
def view_records():
    for record in bookkeeper:
        print(f"收入类型：{record['in_type']}，金额：{record['in_amount']}，备注：{record['in_remark']}")
        print(f"支出类型：{record['out_type']}，金额：{record['out_amount']}，备注：{record['out_remark']}")


#查看统计
def view_statistics():
    total_income = 0
    total_expenditure = 0

    print(f"总收入: {total_income}元, 总支出: {total_expenditure}元, 当前余额: {total_income - total_expenditure}元")


#退出系统
def exit_system():
    print("退出成功")
    exit()


while True:
    number = int(input("请输入数字1-5:"))
    match number:
        case 1:
            add_income()
        case 2:
            add_expenditure()
        case 3:
            view_records()
        case 4:
            view_statistics()
        case 5:
            exit_system()