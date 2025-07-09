import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import sqlite3
import os

def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(val):
    return datetime.fromisoformat(val)

class WaterReminderApp:
    def __init__(self, enable_timer=True):
        self.root = None
        self.countdown = 30  # 30秒倒计时
        self.is_showing = False
        self.timer = None
        self.REMINDER_INTERVAL = 3600  # 1小时的间隔（秒）
        self.time_label = None  # 添加时间标签属性
        self.enable_timer = enable_timer  # 是否启用定时器
        
        # 创建主窗口（隐藏）
        self.main_window = tk.Tk()
        self.main_window.withdraw()  # 隐藏主窗口
        
        # 注册 datetime 适配器
        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("datetime", convert_datetime)
        
        # 初始化数据库
        self.init_database()

    def init_database(self):
        # 确保数据库目录存在
        if not os.path.exists('data'):
            os.makedirs('data')
            
        # 连接数据库并创建表
        with sqlite3.connect('data/water_records.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS water_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp datetime NOT NULL,
                    amount INTEGER NOT NULL
                )
            ''')
            conn.commit()

    def get_today_water_stats(self):
        try:
            with sqlite3.connect('data/water_records.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                # 获取今天零点的时间
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                cursor.execute(
                    'SELECT COUNT(*) as count, SUM(amount) as total FROM water_records WHERE timestamp >= ?',
                    (today,)
                )
                count, total = cursor.fetchone()
                return count or 0, total or 0
        except Exception as e:
            messagebox.showerror("错误", f"获取统计数据失败: {str(e)}")
            return 0, 0

    def save_water_record(self, amount):
        try:
            with sqlite3.connect('data/water_records.db', detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO water_records (timestamp, amount) VALUES (?, ?)',
                    (datetime.now(), amount)
                )
                conn.commit()
            # messagebox.showinfo("成功", "已记录本次喝水量！")
            self.on_window_close()
        except Exception as e:
            messagebox.showerror("错误", f"保存记录失败: {str(e)}")

    def create_reminder_window(self):
        self.is_showing = True
        self.root = tk.Toplevel(self.main_window)
        self.root.attributes('-fullscreen', True)
        self.root.title("喝水提醒")
        
        # 设置窗口在最顶层
        self.root.lift()
        self.root.attributes('-topmost', True)

        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')

        # 显示今日喝水统计
        count, total = self.get_today_water_stats()
        stats_label = ttk.Label(
            main_frame,
            text=f"今日已喝水 {count} 次，共 {total} 毫升",
            font=('微软雅黑', 20),
            justify='center',
            anchor='center'
        )
        stats_label.pack(pady=10, fill='x')

        # 显示大字提醒
        reminder_label = ttk.Label(
            main_frame,
            text="该喝水啦！",
            font=('微软雅黑', 48),
            justify='center',
            anchor='center'
        )
        reminder_label.pack(pady=20, fill='x')

        # 显示当前时间
        self.time_label = ttk.Label(
            main_frame,
            text=f"当前时间: {datetime.now().strftime('%H:%M:%S')}",
            font=('微软雅黑', 24),
            justify='center',
            anchor='center'
        )
        self.time_label.pack(pady=10, fill='x')

        # 倒计时标签
        self.countdown_label = ttk.Label(
            main_frame,
            text=f"{self.countdown} 秒后可关闭",
            font=('微软雅黑', 20),
            justify='center',
            anchor='center'
        )
        self.countdown_label.pack(pady=10, fill='x')

        # 开始倒计时和时间更新
        self.update_countdown()
        
        # 窗口关闭时的回调
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def update_countdown(self):
        if self.countdown > 0:
            # 更新倒计时
            self.countdown_label.config(text=f"{self.countdown} 秒后可关闭")
            # 更新当前时间
            self.time_label.config(text=f"当前时间: {datetime.now().strftime('%H:%M:%S')}")
            self.countdown -= 1
            self.root.after(1000, self.update_countdown)
        else:
            # 清除倒计时文本
            self.countdown_label.config(text="")
            # 显示喝水量输入界面
            self.create_water_input()

    def create_water_input(self):
        # 创建输入框框架
        input_frame = ttk.Frame(self.root)
        input_frame.place(relx=0.5, rely=0.7, anchor='center')

        # 标签
        ttk.Label(
            input_frame,
            text="请输入喝水量(ml):",
            font=('微软雅黑', 16),
            justify='center',
            anchor='center'
        ).pack(side='left', padx=5)

        # 输入框
        water_amount = ttk.Entry(
            input_frame,
            font=('微软雅黑', 16),
            width=10,
            justify='center'
        )
        water_amount.pack(side='left', padx=5)

        # 确认按钮
        def on_confirm():
            try:
                amount = int(water_amount.get())
                if amount <= 0:
                    messagebox.showwarning("警告", "请输入大于0的数值！")
                    return
                self.save_water_record(amount)
            except ValueError:
                messagebox.showwarning("警告", "请输入有效的数字！")

        ttk.Button(
            input_frame,
            text="记录",
            command=on_confirm
        ).pack(side='left', padx=5)

    def schedule_next_reminder(self):
        self.countdown = 30
        self.timer = threading.Timer(self.REMINDER_INTERVAL, self.show_reminder)
        self.timer.daemon = True
        self.timer.start()

    def show_reminder(self):
        if not self.is_showing:
            self.create_reminder_window()

    def start(self):
        # 启动第一次提醒
        self.show_reminder()
        # 启动主循环
        self.main_window.mainloop()

    def on_window_close(self):
        if self.countdown <= 0:
            self.is_showing = False
            self.root.destroy()  # 只关闭提醒窗口
            if self.enable_timer:
                self.schedule_next_reminder()
            else:
                self.main_window.quit()  # 如果不启用定时器，直接退出程序

if __name__ == "__main__":
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='喝水提醒程序')
    parser.add_argument('--no-timer', action='store_true', 
                      help='禁用定时器（仅显示一次提醒）')
    args = parser.parse_args()
    
    # 根据命令行参数决定是否启用定时器
    app = WaterReminderApp(enable_timer=not args.no_timer)
    app.start() 