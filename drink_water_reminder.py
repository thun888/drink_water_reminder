import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading

class WaterReminderApp:
    def __init__(self):
        self.root = None
        self.countdown = 30  # 30秒倒计时
        self.is_showing = False
        self.timer = None
        self.REMINDER_INTERVAL = 3600  # 1小时的间隔（秒）

    def create_reminder_window(self):
        self.is_showing = True
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.title("喝水提醒")
        
        # 设置窗口在最顶层
        self.root.lift()
        self.root.attributes('-topmost', True)

        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.place(relx=0.5, rely=0.5, anchor='center')

        # 显示大字提醒
        reminder_label = ttk.Label(
            main_frame,
            text="该喝水啦！",
            font=('微软雅黑', 48)
        )
        reminder_label.pack(pady=20)

        # 显示当前时间
        time_label = ttk.Label(
            main_frame,
            text=f"当前时间: {datetime.now().strftime('%H:%M:%S')}",
            font=('微软雅黑', 24)
        )
        time_label.pack(pady=10)

        # 倒计时标签
        self.countdown_label = ttk.Label(
            main_frame,
            text=f"{self.countdown} 秒后可关闭",
            font=('微软雅黑', 20)
        )
        self.countdown_label.pack(pady=10)

        # 开始倒计时
        self.update_countdown()
        
        # 窗口关闭时的回调
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        self.root.mainloop()

    def update_countdown(self):
        if self.countdown > 0:
            self.countdown_label.config(text=f"{self.countdown} 秒后可关闭")
            self.countdown -= 1
            self.root.after(1000, self.update_countdown)
        else:
            close_button = ttk.Button(
                self.root,
                text="关闭提醒",
                command=self.on_window_close
            )
            close_button.place(relx=0.5, rely=0.7, anchor='center')

    def on_window_close(self):
        if self.countdown <= 0:
            self.is_showing = False
            self.root.destroy()
            self.schedule_next_reminder()

    def schedule_next_reminder(self):
        self.countdown = 30
        self.timer = threading.Timer(self.REMINDER_INTERVAL, self.show_reminder)
        self.timer.daemon = True
        self.timer.start()

    def show_reminder(self):
        if not self.is_showing:
            self.create_reminder_window()

    def start(self):
        self.show_reminder()

if __name__ == "__main__":
    app = WaterReminderApp()
    app.start() 