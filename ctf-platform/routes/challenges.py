from flask import Blueprint, request, jsonify, send_file, current_app
from functools import wraps
import os
import datetime
import json
from models import db, Challenge, Submission, User, Category
from utils.auth import token_required
from utils.flag import verify_flag
from utils.scoring import ScoringSystem
from config import Config

challenges_bp = Blueprint('challenges', __name__)

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@challenges_bp.route('/challenges', methods=['GET'])
@token_required
def get_challenges(current_user):
    try:
        # 管理员可以看到所有题目，包括隐藏的
        if current_user.is_admin:
            challenges = Challenge.query.all()
        else:
            challenges = Challenge.query.filter_by(is_hidden=False).all()
        
        result = []
        for challenge in challenges:
            # Check if user has solved this challenge
            solved = Submission.query.filter_by(
                user_id=current_user.id,
                challenge_id=challenge.id,
                is_correct=True
            ).first() is not None
            
            challenge_data = {
                'id': challenge.id,
                'title': challenge.title,
                'description': challenge.description,
                'category': challenge.category.name if challenge.category else 'General',
                'category_id': challenge.category_id,
                'difficulty': challenge.difficulty,
                'points': challenge.points,
                'solved_count': challenge.solved_count,
                'is_solved': solved,
                'is_hidden': challenge.is_hidden,
                'created_at': challenge.created_at.isoformat() if challenge.created_at else None
            }
            
            # Only show hints to users who have attempted the challenge or are admins
            if current_user.is_admin or Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
                try:
                    challenge_data['hints'] = json.loads(challenge.hints) if challenge.hints else []
                except:
                    challenge_data['hints'] = []
            
            result.append(challenge_data)
        
        return jsonify({'challenges': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取题目列表失败: {str(e)}")
        return jsonify({'message': '获取题目列表失败'}), 500

@challenges_bp.route('/challenges/<int:challenge_id>', methods=['GET'])
@token_required
def get_challenge(current_user, challenge_id):
    try:
        challenge = Challenge.query.get_or_404(challenge_id)
        
        if challenge.is_hidden and not current_user.is_admin:
            return jsonify({'message': 'Challenge not found!'}), 404
        
        solved = Submission.query.filter_by(
            user_id=current_user.id,
            challenge_id=challenge.id,
            is_correct=True
        ).first() is not None
        
        challenge_data = {
            'id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'category': challenge.category.name if challenge.category else 'General',
            'category_id': challenge.category_id,
            'difficulty': challenge.difficulty,
            'points': challenge.points,
            'solved_count': challenge.solved_count,
            'is_solved': solved,
            'is_hidden': challenge.is_hidden,
            'created_at': challenge.created_at.isoformat() if challenge.created_at else None,
            'updated_at': challenge.updated_at.isoformat() if challenge.updated_at else None
        }
        
        # Only show hints to users who have attempted the challenge or are admins
        if current_user.is_admin or Submission.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
            try:
                challenge_data['hints'] = json.loads(challenge.hints) if challenge.hints else []
            except:
                challenge_data['hints'] = []
        
        return jsonify({'challenge': challenge_data}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取题目详情失败: {str(e)}")
        return jsonify({'message': '获取题目详情失败'}), 500

@challenges_bp.route('/challenges/<int:challenge_id>/submit', methods=['POST'])
@token_required
def submit_flag(current_user, challenge_id):
    try:
        data = request.get_json()
        
        if not data or not data.get('flag'):
            return jsonify({'message': 'Flag is required!'}), 400
        
        challenge = Challenge.query.get_or_404(challenge_id)
        
        if challenge.is_hidden and not current_user.is_admin:
            return jsonify({'message': 'Challenge not found!'}), 404
        
        # Check if already solved
        existing_solution = Submission.query.filter_by(
            user_id=current_user.id,
            challenge_id=challenge_id,
            is_correct=True
        ).first()
        
        if existing_solution:
            return jsonify({'message': 'You have already solved this challenge!'}), 400
        
        # Verify flag
        is_correct = verify_flag(data['flag'], challenge.flag)
        
        submission = Submission(
            user_id=current_user.id,
            challenge_id=challenge_id,
            flag_submitted=data['flag'],
            is_correct=is_correct,
            submitted_at=datetime.datetime.utcnow()
        )
        
        db.session.add(submission)
        
        if is_correct:
            # Update user score and challenge solved count
            current_user.score += challenge.points
            challenge.solved_count += 1
            
            # Update first blood if this is the first solution
            if challenge.solved_count == 1:
                challenge.first_blood_user_id = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'message': 'Correct flag!' if is_correct else 'Incorrect flag!',
            'is_correct': is_correct
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"提交Flag失败: {str(e)}")
        return jsonify({'message': '提交Flag失败'}), 500

@challenges_bp.route('/challenges', methods=['POST'])
@admin_required
def create_challenge(current_user):
    try:
        # 检查请求数据
        if not request.json:
            return jsonify({'message': '请求数据必须是JSON格式'}), 400
            
        data = request.get_json()
        
        # 详细的字段验证
        required_fields = ['title', 'description', 'flag', 'points', 'difficulty', 'category_id']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            return jsonify({
                'message': f'缺少必填字段: {", ".join(missing_fields)}'
            }), 400
        
        # 验证数据类型
        try:
            points = int(data['points'])
            category_id = int(data['category_id'])
        except (ValueError, TypeError):
            return jsonify({'message': '分数和分类ID必须是数字'}), 400
        
        # 验证分类是否存在
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': '分类不存在'}), 400
        
        # 验证难度值
        valid_difficulties = ['easy', 'medium', 'hard', 'expert']
        if data['difficulty'] not in valid_difficulties:
            return jsonify({'message': '难度值无效'}), 400
        
        # 处理提示字段
        hints = data.get('hints', [])
        if hints and isinstance(hints, list):
            hints_json = json.dumps(hints)
        else:
            hints_json = None
        
        # 创建题目对象
        challenge = Challenge(
            title=data['title'].strip(),
            description=data['description'].strip(),
            flag=data['flag'].strip(),
            points=points,
            difficulty=data['difficulty'],
            category_id=category_id,
            creator_id=current_user.id,
            hints=hints_json,
            is_hidden=bool(data.get('is_hidden', False)),
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow()
        )
        
        db.session.add(challenge)
        db.session.commit()
        
        # 返回完整的成功响应
        response_data = {
            'message': '题目创建成功!',
            'challenge_id': challenge.id,
            'challenge': {
                'id': challenge.id,
                'title': challenge.title,
                'points': challenge.points,
                'difficulty': challenge.difficulty
            }
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        # 回滚数据库会话
        db.session.rollback()
        
        # 详细的错误日志
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"创建题目错误详情: {error_details}")
        
        # 返回明确的错误信息
        error_message = f'创建题目失败: {str(e)}'
        if 'creator_id' in str(e).lower():
            error_message = '创建题目失败: 用户身份验证问题'
        elif 'foreign key' in str(e).lower():
            error_message = '创建题目失败: 分类不存在或用户不存在'
        
        return jsonify({
            'message': error_message,
            'error': str(e) if current_app.debug else None
        }), 500

@challenges_bp.route('/challenges/<int:challenge_id>', methods=['PUT'])
@admin_required
def update_challenge(current_user, challenge_id):
    try:
        challenge = Challenge.query.get_or_404(challenge_id)
        data = request.get_json()
        
        updatable_fields = ['title', 'description', 'flag', 'points', 'difficulty', 'category_id', 'is_hidden']
        
        for field in updatable_fields:
            if field in data:
                setattr(challenge, field, data[field])
        
        # 特殊处理 hints 字段
        if 'hints' in data:
            hints = data['hints']
            if hints and isinstance(hints, list):
                challenge.hints = json.dumps(hints)
            else:
                challenge.hints = None
        
        challenge.updated_at = datetime.datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Challenge updated successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新题目失败: {str(e)}")
        return jsonify({'message': '更新题目失败'}), 500

@challenges_bp.route('/challenges/<int:challenge_id>', methods=['DELETE'])
@admin_required
def delete_challenge(current_user, challenge_id):
    try:
        challenge = Challenge.query.get_or_404(challenge_id)
        
        # Delete related submissions first
        Submission.query.filter_by(challenge_id=challenge_id).delete()
        
        db.session.delete(challenge)
        db.session.commit()
        
        return jsonify({'message': 'Challenge deleted successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除题目失败: {str(e)}")
        return jsonify({'message': '删除题目失败'}), 500

@challenges_bp.route('/categories', methods=['GET'])
@token_required
def get_categories(current_user):
    try:
        categories = Category.query.all()
        
        result = []
        for category in categories:
            category_data = {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'created_at': category.created_at.isoformat() if category.created_at else None
            }
            result.append(category_data)
        
        return jsonify({'categories': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"获取分类列表失败: {str(e)}")
        return jsonify({'message': '获取分类列表失败'}), 500

@challenges_bp.route('/challenges/<int:challenge_id>/download', methods=['GET'])
@token_required
def download_attachment(current_user, challenge_id):
    try:
        challenge = Challenge.query.get_or_404(challenge_id)
        
        if not challenge.attachment_filename or not challenge.attachment_url:
            return jsonify({'message': 'No attachment available for this challenge!'}), 404
        
        # 检查文件是否存在
        file_path = os.path.join(Config.CHALLENGE_ATTACHMENTS_FOLDER, challenge.attachment_filename)
        
        if not os.path.exists(file_path):
            return jsonify({'message': 'Attachment file not found!'}), 404
        
        return send_file(file_path, as_attachment=True, download_name=challenge.attachment_filename)
        
    except Exception as e:
        current_app.logger.error(f"下载附件失败: {str(e)}")
        return jsonify({'message': '下载附件失败'}), 500