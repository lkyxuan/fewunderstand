#!/usr/bin/env python3
import os
import shutil
import yaml
import datetime
from pathlib import Path
import re

# 配置
SOURCE_DIR = "source_posts"  # 源文章目录
TARGET_DIR = "_posts"        # 目标文章目录

# 标签映射
TAG_MAPPING = {
    "Bitcoin": "比特币",
    "Crypto": "加密货币",
    "Airdrop": "空投",
    "AI": "人工智能",
    "Web3": "Web3",
    "DeFi": "去中心化金融",
    "NFT": "NFT",
    "GameFi": "链游",
    "Layer2": "二层网络",
    "DAO": "DAO",
    "Staking": "质押",
    "Trading": "交易",
    "Research": "研究",
    "Analysis": "分析",
    "News": "新闻",
    "Tutorial": "教程",
    "Guide": "指南",
    "Review": "评测",
    "Interview": "访谈",
    "AMA": "AMA",
}

# 类别映射
CATEGORY_MAPPING = {
    "Bitcoin": "加密货币",
    "Crypto": "加密货币",
    "Airdrop": "空投",
    "AI": "人工智能",
    "Web3": "Web3",
    "DeFi": "去中心化金融",
    "NFT": "NFT",
    "GameFi": "链游",
    "Layer2": "二层网络",
    "DAO": "DAO",
    "Staking": "质押",
    "Trading": "交易",
    "Research": "研究",
    "Analysis": "分析",
    "News": "新闻",
    "Tutorial": "教程",
    "Guide": "指南",
    "Review": "评测",
    "Interview": "访谈",
    "AMA": "AMA",
}

DEFAULT_CATEGORY = "加密货币"

def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None

def format_post_content(content, filename):
    """格式化文章内容"""
    # 提取日期
    date = extract_date_from_filename(filename)
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # 解析原始 front matter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return content
    
    front_matter = yaml.safe_load(parts[1])
    
    # 获取当前时间
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    # 构建新的 front matter
    new_front_matter = {
        'title': front_matter.get('title', ''),
        'date': f"{date} 14:00:00 +0800",
        'categories': DEFAULT_CATEGORY,
        'tags': [],
        'description': front_matter.get('description', ''),
        'updated': f"{date} {current_time}",
        'created': date
    }
    
    # 处理标签
    if 'tags' in front_matter:
        for tag in front_matter['tags']:
            # 移除 # 符号
            clean_tag = tag.replace('#', '')
            # 转换为中文标签
            chinese_tag = TAG_MAPPING.get(clean_tag, clean_tag)
            new_front_matter['tags'].append(chinese_tag)
            
            # 处理类别
            if clean_tag in CATEGORY_MAPPING:
                new_front_matter['categories'] = CATEGORY_MAPPING[clean_tag]
    
    # 构建新的内容
    new_content = f"""---
{yaml.dump(new_front_matter, allow_unicode=True, sort_keys=False)}---
{parts[2]}"""
    
    return new_content

def sync_posts():
    """同步文章"""
    # 确保目标目录存在
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 遍历源目录中的所有文件
    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith('.md'):
            source_path = os.path.join(SOURCE_DIR, filename)
            target_path = os.path.join(TARGET_DIR, filename)
            
            # 读取源文件内容
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 格式化内容
            formatted_content = format_post_content(content, filename)
            
            # 写入目标文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            print(f"已同步: {filename}")

if __name__ == "__main__":
    sync_posts() 