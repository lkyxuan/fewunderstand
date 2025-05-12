import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import sys
import os

class SyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件同步工具")
        self.root.geometry("300x200")
        
        # 设置窗口样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10)
        self.style.configure("TLabel", padding=5)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=0, column=0, pady=10)
        
        # 启动按钮
        self.start_button = ttk.Button(main_frame, text="开始同步", command=self.start_sync)
        self.start_button.grid(row=1, column=0, pady=10)
        
        # 停止按钮
        self.stop_button = ttk.Button(main_frame, text="停止同步", command=self.stop_sync, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=0, pady=10)
        
        self.sync_process = None
        self.is_running = False

    def start_sync(self):
        if not self.is_running:
            self.is_running = True
            self.status_label.config(text="正在同步...")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            # 在新线程中启动同步进程
            threading.Thread(target=self.run_sync, daemon=True).start()

    def stop_sync(self):
        if self.is_running and self.sync_process:
            self.sync_process.terminate()
            self.is_running = False
            self.status_label.config(text="已停止")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def run_sync(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, "auto_sync_posts.py")
        
        try:
            self.sync_process = subprocess.Popen([sys.executable, script_path])
            self.sync_process.wait()
        except Exception as e:
            self.status_label.config(text=f"错误: {str(e)}")
        finally:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncApp(root)
    root.mainloop() 