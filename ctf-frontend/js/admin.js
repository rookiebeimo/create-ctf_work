// 管理员功能模块
const Admin = {
    // 初始化
    init() {
        // 添加题目按钮
        document.getElementById('add-challenge-btn').addEventListener('click', () => {
            this.showAddChallengeModal();
        });
        
        // 添加分类按钮
        document.getElementById('add-category-btn').addEventListener('click', () => {
            this.showAddCategoryModal();
        });
        
        // 系统操作按钮
        document.getElementById('update-scores-btn').addEventListener('click', () => {
            this.updateChallengeScores();
        });
        
        document.getElementById('export-data-btn').addEventListener('click', () => {
            this.exportPlatformData();
        });
        
        document.getElementById('clear-cache-btn').addEventListener('click', () => {
            this.clearCache();
        });
        
        // 页面切换时加载数据
        document.addEventListener('pageChanged', (e) => {
            if (e.detail.page === 'admin-page') {
                this.loadAdminData();
            }
        });
    },
    
// 加载管理员数据（带重试机制）
async loadAdminData(retryCount = 0) {
    const maxRetries = 2;
    
    try {
        // 加载统计信息 - 使用正确的API路径
        const statsData = await Utils.apiRequest('/admin/stats');
        console.log('统计数据:', statsData); // 调试日志
        this.displayStats(statsData.stats);
        
        // 加载题目列表
        const challengesData = await Utils.apiRequest('/challenges?all=true');
        this.displayChallenges(challengesData.challenges);
        
        // 加载用户列表
        const usersData = await Utils.apiRequest('/admin/users');
        this.displayUsers(usersData.users);
        
        // 加载分类列表
        const categoriesData = await Utils.apiRequest('/categories');
        this.displayCategories(categoriesData.categories);
        
    } catch (error) {
        console.error('加载管理员数据失败:', error);
        
        if (retryCount < maxRetries && error.message.includes('Failed to fetch')) {
            console.log(`第 ${retryCount + 1} 次重试...`);
            setTimeout(() => {
                this.loadAdminData(retryCount + 1);
            }, 1000 * (retryCount + 1));
        } else {
            Utils.showAlert('加载管理员数据失败，请检查网络连接', 'warning');
        }
    }
},
    
    // 显示统计信息
    displayStats(stats) {
        document.getElementById('admin-users-count').textContent = stats.total_users || 0;
        document.getElementById('admin-challenges-count').textContent = stats.total_challenges || 0;
        document.getElementById('admin-submissions-count').textContent = stats.total_submissions || 0;
        document.getElementById('admin-contests-count').textContent = stats.total_contests || 0;
    },
    
    // 显示题目列表
    displayChallenges(challenges) {
        const tbody = document.getElementById('admin-challenges-list');
        
        if (challenges.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center">暂无题目</td></tr>';
            return;
        }
        
        tbody.innerHTML = challenges.map(challenge => `
            <tr>
                <td>${challenge.id}</td>
                <td>${challenge.title}</td>
                <td><span class="badge bg-primary">${challenge.category}</span></td>
                <td><span class="badge ${Utils.getDifficultyClass(challenge.difficulty)}">${Utils.getDifficultyText(challenge.difficulty)}</span></td>
                <td>${challenge.points}</td>
                <td>${challenge.solved_count}</td>
                <td>
                    <span class="badge ${challenge.is_hidden ? 'bg-warning' : 'bg-success'}">
                        ${challenge.is_hidden ? '隐藏' : '公开'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-challenge" data-id="${challenge.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-challenge" data-id="${challenge.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        
        // 添加编辑和删除事件
        this.addChallengeEvents();
    },
    
    // 显示用户列表
    displayUsers(users) {
        const tbody = document.getElementById('admin-users-list');
        
        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">暂无用户</td></tr>';
            return;
        }
        
        tbody.innerHTML = users.map(user => `
            <tr>
                <td>${user.id}</td>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>${user.score}</td>
                <td>${Utils.formatDate(user.created_at)}</td>
                <td>
                    <span class="badge ${user.is_admin ? 'bg-danger' : 'bg-secondary'}">
                        ${user.is_admin ? '管理员' : '普通用户'}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-warning toggle-admin" data-id="${user.id}" data-is-admin="${user.is_admin}">
                        ${user.is_admin ? '取消管理员' : '设为管理员'}
                    </button>
                </td>
            </tr>
        `).join('');
        
        // 添加管理员切换事件
        this.addUserEvents();
    },
    
    // 显示分类列表
    displayCategories(categories) {
        const container = document.getElementById('admin-categories-list');
        
        if (categories.length === 0) {
            container.innerHTML = '<div class="col-12 text-center"><p>暂无分类</p></div>';
            return;
        }
        
        container.innerHTML = categories.map(category => `
            <div class="col-md-4 mb-3">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${category.name}</h5>
                        <p class="card-text">${category.description || '暂无描述'}</p>
                        <div class="d-flex justify-content-between">
                            <small class="text-muted">创建: ${Utils.formatDate(category.created_at)}</small>
                            <div>
                                <button class="btn btn-sm btn-outline-primary edit-category" data-id="${category.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger delete-category" data-id="${category.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // 添加分类操作事件
        this.addCategoryEvents();
    },
    
    // 添加题目操作事件
    addChallengeEvents() {
        // 编辑题目
        document.querySelectorAll('.edit-challenge').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const challengeId = e.target.closest('button').getAttribute('data-id');
                this.editChallenge(challengeId);
            });
        });
        
        // 删除题目
        document.querySelectorAll('.delete-challenge').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const challengeId = e.target.closest('button').getAttribute('data-id');
                this.deleteChallenge(challengeId);
            });
        });
    },
    
    // 添加用户操作事件
    addUserEvents() {
        // 切换管理员状态
        document.querySelectorAll('.toggle-admin').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const userId = e.target.getAttribute('data-id');
                const isAdmin = e.target.getAttribute('data-is-admin') === 'true';
                this.toggleUserAdmin(userId, !isAdmin);
            });
        });
    },
    
    // 添加分类操作事件
    addCategoryEvents() {
        // 编辑分类
        document.querySelectorAll('.edit-category').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const categoryId = e.target.closest('button').getAttribute('data-id');
                this.editCategory(categoryId);
            });
        });
        
        // 删除分类
        document.querySelectorAll('.delete-category').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const categoryId = e.target.closest('button').getAttribute('data-id');
                this.deleteCategory(categoryId);
            });
        });
    },
    
    // 显示添加题目模态框
    showAddChallengeModal() {
        // 创建模态框HTML
        const modalHTML = `
            <div class="modal fade" id="addChallengeModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">添加新题目</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="add-challenge-form">
                                <div class="mb-3">
                                    <label class="form-label">标题 <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" name="title" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">描述 <span class="text-danger">*</span></label>
                                    <textarea class="form-control" name="description" rows="4" required></textarea>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Flag <span class="text-danger">*</span></label>
                                    <input type="text" class="form-control" name="flag" required placeholder="CTF{...}">
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">分数 <span class="text-danger">*</span></label>
                                            <input type="number" class="form-control" name="points" value="100" min="1" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="mb-3">
                                            <label class="form-label">难度 <span class="text-danger">*</span></label>
                                            <select class="form-select" name="difficulty" required>
                                                <option value="easy">简单</option>
                                                <option value="medium" selected>中等</option>
                                                <option value="hard">困难</option>
                                                <option value="expert">专家</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">分类 <span class="text-danger">*</span></label>
                                    <select class="form-select" name="category_id" required>
                                        <option value="1">Web</option>
                                        <option value="2">Pwn</option>
                                        <option value="3">Reverse</option>
                                        <option value="4">Crypto</option>
                                        <option value="5">Misc</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">提示 (每行一个)</label>
                                    <textarea class="form-control" name="hints" rows="3" placeholder="每行输入一个提示"></textarea>
                                </div>
                                <div class="form-check mb-3">
                                    <input class="form-check-input" type="checkbox" name="is_hidden">
                                    <label class="form-check-label">隐藏题目</label>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-primary" id="submit-challenge-btn">添加题目</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 添加模态框到页面
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('addChallengeModal'));
        modal.show();
        
        // 添加提交事件
        document.getElementById('submit-challenge-btn').addEventListener('click', () => {
            this.submitChallengeForm();
        });
        
        // 模态框关闭时清理
        document.getElementById('addChallengeModal').addEventListener('hidden.bs.modal', () => {
            document.getElementById('addChallengeModal').remove();
        });
    },

    // 提交题目表单
    async submitChallengeForm() {
        const form = document.getElementById('add-challenge-form');
        const formData = new FormData(form);
        
        // 获取提交按钮并禁用，防止重复提交
        const submitBtn = document.getElementById('submit-challenge-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 添加中...';
        submitBtn.disabled = true;
        
        const challengeData = {
            title: formData.get('title').trim(),
            description: formData.get('description').trim(),
            flag: formData.get('flag').trim(),
            points: parseInt(formData.get('points')),
            difficulty: formData.get('difficulty'),
            category_id: parseInt(formData.get('category_id')),
            is_hidden: formData.get('is_hidden') === 'on'
        };
        
        // 验证必填字段
        if (!challengeData.title || !challengeData.description || !challengeData.flag) {
            Utils.showAlert('请填写所有必填字段!', 'warning');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            return;
        }
        
        // 处理提示
        const hintsText = formData.get('hints');
        if (hintsText && hintsText.trim()) {
            challengeData.hints = hintsText.split('\n')
                .map(hint => hint.trim())
                .filter(hint => hint.length > 0);
        }
        
        console.log('提交题目数据:', challengeData);
        
        try {
            const response = await Utils.apiRequest('/challenges', {
                method: 'POST',
                body: JSON.stringify(challengeData)
            });
            
            console.log('创建题目响应:', response);
            
            Utils.showAlert('题目添加成功!', 'success');
            
            // 延迟关闭模态框，确保用户看到成功消息
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addChallengeModal'));
                if (modal) {
                    modal.hide();
                }
            }, 1000);
            
            // 延迟刷新数据，避免网络竞争
            setTimeout(() => {
                this.loadAdminData();
            }, 1500);
            
        } catch (error) {
            console.error('添加题目失败:', error);
            Utils.showAlert('添加题目失败: ' + (error.message || '网络错误'), 'danger');
        } finally {
            // 恢复按钮状态
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    },
    
    // 显示添加分类模态框
    showAddCategoryModal() {
        const name = prompt("请输入分类名称:");
        if (!name) return;
        
        const description = prompt("请输入分类描述:");
        
        this.addCategory(name, description);
    },
    
    // 添加分类
    async addCategory(name, description) {
        try {
            await Utils.apiRequest('/admin/categories', {
                method: 'POST',
                body: JSON.stringify({
                    name: name,
                    description: description
                })
            });
            
            Utils.showAlert('分类添加成功!', 'success');
            this.loadAdminData();
        } catch (error) {
            Utils.showAlert('添加分类失败: ' + error.message, 'danger');
        }
    },
    
    // 编辑题目
    async editChallenge(challengeId) {
        try {
            // 获取题目详情
            const data = await Utils.apiRequest(`/challenges/${challengeId}`);
            const challenge = data.challenge;
            
            // 创建编辑模态框
            const modalHTML = `
                <div class="modal fade" id="editChallengeModal" tabindex="-1">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">编辑题目</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <form id="edit-challenge-form">
                                    <div class="mb-3">
                                        <label class="form-label">标题 <span class="text-danger">*</span></label>
                                        <input type="text" class="form-control" name="title" value="${challenge.title}" required>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">描述 <span class="text-danger">*</span></label>
                                        <textarea class="form-control" name="description" rows="4" required>${challenge.description}</textarea>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Flag <span class="text-danger">*</span></label>
                                        <input type="text" class="form-control" name="flag" value="${challenge.flag}" required>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">分数 <span class="text-danger">*</span></label>
                                                <input type="number" class="form-control" name="points" value="${challenge.points}" min="1" required>
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="mb-3">
                                                <label class="form-label">难度 <span class="text-danger">*</span></label>
                                                <select class="form-select" name="difficulty" required>
                                                    <option value="easy" ${challenge.difficulty === 'easy' ? 'selected' : ''}>简单</option>
                                                    <option value="medium" ${challenge.difficulty === 'medium' ? 'selected' : ''}>中等</option>
                                                    <option value="hard" ${challenge.difficulty === 'hard' ? 'selected' : ''}>困难</option>
                                                    <option value="expert" ${challenge.difficulty === 'expert' ? 'selected' : ''}>专家</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">分类 <span class="text-danger">*</span></label>
                                        <select class="form-select" name="category_id" required>
                                            <option value="1" ${challenge.category_id === 1 ? 'selected' : ''}>Web</option>
                                            <option value="2" ${challenge.category_id === 2 ? 'selected' : ''}>Pwn</option>
                                            <option value="3" ${challenge.category_id === 3 ? 'selected' : ''}>Reverse</option>
                                            <option value="4" ${challenge.category_id === 4 ? 'selected' : ''}>Crypto</option>
                                            <option value="5" ${challenge.category_id === 5 ? 'selected' : ''}>Misc</option>
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">提示 (每行一个)</label>
                                        <textarea class="form-control" name="hints" rows="3" placeholder="每行输入一个提示">${challenge.hints ? challenge.hints.join('\n') : ''}</textarea>
                                    </div>
                                    <div class="form-check mb-3">
                                        <input class="form-check-input" type="checkbox" name="is_hidden" ${challenge.is_hidden ? 'checked' : ''}>
                                        <label class="form-check-label">隐藏题目</label>
                                    </div>
                                </form>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                <button type="button" class="btn btn-primary" id="update-challenge-btn">更新题目</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // 添加模态框到页面
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            
            // 显示模态框
            const modal = new bootstrap.Modal(document.getElementById('editChallengeModal'));
            modal.show();
            
            // 添加更新事件
            document.getElementById('update-challenge-btn').addEventListener('click', async () => {
                await this.updateChallengeForm(challengeId);
            });
            
            // 模态框关闭时清理
            document.getElementById('editChallengeModal').addEventListener('hidden.bs.modal', () => {
                document.getElementById('editChallengeModal').remove();
            });
            
        } catch (error) {
            Utils.showAlert('获取题目详情失败: ' + error.message, 'danger');
        }
    },

    // 更新题目表单
    async updateChallengeForm(challengeId) {
        const form = document.getElementById('edit-challenge-form');
        const formData = new FormData(form);
        
        // 获取提交按钮并禁用
        const submitBtn = document.getElementById('update-challenge-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 更新中...';
        submitBtn.disabled = true;
        
        const challengeData = {
            title: formData.get('title'),
            description: formData.get('description'),
            flag: formData.get('flag'),
            points: parseInt(formData.get('points')),
            difficulty: formData.get('difficulty'),
            category_id: parseInt(formData.get('category_id')),
            is_hidden: formData.get('is_hidden') === 'on'
        };
        
        // 处理提示
        const hintsText = formData.get('hints');
        if (hintsText.trim()) {
            challengeData.hints = hintsText.split('\n')
                .map(hint => hint.trim())
                .filter(hint => hint.length > 0);
        }
        
        try {
            await Utils.apiRequest(`/challenges/${challengeId}`, {
                method: 'PUT',
                body: JSON.stringify(challengeData)
            });
            
            Utils.showAlert('题目更新成功!', 'success');
            
            // 关闭模态框并刷新数据
            bootstrap.Modal.getInstance(document.getElementById('editChallengeModal')).hide();
            this.loadAdminData();
            
        } catch (error) {
            Utils.showAlert('更新题目失败: ' + error.message, 'danger');
        } finally {
            // 恢复按钮状态
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    },
    
    // 删除题目
    async deleteChallenge(challengeId) {
        if (!confirm('确定要删除这个题目吗？此操作不可逆！')) {
            return;
        }
        
        try {
            await Utils.apiRequest(`/challenges/${challengeId}`, {
                method: 'DELETE'
            });
            
            Utils.showAlert('题目删除成功!', 'success');
            this.loadAdminData();
        } catch (error) {
            Utils.showAlert('删除题目失败: ' + error.message, 'danger');
        }
    },
    
    // 切换用户管理员状态
    async toggleUserAdmin(userId, makeAdmin) {
        try {
            await Utils.apiRequest(`/admin/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_admin: makeAdmin
                })
            });
            
            Utils.showAlert(`用户${makeAdmin ? '设为' : '取消'}管理员成功!`, 'success');
            this.loadAdminData();
        } catch (error) {
            Utils.showAlert('操作失败: ' + error.message, 'danger');
        }
    },
    
    // 编辑分类
    editCategory(categoryId) {
        Utils.showAlert(`编辑分类 ID: ${categoryId}`, 'info');
        // 实际实现中应该打开编辑模态框
    },
    
    // 删除分类
    async deleteCategory(categoryId) {
        if (!confirm('确定要删除这个分类吗？此操作不可逆！')) {
            return;
        }
        
        try {
            await Utils.apiRequest(`/admin/categories/${categoryId}`, {
                method: 'DELETE'
            });
            
            Utils.showAlert('分类删除成功!', 'success');
            this.loadAdminData();
        } catch (error) {
            Utils.showAlert('删除分类失败: ' + error.message, 'danger');
        }
    },
    
    // 更新题目分数
    async updateChallengeScores() {
        try {
            await Utils.apiRequest('/admin/update-scores', {
                method: 'POST'
            });
            
            Utils.showAlert('题目分数更新成功!', 'success');
        } catch (error) {
            Utils.showAlert('更新分数失败: ' + error.message, 'danger');
        }
    },
    
    // 导出平台数据
    async exportPlatformData() {
        try {
            const data = await Utils.apiRequest('/admin/export-data');
            
            // 创建下载链接
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ctf_export_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            Utils.showAlert('数据导出成功!', 'success');
        } catch (error) {
            Utils.showAlert('导出数据失败: ' + error.message, 'danger');
        }
    },
    
    // 清除缓存
    async clearCache() {
        try {
            // 这里可以调用后端API清除缓存
            // 暂时使用前端本地存储清除作为示例
            localStorage.removeItem('ctf_cache_challenges');
            localStorage.removeItem('ctf_cache_leaderboard');
            
            Utils.showAlert('缓存清除成功!', 'success');
        } catch (error) {
            Utils.showAlert('清除缓存失败: ' + error.message, 'danger');
        }
    }
};