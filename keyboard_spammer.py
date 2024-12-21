import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import random
import threading
import keyboard
import json
import os
from PIL import Image, ImageTk, ImageFilter  # 需要安装 pillow 库

class ShadowFrame(tk.Frame):
    def __init__(self, parent, color='#FFFFFF', shadow_color='#DDDDDD', *args, **kwargs):
        super().__init__(parent, bg=shadow_color, *args, **kwargs)
        
        # 创建内部框架
        self.inner_frame = tk.Frame(self, bg=color)
        self.inner_frame.pack(padx=3, pady=3, fill="both", expand=True)

class KeyboardSpammer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("键盘轰炸机 v1.0")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # 设置主题色
        self.PRIMARY_COLOR = "#2196F3"  # 蓝色
        self.BG_COLOR = "#F5F5F5"      # 更浅的背景色
        self.TEXT_COLOR = "#333333"     # 深灰文字
        self.GLASS_COLOR = "#FFFFFF"    # 毛玻璃颜色
        
        # 设置透明度和背景
        self.root.attributes('-alpha', 0.97)  # 微调整透明度
        
        # 创建主框架，添加内边距
        self.main_container = tk.Frame(self.root, bg=self.BG_COLOR)
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 控制变量
        self.is_running = False
        self.delay = tk.DoubleVar(value=0.01)
        self.batch_size = tk.IntVar(value=5)
        
        self.load_settings()
        self.create_widgets()
        
    def create_widgets(self):
        # 自定义样式
        style = ttk.Style()
        style.configure('Frosted.TFrame',
                       background=self.GLASS_COLOR)
        
        style.configure('Frosted.TLabel',
                       background=self.GLASS_COLOR,
                       font=('Arial', 10))
        
        # 标题
        title_frame = tk.Frame(self.main_container, bg=self.GLASS_COLOR)
        title_frame.pack(pady=15)
        
        title_label = tk.Label(title_frame,
                             text="键盘轰炸机",
                             font=('Arial', 20, 'bold'),
                             bg=self.GLASS_COLOR,
                             fg=self.PRIMARY_COLOR)
        title_label.pack()
        
        # 主容器
        main_frame = tk.Frame(self.main_container, bg=self.GLASS_COLOR)
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # 设置区域 - 添加阴影效果
        settings_container = ShadowFrame(main_frame, self.GLASS_COLOR)
        settings_container.pack(fill="x", pady=(0, 10))
        
        settings_frame = tk.Frame(settings_container.inner_frame, bg=self.GLASS_COLOR)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        settings_label = tk.Label(settings_frame,
                                text="基本设置",
                                font=('Arial', 12, 'bold'),
                                bg=self.GLASS_COLOR,
                                fg=self.TEXT_COLOR)
        settings_label.pack(anchor='w', pady=(0, 5))
        
        # 延迟设置
        delay_frame = tk.Frame(settings_frame, bg=self.GLASS_COLOR)
        delay_frame.pack(fill="x", pady=5)
        tk.Label(delay_frame,
                text="延迟(秒):",
                font=('Arial', 10),
                bg=self.GLASS_COLOR).pack(side="left", padx=5)
        self.delay_entry = ttk.Entry(delay_frame,
                                   textvariable=self.delay,
                                   width=10)
        self.delay_entry.pack(side="left", padx=5)
        
        # 批量设置
        batch_frame = tk.Frame(settings_frame, bg=self.GLASS_COLOR)
        batch_frame.pack(fill="x", pady=5)
        tk.Label(batch_frame,
                text="批量数量:",
                font=('Arial', 10),
                bg=self.GLASS_COLOR).pack(side="left", padx=5)
        self.batch_entry = ttk.Entry(batch_frame,
                                   textvariable=self.batch_size,
                                   width=10)
        self.batch_entry.pack(side="left", padx=5)
        
        # 锁定设置
        lock_frame = tk.Frame(settings_frame, bg=self.GLASS_COLOR)
        lock_frame.pack(fill="x", pady=5)
        self.lock_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(lock_frame,
                       text="锁定设置",
                       variable=self.lock_var,
                       command=self.toggle_lock).pack(side="left", padx=5)
        
        # 按钮区域 - 添加悬停效果
        button_frame = tk.Frame(main_frame, bg=self.GLASS_COLOR)
        button_frame.pack(fill="x", pady=10)
        
        def on_enter(e, button):
            button.config(bg=self.darken_color(button.cget('bg')))
            
        def on_leave(e, button, original_color):
            button.config(bg=original_color)
        
        self.start_btn = tk.Button(button_frame,
                                 text="开始 (F6)",
                                 command=self.toggle_spam,
                                 width=15,
                                 font=('Arial', 10, 'bold'),
                                 bg=self.PRIMARY_COLOR,
                                 fg='white',
                                 relief='flat',
                                 cursor='hand2')
        self.start_btn.pack(side="left", padx=5)
        self.start_btn.bind('<Enter>', lambda e: on_enter(e, self.start_btn))
        self.start_btn.bind('<Leave>', lambda e: on_leave(e, self.start_btn, self.PRIMARY_COLOR))
        
        save_btn = tk.Button(button_frame,
                           text="保存设置",
                           command=self.save_settings,
                           width=15,
                           font=('Arial', 10),
                           bg='#4CAF50',
                           fg='white',
                           relief='flat',
                           cursor='hand2')
        save_btn.pack(side="right", padx=5)
        save_btn.bind('<Enter>', lambda e: on_enter(e, save_btn))
        save_btn.bind('<Leave>', lambda e: on_leave(e, save_btn, '#4CAF50'))
        
        # 状态显示
        self.status_label = tk.Label(main_frame,
                                   text="状态: 已停止",
                                   font=('Arial', 11, 'bold'),
                                   bg=self.GLASS_COLOR,
                                   fg=self.TEXT_COLOR)
        self.status_label.pack(pady=10)
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.pack(fill="x", pady=10)
        
        # 使用说明区域 - 添加阴影效果
        tips_container = ShadowFrame(main_frame, self.GLASS_COLOR)
        tips_container.pack(fill="both", expand=True, pady=(10, 0))
        
        tips_frame = tk.Frame(tips_container.inner_frame, bg=self.GLASS_COLOR)
        tips_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tips_label = tk.Label(tips_frame,
                            text="使用说明",
                            font=('Arial', 12, 'bold'),
                            bg=self.GLASS_COLOR,
                            fg=self.TEXT_COLOR)
        tips_label.pack(anchor='w', pady=(0, 5))
        
        tips = """
1. 基本操作:
   • 设置延迟时间（秒）和批量发送数量
   • 点击"开始"按钮或按F6开始/停止
   • F7键可以紧急停止
   • 鼠标移到屏幕左上角可紧急停止

2. 高级功能:
   • 锁定设置：防止运行时意外修改参数
   • 保存设置：保存当前设置供下次使用
   
3. 注意事项:
   • 本工具仅供娱乐使用
   • 禁止用于非法用途
   • 使用前请确保光标在正确位置
   • 如违反使用规则后果自负

原创作者: 杨
        """
        tips_text = tk.Text(tips_frame,
                          height=15,
                          width=45,
                          font=('Arial', 9),
                          bg='white',
                          relief='flat',
                          padx=10,
                          pady=10)
        tips_text.pack(padx=5, pady=5)
        tips_text.insert("1.0", tips)
        tips_text.config(state="disabled")

    def save_settings(self):
        settings = {
            'delay': self.delay.get(),
            'batch_size': self.batch_size.get(),
            'lock_settings': self.lock_var.get()
        }
        try:
            with open('spammer_settings.json', 'w') as f:
                json.dump(settings, f)
            messagebox.showinfo("成功", "设置已保存")
        except:
            messagebox.showerror("错误", "保存设置失败")
            
    def load_settings(self):
        try:
            if os.path.exists('spammer_settings.json'):
                with open('spammer_settings.json', 'r') as f:
                    settings = json.load(f)
                self.delay.set(settings.get('delay', 0.01))
                self.batch_size.set(settings.get('batch_size', 5))
                self.lock_var.set(settings.get('lock_settings', False))
                
                # 如果设置是锁定的，应用锁定状态
                if self.lock_var.get():
                    self.toggle_lock()
        except:
            pass
        
    def spam_keyboard(self):
        chars = 'qwertyuiopasdfghjklzxcvbnm'  # 小写字母
        chars += chars.upper()  # 大写字母
        chars += '1234567890'  # 数字
        chars += ' ' * 10  # 空格
        chars += ',.?!;:\'"`~@#$%^&*()-_+=<>[]{}\\|/'  # 标点符号
        chars = list(chars)
        
        print("程序将在3秒后开始运行...")
        for i in range(3, 0, -1):
            self.status_label.config(text=f"状态: 准备中({i})")
            time.sleep(1)
        
        while self.is_running:
            try:
                batch_chars = ''.join(random.choice(chars) for _ in range(self.batch_size.get()))
                keyboard.write(batch_chars)
                time.sleep(self.delay.get())
            except Exception as e:
                print(f"错误: {str(e)}")
                self.is_running = False
                break
    
    def toggle_spam(self, *args):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(text="停止(F6)", bg="#FF4444")
            self.status_label.config(text="状态: 运行中", fg="#FF4444")
            threading.Thread(target=self.spam_keyboard, daemon=True).start()
        else:
            self.is_running = False
            self.start_btn.config(text="开始(F6)", bg=self.PRIMARY_COLOR)
            self.status_label.config(text="状态: 已停止", fg=self.TEXT_COLOR)
    
    def run(self):
        pyautogui.FAILSAFE = True
        keyboard.on_press_key('F6', self.toggle_spam)
        keyboard.on_press_key('F7', lambda _: setattr(self, 'is_running', False))
        self.root.mainloop()

    def toggle_lock(self):
        """切换设置锁定状态"""
        is_locked = self.lock_var.get()
        state = 'disabled' if is_locked else 'normal'
        
        # 锁定/解锁输入框
        self.delay_entry.config(state=state)
        self.batch_entry.config(state=state)
        
        # 更新状态显示，但不覆盖运行状态
        if is_locked and not self.is_running:
            self.status_label.config(text="状态: 设置已锁定")
        elif not is_locked and not self.is_running:
            self.status_label.config(text="状态: 已停止")

    def darken_color(self, color):
        """使颜色变暗一点"""
        # 将颜色转换为RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # 使每个分量变暗
        factor = 0.9
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        # 转回十六进制
        return f'#{r:02x}{g:02x}{b:02x}'

if __name__ == "__main__":
    app = KeyboardSpammer()
    app.run() 
