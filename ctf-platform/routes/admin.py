from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import db, User, Challenge, Submission, Category
from sqlalchemy import func
from utils.auth import token_required
import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

@admin_bp.route('/stats', methods=['GET'])  # 修复路由，去掉重复的/admin
@admin_required
def get_admin_stats(current_user):
    try:
        # Basic statistics
        total_users = User.query.count()
        total_challenges = Challenge.query.count()
        total_submissions = Submission.query.count()
        
        # Recent activity
        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= week_ago).count()
        recent_submissions = Submission.query.filter(Submission.submitted_at >= week_ago).count()
        
        # Challenge statistics
        challenges_by_difficulty = db.session.query(
            Challenge.difficulty,
            func.count(Challenge.id).label('count')
        ).group_by(Challenge.difficulty).all()
        
        # User growth (last 30 days)
        month_ago = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        user_growth = User.query.filter(User.created_at >= month_ago).count()
        
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_challenges': total_challenges,
                'total_submissions': total_submissions,
                'recent_users': recent_users,
                'recent_submissions': recent_submissions,
                'user_growth': user_growth,
                'challenges_by_difficulty': [
                    {'difficulty': diff, 'count': count} 
                    for diff, count in challenges_by_difficulty
                ]
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取管理员统计失败: {str(e)}")
        return jsonify({'message': '获取统计信息失败'}), 500

@admin_bp.route('/users', methods=['GET'])  # 修复路由
@admin_required
def get_all_users(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        user_list = []
        for user in users.items:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'score': user.score,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            user_list.append(user_data)
        
        return jsonify({
            'users': user_list,
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取用户列表失败: {str(e)}")
        return jsonify({'message': '获取用户列表失败'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        updatable_fields = ['username', 'email', 'is_admin', 'score']
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新用户失败: {str(e)}")
        return jsonify({'message': '更新用户失败'}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(current_user, user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Cannot delete yourself
        if user.id == current_user.id:
            return jsonify({'message': 'Cannot delete your own account!'}), 400
        
        # Delete user's submissions
        Submission.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除用户失败: {str(e)}")
        return jsonify({'message': '删除用户失败'}), 500

@admin_bp.route('/submissions', methods=['GET'])
@admin_required
def get_all_submissions(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        submissions = Submission.query.order_by(Submission.submitted_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        submission_list = []
        for submission in submissions.items:
            submission_data = {
                'id': submission.id,
                'user_id': submission.user_id,
                'username': submission.user.username,
                'challenge_id': submission.challenge_id,
                'challenge_title': submission.challenge.title,
                'flag_submitted': submission.flag_submitted,
                'is_correct': submission.is_correct,
                'submitted_at': submission.submitted_at.isoformat()
            }
            submission_list.append(submission_data)
        
        return jsonify({
            'submissions': submission_list,
            'total': submissions.total,
            'pages': submissions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取提交记录失败: {str(e)}")
        return jsonify({'message': '获取提交记录失败'}), 500

@admin_bp.route('/categories', methods=['POST'])
@admin_required
def create_category(current_user):
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'message': 'Category name is required!'}), 400
        
        category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully!',
            'category_id': category.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建分类失败: {str(e)}")
        return jsonify({'message': '创建分类失败'}), 500

@admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(current_user, category_id):
    try:
        category = Category.query.get_or_404(category_id)
        data = request.get_json()
        
        if data.get('name'):
            category.name = data['name']
        if data.get('description'):
            category.description = data['description']
        
        db.session.commit()
        
        return jsonify({'message': 'Category updated successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"更新分类失败: {str(e)}")
        return jsonify({'message': '更新分类失败'}), 500

@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(current_user, category_id):
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if category is being used by any challenges
        if category.challenges:
            return jsonify({
                'message': 'Cannot delete category that has challenges! Move or delete the challenges first.'
            }), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': 'Category deleted successfully!'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"删除分类失败: {str(e)}")
        return jsonify({'message': '删除分类失败'}), 500

@admin_bp.route('/backup', methods=['POST'])
@admin_required
def create_backup(current_user):
    try:
        # This is a simplified backup endpoint
        # In production, you'd want to implement proper database backup
        backup_data = {
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'users_count': User.query.count(),
            'challenges_count': Challenge.query.count(),
            'submissions_count': Submission.query.count()
        }
        
        return jsonify({
            'message': 'Backup created successfully!',
            'backup': backup_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"创建备份失败: {str(e)}")
        return jsonify({'message': '创建备份失败'}), 500

@admin_bp.route('/update-scores', methods=['POST'])
@admin_required
def update_scores(current_user):
    try:
        from utils.scoring import ScoringSystem
        ScoringSystem.update_challenge_scores()
        
        return jsonify({'message': 'Scores updated successfully!'}), 200
        
    except Exception as e:
        current_app.logger.error(f"更新分数失败: {str(e)}")
        return jsonify({'message': '更新分数失败'}), 500

@admin_bp.route('/export-data', methods=['GET'])
@admin_required
def export_data(current_user):
    try:
        import json
        from datetime import datetime
        
        data = {
            'export_time': datetime.utcnow().isoformat(),
            'users': [user.to_dict() for user in User.query.all()],
            'challenges': [challenge.to_dict() for challenge in Challenge.query.all()],
            'submissions': [submission.to_dict() for submission in Submission.query.limit(1000).all()],
            'categories': [category.to_dict() for category in Category.query.all()]
        }
        
        return jsonify(data), 200
        
    except Exception as e:
        current_app.logger.error(f"导出数据失败: {str(e)}")
        return jsonify({'message': '导出数据失败'}), 500