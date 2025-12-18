from flask import Blueprint, request, jsonify
from models import db, Submission, User, Challenge
from utils.auth import token_required
from config import Config
import datetime

submissions_bp = Blueprint('submissions', __name__)

@submissions_bp.route('/submissions', methods=['GET'])
@token_required
def get_submissions(current_user):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        challenge_id = request.args.get('challenge_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        # Base query
        query = Submission.query
        
        # Filter by challenge if provided
        if challenge_id:
            query = query.filter_by(challenge_id=challenge_id)
        
        # Filter by user if provided (admin can see all, users can only see their own)
        if user_id:
            if current_user.is_admin:
                query = query.filter_by(user_id=user_id)
            else:
                return jsonify({'message': 'Access denied!'}), 403
        else:
            if not current_user.is_admin:
                query = query.filter_by(user_id=current_user.id)
        
        # Order by submission time (newest first)
        query = query.order_by(Submission.submitted_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        submissions = []
        for submission in pagination.items:
            submission_data = {
                'id': submission.id,
                'user_id': submission.user_id,
                'username': submission.user.username,
                'challenge_id': submission.challenge_id,
                'challenge_title': submission.challenge.title,
                'is_correct': submission.is_correct,
                'submitted_at': submission.submitted_at.isoformat()
            }
            
            # Only show submitted flag to admins or the user who submitted it
            if current_user.is_admin or current_user.id == submission.user_id:
                submission_data['flag_submitted'] = submission.flag_submitted
            
            submissions.append(submission_data)
        
        return jsonify({
            'submissions': submissions,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/submissions/user/<int:user_id>', methods=['GET'])
@token_required
def get_user_submissions(current_user, user_id):
    try:
        # Users can only see their own submissions unless they are admin
        if not current_user.is_admin and current_user.id != user_id:
            return jsonify({'message': 'Access denied!'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        submissions = Submission.query.filter_by(user_id=user_id)\
            .order_by(Submission.submitted_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for submission in submissions.items:
            submission_data = {
                'id': submission.id,
                'challenge_id': submission.challenge_id,
                'challenge_title': submission.challenge.title,
                'is_correct': submission.is_correct,
                'submitted_at': submission.submitted_at.isoformat()
            }
            
            if current_user.is_admin or current_user.id == user_id:
                submission_data['flag_submitted'] = submission.flag_submitted
            
            result.append(submission_data)
        
        return jsonify({
            'submissions': result,
            'total': submissions.total,
            'pages': submissions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/submissions/challenge/<int:challenge_id>', methods=['GET'])
@token_required
def get_challenge_submissions(current_user, challenge_id):
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Base query
        query = Submission.query.filter_by(challenge_id=challenge_id)
        
        # Non-admin users can only see their own submissions for a challenge
        if not current_user.is_admin:
            query = query.filter_by(user_id=current_user.id)
        
        submissions = query.order_by(Submission.submitted_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        result = []
        for submission in submissions.items:
            submission_data = {
                'id': submission.id,
                'user_id': submission.user_id,
                'username': submission.user.username,
                'is_correct': submission.is_correct,
                'submitted_at': submission.submitted_at.isoformat()
            }
            
            if current_user.is_admin or current_user.id == submission.user_id:
                submission_data['flag_submitted'] = submission.flag_submitted
            
            result.append(submission_data)
        
        return jsonify({
            'submissions': result,
            'total': submissions.total,
            'pages': submissions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@submissions_bp.route('/submissions/stats', methods=['GET'])
@token_required
def get_submission_stats(current_user):
    try:
        # Total submissions
        total_submissions = Submission.query.count()
        
        # Correct submissions
        correct_submissions = Submission.query.filter_by(is_correct=True).count()
        
        # User's submissions
        user_total = Submission.query.filter_by(user_id=current_user.id).count()
        user_correct = Submission.query.filter_by(user_id=current_user.id, is_correct=True).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        recent_submissions = Submission.query.filter(
            Submission.submitted_at >= week_ago
        ).count()
        
        return jsonify({
            'stats': {
                'total_submissions': total_submissions,
                'correct_submissions': correct_submissions,
                'accuracy_rate': (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0,
                'user_total': user_total,
                'user_correct': user_correct,
                'user_accuracy': (user_correct / user_total * 100) if user_total > 0 else 0,
                'recent_submissions': recent_submissions
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500