// 认证相关功能
const Auth = {
    // 初始化认证状态
    init() {
        this.updateAuthUI();
        
        // 登录表单提交
        document.getElementById('login-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });
        
        // 注册表单提交
        document.getElementById('register-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.register();
        });
        
        // 退出登录
        document.getElementById('logout-btn').addEventListener('click', () => {
            this.logout();
        });
    },
    
    // 更新认证UI
    updateAuthUI() {
        const authNav = document.getElementById('auth-nav');
        const adminMenuItems = document.querySelectorAll('.admin-only');
        
        if (Utils.isLoggedIn()) {
            // 用户已登录，显示用户信息和退出按钮
            authNav.innerHTML = `
                <li class="nav-item">
                    <a class="nav-link" href="#" data-page="profile">
                        <i class="fas fa-user"></i> 个人中心
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" id="logout-link">
                        <i class="fas fa-sign-out-alt"></i> 退出
                    </a>
                </li>
            `;
            
            // 添加退出登录事件
            document.getElementById('logout-link').addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
            
            // 加载用户信息并检查管理员权限
            this.checkAdminStatus();
            
        } else {
            // 用户未登录，显示登录注册按钮
            authNav.innerHTML = `
                <li class="nav-item">
                    <a class="nav-link" href="#" data-page="login">
                        <i class="fas fa-sign-in-alt"></i> 登录
                    </a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#" data-page="register">
                        <i class="fas fa-user-plus"></i> 注册
                    </a>
                </li>
            `;
            
            // 隐藏管理员菜单
            adminMenuItems.forEach(item => {
                item.style.display = 'none';
            });
        }
    },

    // 检查管理员状态
    async checkAdminStatus() {
        try {
            const data = await Utils.apiRequest('/auth/profile');
            const user = data.user;
            
            const adminMenuItems = document.querySelectorAll('.admin-only');
            if (user && user.is_admin) {
                // 显示管理员菜单
                adminMenuItems.forEach(item => {
                    item.style.display = 'block';
                });
            } else {
                // 隐藏管理员菜单
                adminMenuItems.forEach(item => {
                    item.style.display = 'none';
                });
            }
        } catch (error) {
            console.error('检查管理员状态失败:', error);
            // 如果获取用户信息失败，隐藏管理员菜单
            const adminMenuItems = document.querySelectorAll('.admin-only');
            adminMenuItems.forEach(item => {
                item.style.display = 'none';
            });
        }
    },
    
    // 用户登录
    async login() {
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const data = await Utils.apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            Utils.setAuthToken(data.token);
            Utils.showAlert('登录成功！', 'success');
            this.updateAuthUI();
            Utils.showPage('home');
        } catch (error) {
            // 错误处理已在apiRequest中完成
        }
    },
    
    // 用户注册
    async register() {
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const passwordConfirm = document.getElementById('register-password-confirm').value;
        
        if (password !== passwordConfirm) {
            Utils.showAlert('两次输入的密码不一致', 'danger');
            return;
        }
        
        try {
            await Utils.apiRequest('/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
            
            Utils.showAlert('注册成功，请登录！', 'success');
            Utils.showPage('login');
        } catch (error) {
            // 错误处理已在apiRequest中完成
        }
    },
    
    // 退出登录
    logout() {
        Utils.removeAuthToken();
        Utils.showAlert('已退出登录', 'info');
        this.updateAuthUI();
        Utils.showPage('home');
    },
    
    // 加载用户信息
    async loadUserProfile() {
        try {
            const data = await Utils.apiRequest('/auth/profile');
            this.displayUserProfile(data.user);
            return data.user;
        } catch (error) {
            // 如果获取用户信息失败，可能是token过期，强制退出登录
            if (error.message.includes('Token') || error.message.includes('Unauthorized')) {
                this.logout();
            }
            throw error;
        }
    },
    
    // 显示用户信息
    displayUserProfile(user) {
        // 更新个人中心页面
        document.getElementById('profile-username').textContent = user.username;
        document.getElementById('profile-email').textContent = user.email;
        document.getElementById('profile-score').textContent = user.score || 0;
        
        // 检查并更新管理员菜单显示状态
        const adminMenuItems = document.querySelectorAll('.admin-only');
        if (user && user.is_admin) {
            adminMenuItems.forEach(item => {
                item.style.display = 'block';
            });
        } else {
            adminMenuItems.forEach(item => {
                item.style.display = 'none';
            });
        }
        
        // 加载提交记录
        this.loadUserSubmissions(user.id);
    },
    
    // 加载用户提交记录
    async loadUserSubmissions(userId) {
        try {
            const data = await Utils.apiRequest(`/submissions/user/${userId}`);
            this.displaySubmissions(data.submissions);
        } catch (error) {
            console.error('加载提交记录失败:', error);
        }
    },
    
    // 显示提交记录
    displaySubmissions(submissions) {
        const submissionsList = document.getElementById('submissions-list');
        
        if (submissions.length === 0) {
            submissionsList.innerHTML = '<tr><td colspan="3" class="text-center">暂无提交记录</td></tr>';
            return;
        }
        
        submissionsList.innerHTML = submissions.map(submission => `
            <tr>
                <td>${submission.challenge_title}</td>
                <td>${Utils.formatDate(submission.submitted_at)}</td>
                <td>
                    <span class="badge ${submission.is_correct ? 'bg-success' : 'bg-danger'}">
                        ${submission.is_correct ? '正确' : '错误'}
                    </span>
                </td>
            </tr>
        `).join('');
    }
};