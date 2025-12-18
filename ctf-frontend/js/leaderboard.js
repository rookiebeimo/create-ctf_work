// 排行榜相关功能
const Leaderboard = {
    // 初始化
    init() {
        // 分类选择变化事件
        document.getElementById('category-select').addEventListener('change', (e) => {
            this.loadCategoryLeaderboard(e.target.value);
        });
    },
    
    // 加载全球排行榜
    async loadGlobalLeaderboard() {
        try {
            const data = await Utils.apiRequest('/leaderboard');
            this.displayGlobalLeaderboard(data.leaderboard);
        } catch (error) {
            console.error('加载全球排行榜失败:', error);
        }
    },
    
    // 显示全球排行榜
    displayGlobalLeaderboard(leaderboard) {
        const tbody = document.getElementById('global-leaderboard-body');
        
        if (leaderboard.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = leaderboard.map(user => `
            <tr class="${user.rank <= 3 ? `user-rank-${user.rank}` : ''}">
                <td>${user.rank}</td>
                <td>${user.username}</td>
                <td>${user.score}</td>
                <td>${user.solved_count}</td>
                <td>${user.last_solve ? Utils.formatDate(user.last_solve) : '暂无'}</td>
            </tr>
        `).join('');
    },
    
    // 加载分类排行榜
    async loadCategoryLeaderboard(categoryId) {
        try {
            const data = await Utils.apiRequest(`/leaderboard/category/${categoryId}`);
            this.displayCategoryLeaderboard(data.leaderboard);
        } catch (error) {
            console.error('加载分类排行榜失败:', error);
        }
    },
    
    // 显示分类排行榜
    displayCategoryLeaderboard(leaderboard) {
        const tbody = document.getElementById('category-leaderboard-body');
        
        if (leaderboard.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">暂无数据</td></tr>';
            return;
        }
        
        tbody.innerHTML = leaderboard.map(user => `
            <tr class="${user.rank <= 3 ? `user-rank-${user.rank}` : ''}">
                <td>${user.rank}</td>
                <td>${user.username}</td>
                <td>${user.score}</td>
                <td>${user.solved_count}</td>
            </tr>
        `).join('');
    },
    
    // 加载分类选项
    async loadCategories() {
        try {
            const data = await Utils.apiRequest('/categories');
            this.populateCategorySelect(data.categories);
        } catch (error) {
            console.error('加载分类失败:', error);
        }
    },
    
    // 填充分类选择框
    populateCategorySelect(categories) {
        const select = document.getElementById('category-select');
        select.innerHTML = categories.map(category => 
            `<option value="${category.id}">${category.name}</option>`
        ).join('');
        
        // 默认加载第一个分类的排行榜
        if (categories.length > 0) {
            this.loadCategoryLeaderboard(categories[0].id);
        }
    }
};