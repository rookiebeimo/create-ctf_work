import hashlib
import secrets
import string
import re
from flask import current_app

def generate_flag(prefix="CTF", format_type="static", length=32):
    """
    生成Flag
    
    Args:
        prefix: Flag前缀
        format_type: Flag类型 ('static', 'dynamic')
        length: Flag长度
    
    Returns:
        str: 生成的Flag
    """
    if format_type == "static":
        # 静态Flag: CTF{random_string}
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        return f"{prefix}{{{random_part}}}"
    
    elif format_type == "dynamic":
        # 动态Flag: 基于题目ID和密钥生成
        # 这里可以根据需要实现更复杂的动态Flag生成逻辑
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
        return f"{prefix}{{{random_part}}}"
    
    else:
        raise ValueError(f"Unsupported flag format: {format_type}")

def verify_flag(submitted_flag, correct_flag, case_sensitive=False, strict_format=True):
    """
    验证Flag
    
    Args:
        submitted_flag: 用户提交的Flag
        correct_flag: 正确的Flag
        case_sensitive: 是否区分大小写
        strict_format: 是否严格验证格式
    
    Returns:
        bool: Flag是否正确
    """
    if not submitted_flag or not correct_flag:
        return False
    
    # 预处理Flag
    submitted = submitted_flag.strip()
    correct = correct_flag.strip()
    
    if not case_sensitive:
        submitted = submitted.lower()
        correct = correct.lower()
    
    # 严格模式：完全匹配
    if strict_format:
        return submitted == correct
    
    # 宽松模式：去除空格等字符后匹配
    else:
        submitted_clean = re.sub(r'\s+', '', submitted)
        correct_clean = re.sub(r'\s+', '', correct)
        return submitted_clean == correct_clean

def hash_flag(flag, method='sha256'):
    """
    对Flag进行哈希（用于安全存储）
    
    Args:
        flag: 原始Flag
        method: 哈希方法
    
    Returns:
        str: 哈希后的Flag
    """
    if method == 'sha256':
        return hashlib.sha256(flag.encode()).hexdigest()
    elif method == 'md5':
        return hashlib.md5(flag.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash method: {method}")

def validate_flag_format(flag, expected_prefix="CTF"):
    """
    验证Flag格式
    
    Args:
        flag: 要验证的Flag
        expected_prefix: 期望的前缀
    
    Returns:
        bool: 格式是否正确
    """
    if not flag:
        return False
    
    # 检查是否包含大括号
    if '{' not in flag or '}' not in flag:
        return False
    
    # 检查前缀
    if expected_prefix and not flag.startswith(expected_prefix):
        return False
    
    # 提取内容部分
    try:
        content = flag[flag.index('{')+1:flag.index('}')]
        if not content:
            return False
    except ValueError:
        return False
    
    return True

def generate_dynamic_flag(challenge_id, user_id, secret_key):
    """
    生成动态Flag（基于题目ID和用户ID）
    
    Args:
        challenge_id: 题目ID
        user_id: 用户ID
        secret_key: 密钥
    
    Returns:
        str: 动态Flag
    """
    import hmac
    message = f"{challenge_id}:{user_id}"
    signature = hmac.new(
        secret_key.encode(), 
        message.encode(), 
        hashlib.sha256
    ).hexdigest()[:16]
    
    return f"CTF{{{signature}}}"