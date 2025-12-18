// API基础URL
const API_BASE = 'http://localhost:5000/api/v1';

// 工具函数
const Utils = {
    // 显示加载提示
    showLoading() {
        document.getElementById('loading').classList.remove('d-none');
    },
    
    // 隐藏加载提示
    hideLoading() {
        document.getElementById('loading').classList.add('d-none');
    },
    
    // 显示消息提示
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        const alertId = 'alert-' + Date.now();
        
        const alertHTML = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.innerHTML += alertHTML;
        
        // 5秒后自动关闭
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    },
    
    // 切换页面
    showPage(pageId) {
        // 隐藏所有页面
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // 显示目标页面
        const targetPage = document.getElementById(pageId);
        if (targetPage) {
            targetPage.classList.add('active');
        }
    },
    
    // 格式化日期
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    },
    
    // 获取难度标签类名
    getDifficultyClass(difficulty) {
        switch (difficulty) {
            case 'easy': return 'badge-difficulty-easy';
            case 'medium': return 'badge-difficulty-medium';
            case 'hard': return 'badge-difficulty-hard';
            case 'expert': return 'badge-difficulty-expert';
            default: return 'badge-secondary';
        }
    },
    
    // 获取难度中文名称
    getDifficultyText(difficulty) {
        switch (difficulty) {
            case 'easy': return '简单';
            case 'medium': return '中等';
            case 'hard': return '困难';
            case 'expert': return '专家';
            default: return difficulty;
        }
    },
    
    // 设置认证token
    setAuthToken(token) {
        localStorage.setItem('ctf_token', token);
    },
    
    // 获取认证token
    getAuthToken() {
        return localStorage.getItem('ctf_token');
    },
    
    // 移除认证token
    removeAuthToken() {
        localStorage.removeItem('ctf_token');
    },
    
    // 检查是否已登录
    isLoggedIn() {
        return !!this.getAuthToken();
    },
    
    // API请求封装
    async apiRequest(endpoint, options = {}) {
        const token = this.getAuthToken();
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            this.showLoading();
            const response = await fetch(`${API_BASE}${endpoint}`, finalOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || '请求失败');
            }
            
            return data;
        } catch (error) {
            this.showAlert(error.message, 'danger');
            throw error;
        } finally {
            this.hideLoading();
        }
    }
};