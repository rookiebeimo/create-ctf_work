import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
from models import User

def token_required(f):
    """JWT token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            # 解码token
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

def generate_token(user_id, username, is_admin=False):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    """验证JWT token"""
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user():
    """获取当前用户"""
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return User.query.get(data['user_id'])
    except:
        return None