# debug_admin.py
import os
import sys
from flask import Flask
from werkzeug.security import check_password_hash

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_admin():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ctf_user:031006@localhost:3306/ctf_platform'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from models import db, User
    
    db.init_app(app)
    
    with app.app_context():
        print("=== 检查数据库中的用户 ===")
        users = User.query.all()
        
        for user in users:
            print(f"\n用户: {user.username}")
            print(f"邮箱: {user.email}")
            print(f"是管理员: {user.is_admin}")
            print(f"密码哈希: {user.password_hash}")
            print(f"创建时间: {user.created_at}")
            
            # 测试常见密码
            test_passwords = ['admin123', 'admin', 'password', '123456', '031006']
            found = False
            for pwd in test_passwords:
                if check_password_hash(user.password_hash, pwd):
                    print(f"✅ 找到密码: '{pwd}'")
                    found = True
                    break
            
            if not found:
                print("❌ 未匹配到常见密码")
            
            print("-" * 50)

if __name__ == '__main__':
    debug_admin()