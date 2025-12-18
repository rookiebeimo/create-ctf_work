from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime
from functools import wraps
from models import db, User
from config import Config

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'message': 'Username, password and email are required!'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists!'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists!'}), 400
        
        # Create new user
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_password,
            created_at=datetime.datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully!',
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password are required!'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'message': 'Invalid credentials!'}), 401
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful!',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'is_admin': current_user.is_admin,
            'created_at': current_user.created_at.isoformat(),
            'score': current_user.score
        }
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        if data.get('email'):
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != current_user.id:
                return jsonify({'message': 'Email already exists!'}), 400
            current_user.email = data['email']
        
        if data.get('password'):
            current_user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully!'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500