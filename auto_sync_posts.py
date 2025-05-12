import os
import shutil
import time
import schedule
import re
import subprocess
import json
from datetime import datetime

# 配置：请填写你实际的源文件夹路径（可以是绝对路径或相对路径）
SOURCE_DIRS = [
    os.path.expanduser("~/Library/CloudStorage/OneDrive-个人/endless/Clippings"),    # Clippings 目录
    os.path.expanduser("~/Library/CloudStorage/OneDrive-个人/endless/AI_research"),  # AI 研究笔记目录
    os.path.expanduser("~/Library/CloudStorage/OneDrive-个人/endless/Twitter"),      # Twitter 笔记目录
]
TARGET_DIR = "_posts"
GIT_REPO_URL = "https://github.com/lkyxuan/fewunderstand.git"  # GitHub仓库URL
SYNC_RECORD_FILE = "sync_record.json"  # 同步记录文件

def load_last_sync_time():
    """加载上次同步时间"""
    if os.path.exists(SYNC_RECORD_FILE):
        try:
            with open(SYNC_RECORD_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('last_sync_time', 0)
        except Exception as e:
            print(f"读取同步记录失败: {e}")
    return 0

def save_last_sync_time(sync_time):
    """保存同步时间"""
    try:
        with open(SYNC_RECORD_FILE, 'w', encoding='utf-8') as f:
            json.dump({'last_sync_time': sync_time}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存同步记录失败: {e}")

def git_init():
    """初始化Git仓库（如果尚未初始化）"""
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "remote", "add", "origin", GIT_REPO_URL], check=True)

def git_commit_and_push():
    """提交更改并推送到GitHub"""
    try:
        # 添加 _posts 目录和 sync_record.json 的更改
        subprocess.run(["git", "add", "_posts/", "sync_record.json"], check=True)
        
        # 检查是否有更改需要提交
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if not result.stdout.strip():
            print("没有文件需要提交")
            return
        
        # 提交更改
        commit_message = f"自动同步更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # 推送到GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"Git提交成功: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {str(e)}")

def normalize_filename(filename):
    """规范化文件名：将空格替换为连字符，保留中文字符"""
    return filename.replace(' ', '-')

def sync_and_rename():
    os.makedirs(TARGET_DIR, exist_ok=True)
    last_sync_time = load_last_sync_time()
    print(f"上次同步时间: {datetime.fromtimestamp(last_sync_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    for src_dir in SOURCE_DIRS:
        if not os.path.exists(src_dir):
            print(f"源文件夹不存在: {src_dir}")
            continue
        for filename in os.listdir(src_dir):
            if filename.endswith('.md'):
                src_path = os.path.join(src_dir, filename)
                src_mtime = os.path.getmtime(src_path)
                
                # 如果源文件比上次同步时间新，则需要同步
                if src_mtime > last_sync_time:
                    new_filename = normalize_filename(filename)
                    dst_path = os.path.join(TARGET_DIR, new_filename)
                    shutil.copy2(src_path, dst_path)
                    print(f"已复制并重命名: {src_path} -> {dst_path}")
    
    # 更新同步时间
    save_last_sync_time(time.time())

def job():
    print(f"开始同步 - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    sync_and_rename()
    git_commit_and_push()
    print(f"同步完成 - {time.strftime('%Y-%m-%d %H:%M:%S')}")

# 初始化Git仓库
git_init()

# 每10分钟执行一次
schedule.every(10).minutes.do(job)

# 启动时立即执行一次
job()

while True:
    schedule.run_pending()
    time.sleep(60) 