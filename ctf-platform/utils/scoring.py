import math
from datetime import datetime
from models import Challenge, Submission

class ScoringSystem:
    """积分计算系统"""
    
    @staticmethod
    def calculate_dynamic_score(challenge, total_solves, time_decay=True, base_points=1000):
        """
        计算动态分数
        
        Args:
            challenge: 题目对象
            total_solves: 总解题人数
            time_decay: 是否启用时间衰减
            base_points: 基础分数
        
        Returns:
            int: 计算后的分数
        """
        if not challenge:
            return 0
        
        # 基础分数
        base_score = challenge.points or base_points
        
        # 根据难度调整基础分数
        difficulty_multiplier = ScoringSystem._get_difficulty_multiplier(challenge.difficulty)
        base_score = int(base_score * difficulty_multiplier)
        
        # 根据解题人数调整分数（解题越多，分数越低）
        if total_solves > 0:
            solve_ratio = min(total_solves / 100, 1.0)  # 假设最多100人解题
            decay_factor = 1.0 - (solve_ratio * 0.5)    # 最多衰减50%
            base_score = int(base_score * decay_factor)
        
        # 时间衰减（题目发布越久，分数越低）
        if time_decay and challenge.created_at:
            days_since_creation = (datetime.utcnow() - challenge.created_at).days
            time_decay_factor = max(0.5, 1.0 - (days_since_creation * 0.01))  # 每天衰减1%，最多衰减50%
            base_score = int(base_score * time_decay_factor)
        
        return max(100, base_score)  # 最低100分

    @staticmethod
    def _get_difficulty_multiplier(difficulty):
        """获取难度系数"""
        multipliers = {
            'easy': 0.7,
            'medium': 1.0,
            'hard': 1.5,
            'expert': 2.0
        }
        return multipliers.get(difficulty.lower(), 1.0)

    @staticmethod
    def calculate_user_score(user):
        """
        计算用户总分
        
        Args:
            user: 用户对象
        
        Returns:
            int: 用户总分
        """
        if not user:
            return 0
        
        # 从数据库中获取用户正确提交的题目
        correct_submissions = Submission.query.filter_by(
            user_id=user.id, 
            is_correct=True
        ).all()
        
        total_score = 0
        solved_challenges = set()
        
        for submission in correct_submissions:
            # 只计算每个题目的最高分（防止重复计算）
            if submission.challenge_id not in solved_challenges:
                total_score += submission.challenge.points
                solved_challenges.add(submission.challenge_id)
        
        return total_score

    @staticmethod
    def update_challenge_scores():
        """
        更新所有题目的动态分数
        """
        from models import db, Challenge
        
        challenges = Challenge.query.all()
        
        for challenge in challenges:
            total_solves = Submission.query.filter_by(
                challenge_id=challenge.id,
                is_correct=True
            ).distinct(Submission.user_id).count()
            
            new_score = ScoringSystem.calculate_dynamic_score(
                challenge, 
                total_solves
            )
            
            # 更新题目分数
            challenge.points = new_score
            challenge.solved_count = total_solves
        
        db.session.commit()

    @staticmethod
    def calculate_blood_bonus(position):
        """
        计算一血/二血/三血奖励
        
        Args:
            position: 解题位置 (1, 2, 3)
        
        Returns:
            int: 奖励分数
        """
        bonuses = {
            1: 100,  # 一血奖励
            2: 50,   # 二血奖励
            3: 25    # 三血奖励
        }
        return bonuses.get(position, 0)

    @staticmethod
    def get_user_rank(user_id):
        """
        获取用户排名
        
        Args:
            user_id: 用户ID
        
        Returns:
            int: 用户排名
        """
        from models import User
        from sqlalchemy import desc
        
        # 获取所有用户按分数排序
        users = User.query.filter_by(is_admin=False).order_by(desc(User.score)).all()
        
        for rank, user in enumerate(users, start=1):
            if user.id == user_id:
                return rank
        
        return None