#!/usr/bin/env python3
"""
数据库初始化脚本
在首次部署时运行此脚本创建数据库和表
"""

import os
import sys
from flask import Flask
from models import db, init_db

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置
    from config import get_config
    app.config.from_object(get_config())
    
    return app

def main():
    """主函数"""
    print("正在初始化CTF平台数据库...")
    
    # 创建应用实例
    app = create_app()
    
    # 初始化数据库
    with app.app_context():
        init_db(app)
        print("数据库初始化完成！")
        
        # 显示创建的表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"创建的表: {', '.join(tables)}")
        
        # 显示默认分类
        from models import Category, User
        categories = Category.query.all()
        print(f"默认分类: {[cat.name for cat in categories]}")
        
        # 显示管理员用户
        admin_users = User.query.filter_by(is_admin=True).all()
        print(f"管理员用户: {[user.username for user in admin_users]}")

if __name__ == '__main__':
    main()