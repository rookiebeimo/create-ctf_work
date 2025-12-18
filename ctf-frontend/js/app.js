// 主应用逻辑
document.addEventListener('DOMContentLoaded', function() {
    // 初始化各个模块
    Auth.init();
    Challenges.init();
    Leaderboard.init();
    Admin.init();
    
    // 页面导航
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-page]') || e.target.closest('[data-page]')) {
            e.preventDefault();
            const page = e.target.getAttribute('data-page') || 
                         e.target.closest('[data-page]').getAttribute('data-page');
            navigateToPage(page);
        }
    });
    
    // 页面导航函数
    function navigateToPage(page) {
        switch (page) {
            case 'home':
                Utils.showPage('home-page');
                break;
            case 'login':
                Utils.showPage('login-page');
                break;
            case 'register':
                Utils.showPage('register-page');
                break;
            case 'admin':
                if (Utils.isLoggedIn()) {
                // 这里应该检查用户是否是管理员
                // 暂时先显示页面，实际权限检查在后台进行
                    Utils.showPage('admin-page');
                } else {
                    Utils.showAlert('请先登录', 'warning');
                    Utils.showPage('login-page');
                }
                break;
            case 'challenges':
                if (Utils.isLoggedIn()) {
                    Challenges.loadChallenges();
                    Utils.showPage('challenges-page');
                } else {
                    Utils.showAlert('请先登录', 'warning');
                    Utils.showPage('login-page');
                }
                break;
            case 'leaderboard':
                Leaderboard.loadGlobalLeaderboard();
                Leaderboard.loadCategories();
                Utils.showPage('leaderboard-page');
                break;
            case 'contests':
                // 比赛功能待实现
                Utils.showAlert('比赛功能开发中', 'info');
                break;
            case 'profile':
                if (Utils.isLoggedIn()) {
                    Auth.loadUserProfile();
                    Utils.showPage('profile-page');
                } else {
                    Utils.showAlert('请先登录', 'warning');
                    Utils.showPage('login-page');
                }
                break;
            default:
                Utils.showPage('home-page');
        }
    }
    
    // 检查认证状态并显示相应页面
    if (Utils.isLoggedIn()) {
        Auth.loadUserProfile();
    }
    
    // 显示首页
    Utils.showPage('home-page');
});