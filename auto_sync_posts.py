import os
import shutil
import time
import schedule
import re
import subprocess
from datetime import datetime

# 配置：请填写你实际的源文件夹路径（可以是绝对路径或相对路径）
SOURCE_DIRS = [
    os.path.expanduser("~/Library/CloudStorage/OneDrive-个人/endless/Clippings"),    # Clippings 目录
    os.path.expanduser("~/Library/CloudStorage/OneDrive-个人/endless/AI_research"),  # AI 研究笔记目录
    os.path.expanduser("~/Library/CloudStorage/OneDrive-个人/endless/Twitter"),      # Twitter 笔记目录
]
TARGET_DIR = "_posts"
GIT_REPO_URL = "https://github.com/lkyxuan/fewunderstand.git"  # GitHub仓库URL

def git_init():
    """初始化Git仓库（如果尚未初始化）"""
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "remote", "add", "origin", GIT_REPO_URL], check=True)

def git_commit_and_push():
    """提交更改并推送到GitHub"""
    try:
        # 添加所有更改
        subprocess.run(["git", "add", "."], check=True)
        
        # 提交更改
        commit_message = f"自动同步更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # 推送到GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"Git提交成功: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Git操作失败: {str(e)}")

def normalize_filename(filename):
    # 替换空格为-，只保留字母、数字、-、_和.
    name, ext = os.path.splitext(filename)
    name = re.sub(r'[^A-Za-z0-9\-_\.]+', '-', name)
    return f"{name}{ext}"

def sync_and_rename():
    os.makedirs(TARGET_DIR, exist_ok=True)
    for src_dir in SOURCE_DIRS:
        if not os.path.exists(src_dir):
            print(f"源文件夹不存在: {src_dir}")
            continue
        for filename in os.listdir(src_dir):
            if filename.endswith('.md'):
                src_path = os.path.join(src_dir, filename)
                new_filename = normalize_filename(filename)
                dst_path = os.path.join(TARGET_DIR, new_filename)
                shutil.copy2(src_path, dst_path)
                print(f"已复制并重命名: {src_path} -> {dst_path}")

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