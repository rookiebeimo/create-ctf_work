// 题目相关功能
const Challenges = {
    currentChallenges: [],
    currentChallenge: null,
    
    // 初始化
    init() {
        // 返回题目列表按钮
        document.getElementById('back-to-challenges').addEventListener('click', () => {
            Utils.showPage('challenges-page');
        });
        
        // 分类筛选
        document.querySelectorAll('[data-category]').forEach(button => {
            button.addEventListener('click', (e) => {
                const category = e.target.getAttribute('data-category');
                this.filterChallenges(category);
                
                // 更新按钮状态
                document.querySelectorAll('[data-category]').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
            });
        });
        
        // 提交Flag表单
        document.getElementById('submit-flag-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitFlag();
        });
    },
    
    // 加载题目列表
    async loadChallenges() {
        try {
            const data = await Utils.apiRequest('/challenges');
            this.currentChallenges = data.challenges;
            this.displayChallenges(this.currentChallenges);
        } catch (error) {
            console.error('加载题目失败:', error);
        }
    },
    
    // 显示题目列表
    displayChallenges(challenges) {
        const challengesList = document.getElementById('challenges-list');
        
        if (challenges.length === 0) {
            challengesList.innerHTML = '<div class="col-12 text-center"><p>暂无题目</p></div>';
            return;
        }
        
        challengesList.innerHTML = challenges.map(challenge => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card challenge-card h-100" data-challenge-id="${challenge.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title">${challenge.title}</h5>
                            <span class="badge ${Utils.getDifficultyClass(challenge.difficulty)}">
                                ${Utils.getDifficultyText(challenge.difficulty)}
                            </span>
                        </div>
                        <p class="card-text text-muted small">${challenge.description.substring(0, 100)}...</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="badge bg-primary">${challenge.category}</span>
                            <span class="badge bg-success">${challenge.points} 分</span>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">
                                <i class="fas fa-users"></i> ${challenge.solved_count} 人解决
                                ${challenge.is_solved ? '<span class="badge bg-success ms-2">已解决</span>' : ''}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        // 添加点击事件
        document.querySelectorAll('.challenge-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const challengeId = card.getAttribute('data-challenge-id');
                this.showChallengeDetail(challengeId);
            });
        });
    },
    
    // 筛选题目
    filterChallenges(category) {
        if (category === 'all') {
            this.displayChallenges(this.currentChallenges);
        } else {
            const filtered = this.currentChallenges.filter(challenge => 
                challenge.category === category
            );
            this.displayChallenges(filtered);
        }
    },
    
    // 显示题目详情
    async showChallengeDetail(challengeId) {
        try {
            const data = await Utils.apiRequest(`/challenges/${challengeId}`);
            this.currentChallenge = data.challenge;
            this.displayChallengeDetail(this.currentChallenge);
            Utils.showPage('challenge-detail-page');
        } catch (error) {
            console.error('加载题目详情失败:', error);
        }
    },
    
    // 显示题目详情
    displayChallengeDetail(challenge) {
        document.getElementById('challenge-title').textContent = challenge.title;
        document.getElementById('challenge-category').textContent = challenge.category;
        document.getElementById('challenge-points').textContent = `${challenge.points} 分`;
        document.getElementById('challenge-description').innerHTML = 
            `<p>${challenge.description.replace(/\n/g, '<br>')}</p>`;
        
        // 显示提示（如果有）
        const hintsContainer = document.getElementById('challenge-hints');
        const hintsList = document.getElementById('hints-list');
        
        if (challenge.hints && challenge.hints.length > 0) {
            hintsList.innerHTML = challenge.hints.map(hint => `<li>${hint}</li>`).join('');
            hintsContainer.style.display = 'block';
        } else {
            hintsContainer.style.display = 'none';
        }
        
        // 清空提交结果和输入框
        document.getElementById('submission-result').style.display = 'none';
        document.getElementById('flag-input').value = '';
    },
    
    // 提交Flag
    async submitFlag() {
        if (!this.currentChallenge) return;
        
        const flag = document.getElementById('flag-input').value.trim();
        if (!flag) {
            Utils.showAlert('请输入Flag', 'warning');
            return;
        }
        
        try {
            const data = await Utils.apiRequest(`/challenges/${this.currentChallenge.id}/submit`, {
                method: 'POST',
                body: JSON.stringify({ flag })
            });
            
            const resultDiv = document.getElementById('submission-result');
            resultDiv.style.display = 'block';
            
            if (data.is_correct) {
                resultDiv.innerHTML = `
                    <div class="alert alert-success">
                        <i class="fas fa-check-circle"></i> ${data.message}
                    </div>
                `;
                // 刷新题目列表和用户信息
                this.loadChallenges();
                Auth.loadUserProfile();
            } else {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-times-circle"></i> ${data.message}
                    </div>
                `;
            }
        } catch (error) {
            console.error('提交Flag失败:', error);
        }
    }
};