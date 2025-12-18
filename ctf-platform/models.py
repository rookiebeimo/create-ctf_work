from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户模型"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    created_challenges = db.relationship('Challenge', backref='creator', lazy='dynamic', foreign_keys='Challenge.creator_id')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_solved_challenges(self):
        """获取用户解决的题目"""
        from sqlalchemy import distinct
        solved_challenge_ids = db.session.query(distinct(Submission.challenge_id)).filter(
            Submission.user_id == self.id,
            Submission.is_correct == True
        ).all()
        return [id[0] for id in solved_challenge_ids]
    
    def to_dict(self):
        """转换为字典（用于API响应）"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """题目分类模型"""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    challenges = db.relationship('Challenge', backref='category', lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Challenge(db.Model):
    """题目模型"""
    
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    flag = db.Column(db.Text, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=100)
    difficulty = db.Column(db.Enum('easy', 'medium', 'hard', 'expert'), nullable=False, default='medium')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, default=1)  # 设置默认管理员ID
    
    # 题目元数据
    solved_count = db.Column(db.Integer, default=0)
    first_blood_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_hidden = db.Column(db.Boolean, default=False)
    hints = db.Column(db.Text)  # JSON格式存储提示
    
    # 文件附件
    attachment_filename = db.Column(db.String(255))
    attachment_url = db.Column(db.String(255))
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    submissions = db.relationship('Submission', backref='challenge', lazy='dynamic', cascade='all, delete-orphan')
    first_blood_user = db.relationship('User', foreign_keys=[first_blood_user_id], backref='first_bloods')
    
    def get_hints(self):
        """获取提示列表"""
        if self.hints:
            try:
                return json.loads(self.hints)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_hints(self, hints_list):
        """设置提示列表"""
        if hints_list and isinstance(hints_list, list):
            self.hints = json.dumps(hints_list)
        else:
            self.hints = None
    
    def to_dict(self, include_flag=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'points': self.points,
            'difficulty': self.difficulty,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'solved_count': self.solved_count,
            'first_blood_user_id': self.first_blood_user_id,
            'is_hidden': self.is_hidden,
            'hints': self.get_hints(),
            'attachment_filename': self.attachment_filename,
            'attachment_url': self.attachment_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_flag:
            data['flag'] = self.flag
        
        return data
    
    def __repr__(self):
        return f'<Challenge {self.title}>'

class Submission(db.Model):
    """提交记录模型"""
    
    __tablename__ = 'submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False, index=True)
    flag_submitted = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user_rel = db.relationship('User', backref='submission_records', foreign_keys=[user_id])
    challenge_rel = db.relationship('Challenge', backref='submission_records', foreign_keys=[challenge_id])
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user_rel.username if self.user_rel else None,
            'challenge_id': self.challenge_id,
            'challenge_title': self.challenge_rel.title if self.challenge_rel else None,
            'flag_submitted': self.flag_submitted,
            'is_correct': self.is_correct,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
    
    def __repr__(self):
        return f'<Submission {self.user_id} -> {self.challenge_id} : {self.is_correct}>'


class SystemLog(db.Model):
    """系统日志模型"""
    
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Enum('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'), nullable=False)
    module = db.Column(db.String(64), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    ip_address = db.Column(db.String(45))  # 支持IPv6
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user = db.relationship('User', backref='logs')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'level': self.level,
            'module': self.module,
            'message': self.message,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SystemLog {self.level} - {self.module}>'

# 初始化数据库
def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认分类
        default_categories = [
            ('Web', 'Web安全相关题目'),
            ('Pwn', '二进制漏洞利用题目'),
            ('Reverse', '逆向工程题目'),
            ('Crypto', '密码学题目'),
            ('Misc', '杂项题目'),
            ('Forensics', '数字取证题目')
        ]
        
        for name, description in default_categories:
            if not Category.query.filter_by(name=name).first():
                category = Category(name=name, description=description)
                db.session.add(category)
        
        # 创建默认管理员用户（确保用户名正确）
        admin_username = 'admin'
        admin_user = User.query.filter_by(username=admin_username).first()
        
        if not admin_user:
            print("创建默认管理员用户...")
            admin_user = User(
                username=admin_username,  # 确保设置用户名
                email='admin@ctfplatform.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
        else:
            # 确保现有用户的用户名正确
            if admin_user.username != admin_username:
                print(f"修复管理员用户名: '{admin_user.username}' -> '{admin_username}'")
                admin_user.username = admin_username
            
            # 确保是管理员
            if not admin_user.is_admin:
                print(f"将用户 {admin_username} 设置为管理员...")
                admin_user.is_admin = True
        
        db.session.commit()
        print("数据库初始化完成!")