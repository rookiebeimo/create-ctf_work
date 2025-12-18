from flask import Blueprint, request, jsonify
from models import db, User, Submission, Challenge
from sqlalchemy import func, desc, case, text
from utils.auth import token_required
import datetime

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard', methods=['GET'])
@token_required
def get_leaderboard(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # 全球排行榜查询
        user_scores = db.session.query(
            User.id,
            User.username,
            User.score,
            func.count(case((Submission.is_correct == True, Submission.id))).label('solved_count'),
            func.max(case((Submission.is_correct == True, Submission.submitted_at))).label('last_solve')
        ).outerjoin(Submission, User.id == Submission.user_id)\
         .filter(User.is_admin == False)\
         .group_by(User.id)\
         .order_by(desc(User.score), desc('solved_count'))\
         .paginate(page=page, per_page=per_page, error_out=False)
        
        leaderboard = []
        rank_offset = (page - 1) * per_page
        
        for i, user in enumerate(user_scores.items, start=1):
            user_data = {
                'rank': rank_offset + i,
                'user_id': user.id,
                'username': user.username,
                'score': user.score or 0,
                'solved_count': user.solved_count or 0,
                'last_solve': user.last_solve.isoformat() if user.last_solve else None
            }
            leaderboard.append(user_data)
        
        return jsonify({
            'leaderboard': leaderboard,
            'total': user_scores.total,
            'pages': user_scores.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        import traceback
        print(f"排行榜错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@leaderboard_bp.route('/leaderboard/category/<int:category_id>', methods=['GET'])
@token_required
def get_category_leaderboard(current_user, category_id):
    try:
        # 简化的分类排行榜实现
        # 获取所有非管理员用户
        users = User.query.filter_by(is_admin=False).all()
        
        leaderboard_data = []
        
        for user in users:
            # 获取用户在该分类下解决的所有题目（去重）
            solved_challenges_query = db.session.query(
                Submission.challenge_id
            ).join(
                Challenge, Submission.challenge_id == Challenge.id
            ).filter(
                Submission.user_id == user.id,
                Submission.is_correct == True,
                Challenge.category_id == category_id
            ).distinct()
            
            solved_challenges = solved_challenges_query.all()
            solved_count = len(solved_challenges)
            
            if solved_count > 0:
                # 计算该分类下的总分
                total_score = 0
                for challenge_tuple in solved_challenges:
                    challenge_id = challenge_tuple[0]
                    challenge = Challenge.query.get(challenge_id)
                    if challenge:
                        total_score += challenge.points
                
                leaderboard_data.append({
                    'user_id': user.id,
                    'username': user.username,
                    'score': total_score,
                    'solved_count': solved_count
                })
        
        # 按分数排序
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
        
        # 添加排名
        leaderboard = []
        for i, user_data in enumerate(leaderboard_data, start=1):
            user_data['rank'] = i
            leaderboard.append(user_data)
        
        return jsonify({
            'category_id': category_id,
            'leaderboard': leaderboard
        }), 200
        
    except Exception as e:
        import traceback
        print(f"分类排行榜错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'message': str(e)}), 500

@leaderboard_bp.route('/leaderboard/challenge/<int:challenge_id>', methods=['GET'])
@token_required
def get_challenge_leaderboard(current_user, challenge_id):
    try:
        # 题目排行榜：显示解决该题目的用户（按解决时间排序）
        submissions = db.session.query(
            Submission.user_id,
            User.username,
            Submission.submitted_at
        ).join(
            User, Submission.user_id == User.id
        ).filter(
            Submission.challenge_id == challenge_id,
            Submission.is_correct == True
        ).order_by(
            Submission.submitted_at
        ).all()
        
        leaderboard = []
        for i, submission in enumerate(submissions, start=1):
            user_data = {
                'rank': i,
                'user_id': submission.user_id,
                'username': submission.username,
                'solved_at': submission.submitted_at.isoformat()
            }
            leaderboard.append(user_data)
        
        return jsonify({
            'challenge_id': challenge_id,
            'leaderboard': leaderboard
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500
