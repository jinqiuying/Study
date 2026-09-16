promote = """
===== 记账小程序 =====
1. 添加收入
2. 添加支出
3. 查看记录
4. 查看统计
5. 退出
"""
# 请选择: 1;请输入金额: 5000;请输入类型: 工资;请输入备注: 月薪;✓ 添加成功！
# 请选择: 4,【财务统计】:总收入: 5000元:总支出: 0元:当前余额: 5000元
print(promote)


class Bookkeeper:
    def __init__(self):
        self.bookkeeper = []

    # 添加记录
    def add_records(self, category):
        label = "收入" if category == "income" else "支出"
        try:
            amount = float(input(f"请输入{label}金额："))
            if amount < 0:
                print("金额无效，请重新输入")
                return
        except Exception as e:
            print(f"发生错误: {e}")
            print("金额无效，请重新输入")
            return
        type_ = input(f"请输入{label}类型：")
        remark = input(f"请输入{label}备注：")
        self.bookkeeper.append({"category": category, "amount": amount, "type": type_, "remark": remark})
        print(f"✓添加{label}成功")

    def view_records(self):
        if not self.bookkeeper:
            print("没有记录")
            return
        for record in self.bookkeeper:
            label = "收入" if record["category"] == "income" else "支出"
            print(f"{label}类型：{record['type']}，金额：{record['amount']}，备注：{record['remark']}")

    def view_statistics(self):
        total_income = 0
        total_expenditure = 0
        for record in self.bookkeeper:
            if record["category"] == "income":
                total_income += record["amount"]
            else:
                total_expenditure += record["amount"]
        print(
            f"总收入: {total_income}元, 总支出: {total_expenditure}元, 当前余额: {total_income - total_expenditure}元")

    # 退出系统
    def exit_system(self):
        print("退出系统")
        exit()


bookkeeper_app = Bookkeeper()

while True:
    try:
        number = int(input("请输入数字1-5:"))
        if number < 1 or number > 5:
            print("无效的输入，请重新输入")
            continue
    except Exception as e:
        print(f"发生错误: {e}")
        print("无效的输入，请重新输入")
        continue
    match number:
        case 1:
            bookkeeper_app.add_records("income")
        case 2:
            bookkeeper_app.add_records("expenditure")
        case 3:
            bookkeeper_app.view_records()
        case 4:
            bookkeeper_app.view_statistics()
        case 5:
            bookkeeper_app.exit_system()
