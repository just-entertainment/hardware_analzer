const App = {
    init() {
        Navigation.init();
        Search.init();
        Visualization.init();
        Config.init();
        Navigation.showSection('search');
    }
};
const Detail = {
    show(type, id) {
        const modal = document.getElementById('detailModal');
        const title = document.getElementById('detailTitle');
        const content = document.getElementById('detailContent');

        if (!modal || !title || !content) {
            console.error('弹窗元素缺失:', { modal, title, content });
            return;
        }

        modal.classList.add('active');
        content.innerHTML = '<div class="loading-spinner">加载中...</div>';

        fetch(`/api/detail/${type}/${id}/`)
            .then(res => {
                if (!res.ok) {
                    return res.json().then(data => {
                        throw new Error(data.error || `加载失败: ${res.status}`);
                    });
                }
                return res.json();
            })
            .then(data => {
                console.log('API 响应:', data);
                title.textContent = data.title;

                // 构建组件特定字段
                let specificFields = '';
                if (type === 'cpu') {
                    specificFields = `
                        <p><strong>系列:</strong> ${data.cpu_series || '未知'}</p>
                        <p><strong>核心数:</strong> ${data.core_count || '未知'}</p>
                        <p><strong>线程数:</strong> ${data.thread_count || '未知'}</p>
                        <p><strong>主频:</strong> ${data.cpu_frequency || '未知'}</p>
                    `;
                } else if (type === 'gpu') {
                    specificFields = `
                        <p><strong>芯片厂商:</strong> ${data.chip_manufacturer || '未知'}</p>
                        <p><strong>显存容量:</strong> ${data.memory_size || '未知'}</p>
                        <p><strong>核心频率:</strong> ${data.core_clock || '未知'}</p>
                    `;
                } else if (type === 'motherboard') {
                    specificFields = `
                        <p><strong>主芯片组:</strong> ${data.chipset || '未知'}</p>
                        <p><strong>内存类型:</strong> ${data.memory_type || '未知'}</p>
                        <p><strong>板型:</strong> ${data.form_factor || '未知'}</p>
                    `;
                } else if (type === 'ram') {
                    specificFields = `
                        <p><strong>内存类型:</strong> ${data.memory_type || '未知'}</p>
                        <p><strong>容量:</strong> ${data.capacity || '未知'}</p>
                        <p><strong>频率:</strong> ${data.frequency || '未知'}</p>
                    `;
                } else if (type === 'ssd') {
                    specificFields = `
                        <p><strong>容量:</strong> ${data.capacity || '未知'}</p>
                        <p><strong>接口类型:</strong> ${data.interface_type || '未知'}</p>
                        <p><strong>读取速度:</strong> ${data.read_speed || '未知'}</p>
                    `;
                } else if (type === 'cooler') {
                    specificFields = `
                        <p><strong>散热器类型:</strong> ${data.cooler_type || '未知'}</p>
                        <p><strong>风扇尺寸:</strong> ${data.fan_size || '未知'}</p>
                        <p><strong>兼容性:</strong> ${data.compatibility || '未知'}</p>
                    `;
                } else if (type === 'power_supply') {
                    specificFields = `
                        <p><strong>功率:</strong> ${data.wattage || '未知'}</p>
                        <p><strong>效率认证:</strong> ${data.efficiency_rating || '未知'}</p>
                        <p><strong>模组化:</strong> ${data.modular || '未知'}</p>
                    `;
                } else if (type === 'chassis') {
                    specificFields = `
                        <p><strong>板型:</strong> ${data.form_factor || '未知'}</p>
                        <p><strong>最大显卡长度:</strong> ${data.max_gpu_length || '未知'}</p>
                        <p><strong>风扇位:</strong> ${data.fan_slots || '未知'}</p>
                    `;
                }

                content.innerHTML = `
                    <img src="${data.product_image}" alt="${data.title}" class="product-image">
                    <div class="price-info">
                        <span>参考价: ¥${data.reference_price}</span>
                        <span>京东价: ¥${data.jd_price}</span>
                    </div>
                    <p>京东链接: <a href="${data.jd_link || '#'}" target="_blank">${data.jd_link ? '点击购买' : '暂无链接'}</a></p>
                    <div class="specs-list">
                        <h3>规格参数</h3>
                        ${specificFields}
                        <p>${data.product_parameters.replace(/\n/g, '<br>') || '暂无详细参数'}</p>
                    </div>
                    <div class="price-history">
                        <h3>历史价格趋势</h3>
                        <canvas id="priceChart" height="200"></canvas>
                        <p class="price-note">${
                            data.price_history.length === 91 && data.price_history.every(item => item.price === data.price_history[0].price)
                            ? '注：无历史价格记录，显示当前参考价格'
                            : ''
                        }</p>
                    </div>
                `;

                const priceHistory = data.price_history || [];
                console.log('价格历史:', priceHistory);
                const ctx = document.getElementById('priceChart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: priceHistory.map(item => item.date),
                        datasets: [{
                            label: '价格 (¥)',
                            data: priceHistory.map(item => item.price),
                            borderColor: '#1DA1F2',
                            backgroundColor: 'rgba(29, 161, 242, 0.1)',
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4,
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            x: {
                                title: { display: true, text: '日期' },
                                ticks: { maxTicksLimit: 10 }
                            },
                            y: {
                                title: { display: true, text: '价格 (¥)' },
                                beginAtZero: false
                            }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: ctx => `¥${ctx.parsed.y.toFixed(2)}`
                                }
                            }
                        }
                    }
                });
            })
            .catch(err => {
                console.error('加载详情失败:', err);
                content.innerHTML = `<div class="error">加载失败：${err.message || '请稍后重试'}</div>`;
            });
    },
    close() {
        const modal = document.getElementById('detailModal');
        if (modal) modal.classList.remove('active');
    }
};
const Favorites = {
    load() {
        const resultDiv = document.getElementById('favoritesResult');
        if (!resultDiv) {
            console.error('favoritesResult 元素缺失');
            return;
        }
        resultDiv.innerHTML = '<div class="loading-spinner">加载中...</div>';
        fetch('/api/favorites/')
            .then(res => {
                if (!res.ok) throw new Error('加载失败');
                return res.json();
            })
            .then(data => {
                if (data.results.length > 0) {
                    resultDiv.innerHTML = data.results.map(item => `
                        <div class="favorite-item" data-type="${item.type}" data-id="${item.id}"
                             onclick="Detail.show('${item.type}', ${item.id})">
                            <div class="title">${item.title}</div>
                            <div class="info">
                                <span>参考价: ¥${item.reference_price}</span>
                                <span>京东价: ¥${item.jd_price}</span>
                            </div>
                            <button class="delete-btn" onclick="Favorites.delete(this, '${item.type}', ${item.id}); event.stopPropagation()">
                                删除
                            </button>
                        </div>
                    `).join('');
                } else {
                    resultDiv.innerHTML = '<div class="no-results">暂无收藏</div>';
                }
            })
            .catch(err => {
                console.error('加载收藏失败:', err);
                resultDiv.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
            });
    },
    delete(btn, type, id) {
    if (confirm('确定删除此收藏？')) {
        fetch('/api/favorite/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(), // 确保有此函数获取 CSRF 令牌
            },
            body: JSON.stringify({ type, id }),
        })
            .then(res => {
                if (!res.ok) throw new Error(`删除失败: ${res.status}`);
                return res.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    btn.closest('.favorite-item').remove();
                    // 检查收藏列表是否为空
                    const resultDiv = document.getElementById('favoritesResult');
                    if (!resultDiv.querySelector('.favorite-item')) {
                        resultDiv.innerHTML = '<div class="no-results">暂无收藏</div>';
                    }
                }
            })
            .catch(err => {
                console.error('删除收藏失败:', err);
                alert('删除失败，请稍后重试');
            });
    }
}
};
const Navigation = {
    init() {
        // 初始化导航事件
        document.addEventListener('click', (event) => {
            const userProfile = document.querySelector('.user-profile');
            const userMenu = document.getElementById('userMenu');
            if (userProfile && userMenu && !userProfile.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.remove('active');
            }
        });
    },

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.querySelectorAll('.sidebar a').forEach(link => {
            link.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');
        document.querySelector(`a[onclick*="showSection('${sectionId}')"]`).classList.add('active');

        if (sectionId === 'favorites') {
            Favorites.load();
        } else if (sectionId === 'price') {
            Visualization.loadData();
        }
    },

    toggleUserMenu() {
        const userMenu = document.getElementById('userMenu');
        if (userMenu) {
            userMenu.classList.toggle('active');
        }
    }
};
const Search = {
    currentPage: 1,
    currentType: '',
    currentSort: '',

    init() {
        document.getElementById('componentType').addEventListener('change', () => {
            this.updateFilters();
            this.currentPage = 1;
        });
        document.querySelector('.search-bar button').addEventListener('click', () => this.searchComponent(1));
        document.getElementById('sortBy').addEventListener('change', () => this.searchComponent(1));
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchComponent(1);
        });
    },

    updateFilters() {
        const componentType = document.getElementById('componentType').value;
        this.currentType = componentType;
        const filterContainer = document.getElementById('dynamicFilters');
        filterContainer.innerHTML = '';
        if (!componentType) return;
        if (componentType === 'cpu') {
            filterContainer.innerHTML = `
                <select id="cpuBrand" class="filter-select">
                    <option value="">所有品牌</option>
                    <option value="intel">Intel</option>
                    <option value="amd">AMD</option>
                </select>
                <select id="cpuSeries" class="filter-select">
                    <option value="">所有系列</option>
                </select>
            `;
            document.getElementById('cpuBrand').addEventListener('change', function() {
                const brand = this.value;
                const seriesSelect = document.getElementById('cpuSeries');
                seriesSelect.innerHTML = '<option value="">所有系列</option>';
                if (!brand) return;
                fetch(`/api/get_cpu_series/?brand=${brand}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.series) {
                            data.series.forEach(series => {
                                const option = document.createElement('option');
                                option.value = series;
                                option.textContent = series;
                                seriesSelect.appendChild(option);
                            });
                        }
                    });
            });
        }
    },

    searchComponent(page) {
        this.currentPage = page;
        const query = document.getElementById('searchInput').value.trim();
        const componentType = document.getElementById('componentType').value;
        const sortValue = document.getElementById('sortBy').value;
        const resultDiv = document.getElementById('searchResult');
        const paginationDiv = document.getElementById('pagination');

        const params = new URLSearchParams();
        if (componentType) params.append('type', componentType);
        if (query) params.append('q', query);
        params.append('page', page);
        if (componentType === 'cpu') {
            const brand = document.getElementById('cpuBrand')?.value || '';
            const series = document.getElementById('cpuSeries')?.value || '';
            if (brand) params.append('brand', brand);
            if (series) params.append('series', series);
        }
        if (sortValue) {
            const [sortBy, sortOrder] = sortValue.split('_');
            params.append('sort_by', sortBy);
            params.append('sort_order', sortOrder);
        }

        resultDiv.innerHTML = '<div class="loading-spinner"></div> 搜索中...';
        fetch(`/api/search/?${params.toString()}`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP错误! 状态码: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `<div class="error">错误: ${data.error}</div>`;
                    return;
                }
                this.renderResults(data, resultDiv, paginationDiv);
            })
            .catch(error => {
                resultDiv.innerHTML = `<div class="error">搜索出错: ${error.message}</div>`;
                console.error('搜索错误:', error);
            });
    },

    renderResults(data, resultDiv, paginationDiv) {
    if (data.results.length > 0) {
        resultDiv.innerHTML = data.results.map(item => `
            <div class="post" data-type="${item.type}" data-id="${item.id}"
                 onclick="Detail.show('${item.type}', ${item.id})">
                <div class="title">${item.title}</div>
                <div class="info">
                    <span>参考价: ¥${item.reference_price}</span>
                    <span>京东价: ¥${item.jd_price}</span>
                </div>
                <!-- 收藏按钮，点击切换收藏状态 -->
                <button class="favorite-btn ${item.is_favorited ? 'favorited' : ''}"
                        data-type="${item.type}" data-id="${item.id}"
                        data-csrf="${data.csrf_token || ''}"
                        onclick="Search.toggleFavorite(this); event.stopPropagation()">
                    ${item.is_favorited ? '取消收藏' : '收藏'}
                </button>
            </div>
        `).join('');
    } else {
        resultDiv.innerHTML = '<div class="no-results">未找到符合条件的配件</div>';
    }
    this.renderPagination(data, paginationDiv);
},

    renderPagination(data, container) {
        container.innerHTML = '';
        if (data.pages > 1) {
            const pagination = document.createElement('div');
            pagination.className = 'pagination';
            if (data.has_previous) {
                const prevBtn = document.createElement('button');
                prevBtn.innerHTML = '« 上一页';
                prevBtn.addEventListener('click', () => this.searchComponent(data.current_page - 1));
                pagination.appendChild(prevBtn);
            }
            const pageInfo = document.createElement('span');
            pageInfo.textContent = `第 ${data.current_page} 页 / 共 ${data.pages} 页`;
            pagination.appendChild(pageInfo);
            if (data.has_next) {
                const nextBtn = document.createElement('button');
                nextBtn.innerHTML = '下一页 »';
                nextBtn.addEventListener('click', () => this.searchComponent(data.current_page + 1));
                pagination.appendChild(nextBtn);
            }
            container.appendChild(pagination);
        }
    },

    // 收藏切换函数
        toggleFavorite(btn) {
    const csrfToken = btn.dataset.csrf;
    if (!csrfToken) {
        alert('CSRF 令牌缺失，请刷新页面！');
        return;
    }
    const type = btn.dataset.type;
    const id = btn.dataset.id;
    const isFavorited = btn.classList.contains('favorited');

    fetch('/api/favorite/', {
        method: isFavorited ? 'DELETE' : 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ type, id }),
    })
        .then(res => {
            if (res.status === 401) {
                alert('会话过期，请重新登录！');
                window.location.href = '/accounts/login/';
                return null;
            }
            if (!res.ok) throw new Error(`请求失败: ${res.status}`);
            return res.json();
        })
        .then(data => {
            if (data && data.status === 'success') {
                btn.textContent = isFavorited ? '收藏' : '取消收藏';
                btn.classList.toggle('favorited');
                // 可选：如果在收藏页面，刷新收藏列表
                if (document.getElementById('favorites').classList.contains('active')) {
                    Favorites.load();
                }
            }
        })
        .catch(err => {
            console.error('收藏操作失败:', err);
            alert('操作失败，请稍后重试');
        });
}
};

const Visualization = {
    charts: {
        priceDistribution: null,
        averagePriceTrend: null,
        salesDistribution: null,
        priceCommentScatter: null,
        salesRanking: null
    },
    currentType: 'cpu',
    componentNames: {
        'cpu': 'CPU',
        'gpu': '显卡',
        'ram': '内存',
        'ssd': '固态硬盘',
        'motherboard': '主板',
        'cooler': '散热器',
        'power_supply': '电源',
        'chassis': '机箱'
    },

    init() {
        // 确保控件容器存在
        if (!document.querySelector('.viz-controls')) {
            console.error('Visualization controls container not found');
            return;
        }
        console.log('Visualization init');
        this.renderControls();
        this.loadData();
        this.bindEvents();
    },

    renderControls() {
        const controlsDiv = document.querySelector('.viz-controls');
        if (!controlsDiv) {
            console.error('Controls container not found');
            return;
        }
        // 动态生成选项，保持与 currentType 同步
        controlsDiv.innerHTML = `
            <select id="vizComponentType" class="filter-select">
                ${Object.entries(this.componentNames).map(([value, name]) => 
                    `<option value="${value}" ${value === this.currentType ? 'selected' : ''}>${name}</option>`
                ).join('')}
            </select>
            <button onclick="Visualization.loadData()">刷新数据</button>
        `;
    },

    bindEvents() {
        const select = document.getElementById('vizComponentType');
        if (!select) {
            console.error('Component type select not found');
            return;
        }
        // 防止重复绑定
        if (this.handleTypeChange) {
            select.removeEventListener('change', this.handleTypeChange);
        }
        this.handleTypeChange = (e) => {
            this.currentType = e.target.value;
            console.log(`Selected component type: ${this.currentType}`);
            this.loadData();
        };
        select.addEventListener('change', this.handleTypeChange);
        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => chart?.resize());
        });
    },

    loadData: debounce(async function() {
        console.log('Loading visualization data for type:', this.currentType);
        const chartIds = [
            'priceDistributionChart', 'averagePriceTrendChart',
            'salesDistributionChart', 'priceCommentScatterChart', 'salesRankingChart'
        ];
        const statsSummary = document.getElementById('statsSummary');

        if (chartIds.some(id => !document.getElementById(id)) || !statsSummary) {
            console.error('图表元素缺失:', { chartIds, statsSummary });
            return;
        }

        chartIds.forEach(id => document.getElementById(id).parentElement.classList.add('chart-loading'));
        statsSummary.innerHTML = '<div class="loading-spinner"></div>加载中...';

        try {
            // 添加请求超时
            const timeout = (promise, time) => Promise.race([
                promise,
                new Promise((_, reject) => setTimeout(() => reject(new Error('请求超时')), time))
            ]);
            const [statsResponse, trendResponse] = await Promise.all([
                timeout(fetch(`/api/price_stats/?type=${this.currentType}`), 5000),
                timeout(fetch(`/api/average_price_trend/?type=${this.currentType}`), 5000)
            ]);

            if (!statsResponse.ok || !trendResponse.ok) {
                const errorData = await (statsResponse.ok ? trendResponse : statsResponse).json().catch(() => ({}));
                throw new Error(`数据加载错误: ${errorData.error || '网络错误'}`);
            }

            const statsData = await statsResponse.json();
            const trendData = await trendResponse.json();

            // 验证数据
            if (!statsData.price_distribution && !statsData.sales_distribution &&
                !statsData.price_comment_scatter && !statsData.sales_ranking) {
                throw new Error('无有效统计数据');
            }

            chartIds.forEach(id => document.getElementById(id).parentElement.classList.remove('chart-loading'));

            this.renderPriceDistributionChart(statsData);
            this.renderAveragePriceTrendChart(trendData);
            this.renderSalesDistributionChart(statsData);
            this.renderPriceCommentScatterChart(statsData);
            this.renderSalesRankingChart(statsData);
            this.renderStatsSummary(statsData);
        } catch (error) {
            console.error('可视化数据加载失败:', error);
            chartIds.forEach(id => {
                const container = document.getElementById(id).parentElement;
                container.innerHTML = `<div class="chart-error">${error.message}</div><canvas id="${id}"></canvas>`;
            });
            statsSummary.innerHTML = `<div class="error">${error.message}</div>`;
        }
    }, 300),

    renderPriceDistributionChart(statsData) {
        const ctx = document.getElementById('priceDistributionChart')?.getContext('2d');
        if (!ctx) {
            console.error('Price distribution canvas not found');
            return;
        }

        if (this.charts.priceDistribution) this.charts.priceDistribution.destroy();

        const priceData = (statsData.price_distribution || []).filter(x => x.count >= 0);
        if (!priceData.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="no-data">${statsData.message || '暂无价格分布数据'}</div>`;
            return;
        }

        this.charts.priceDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: priceData.map(x => x.range),
                datasets: [{
                    label: '产品数量',
                    data: priceData.map(x => x.count),
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: `${this.getComponentName(this.currentType)} 价格分布`, font: { size: 16 } },
                    tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} 款产品` } },
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: '产品数量' }, ticks: { precision: 0 } },
                    x: {
                        title: { display: true, text: '价格区间 (¥)' },
                        ticks: { autoSkip: true, maxTicksLimit: 10, maxRotation: 45, minRotation: 0 }
                    }
                }
            }
        });
    },

    renderAveragePriceTrendChart(trendData) {
        const ctx = document.getElementById('averagePriceTrendChart')?.getContext('2d');
        if (!ctx) {
            console.error('Average price trend canvas not found');
            return;
        }

        if (this.charts.averagePriceTrend) this.charts.averagePriceTrend.destroy();

        const data = (trendData.data || []).filter(x => x.avg_price != null && x.avg_price >= 0);
        if (!data.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="no-data">${trendData.message || '暂无价格趋势数据'}</div>`;
            return;
        }

        this.charts.averagePriceTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(x => x.date),
                datasets: [{
                    label: '平均价格',
                    data: data.map(x => x.avg_price),
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: `${this.getComponentName(this.currentType)} 平均价格趋势`, font: { size: 16 } },
                    tooltip: { callbacks: { label: ctx => `¥${ctx.parsed.y.toFixed(2)}` } },
                    legend: { display: false }
                },
                scales: {
                    x: { title: { display: true, text: '日期' }, ticks: { maxTicksLimit: 10 } },
                    y: {
                        title: { display: true, text: '平均价格 (¥)' },
                        beginAtZero: false,
                        suggestedMin: Math.max(0, Math.min(...data.map(x => x.avg_price)) - 50),
                        suggestedMax: Math.max(...data.map(x => x.avg_price)) + 50
                    }
                }
            }
        });
    },

    renderSalesDistributionChart(statsData) {
        const ctx = document.getElementById('salesDistributionChart')?.getContext('2d');
        if (!ctx) {
            console.error('Sales distribution canvas not found');
            return;
        }

        if (this.charts.salesDistribution) this.charts.salesDistribution.destroy();

        const salesData = (statsData.sales_distribution || []).filter(x => x.count >= 0);
        if (!salesData.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="no-data">${statsData.message || '暂无销量分布数据'}</div>`;
            return;
        }

        this.charts.salesDistribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: salesData.map(x => x.range.replace(/(\d+)-(\d+)/, (m, a, b) => `${(a/1000).toFixed(0)}k-${(b/1000).toFixed(0)}k`)),
                datasets: [{
                    label: '产品数量',
                    data: salesData.map(x => x.count),
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: `${this.getComponentName(this.currentType)} 销量分布`, font: { size: 16 } },
                    tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} 款产品` } },
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: '产品数量' }, ticks: { precision: 0 } },
                    x: {
                        title: { display: true, text: '评论数区间' },
                        ticks: { autoSkip: true, maxTicksLimit: 10, maxRotation: 45, minRotation: 0 }
                    }
                }
            }
        });
    },

    renderPriceCommentScatterChart(statsData) {
        const ctx = document.getElementById('priceCommentScatterChart')?.getContext('2d');
        if (!ctx) {
            console.error('Price vs comment scatter canvas not found');
            return;
        }

        if (this.charts.priceCommentScatter) this.charts.priceCommentScatter.destroy();

        const scatterData = (statsData.price_comment_scatter || []).filter(x => x.price >= 0 && x.comment_count >= 0).slice(0, 1000);
        if (!scatterData.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="no-data">${statsData.message || '暂无价格与销量数据'}</div>`;
            return;
        }

        this.charts.priceCommentScatter = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: '价格 vs 销量',
                    data: scatterData.map(item => ({ x: item.price, y: item.comment_count })),
                    backgroundColor: 'rgba(255, 159, 64, 0.7)',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: `${this.getComponentName(this.currentType)} 价格与销量关系`, font: { size: 16 } },
                    tooltip: { callbacks: { label: ctx => `价格: ¥${ctx.raw.x.toFixed(2)}, 销量: ${ctx.raw.y}` } },
                    legend: { display: false }
                },
                scales: {
                    x: { title: { display: true, text: '价格 (¥)' } },
                    y: { title: { display: true, text: '评论数' }, beginAtZero: true }
                }
            }
        });
    },

    renderSalesRankingChart(statsData) {
        const ctx = document.getElementById('salesRankingChart')?.getContext('2d');
        if (!ctx) {
            console.error('Sales ranking canvas not found');
            return;
        }

        if (this.charts.salesRanking) this.charts.salesRanking.destroy();

        const rankingData = (statsData.sales_ranking || []).filter(x => x.comment_count >= 0);
        if (!rankingData.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="no-data">${statsData.message || '暂无销量排名数据'}</div>`;
            return;
        }

        this.charts.salesRanking = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: rankingData.map(x => x.title.length > 20 ? x.title.substring(0, 17) + '...' : x.title),
                datasets: [{
                    label: '销量 (评论数)',
                    data: rankingData.map(x => x.comment_count),
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: `${this.getComponentName(this.currentType)} 销量排名 (Top 10)`, font: { size: 16 } },
                    tooltip: { callbacks: { label: ctx => `${ctx.parsed.y} 条评论` } },
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, title: { display: true, text: '评论数' }, ticks: { precision: 0 } },
                    x: {
                        title: { display: true, text: '产品' },
                        ticks: { autoSkip: true, maxTicksLimit: 10, maxRotation: 45, minRotation: 0 }
                    }
                }
            }
        });
    },

    renderStatsSummary(statsData) {
        const statsSummary = document.getElementById('statsSummary');
        if (!statsSummary) {
            console.error('Stats summary container not found');
            return;
        }

        const formatNumber = (num) => num != null ? num.toFixed(2) : '未知';
        if (!statsData || statsData.total_count === 0) {
            statsSummary.innerHTML = `<div class="no-data">${statsData?.message || '暂无统计数据'}</div>`;
            return;
        }

        const stats = [
            { label: '总产品数', value: statsData.total_count },
            { label: '中位数价格 (¥)', value: formatNumber(statsData.median_price) },
            { label: '平均价格 (¥)', value: formatNumber(statsData.avg_price) },
            { label: '价格标准差 (¥)', value: formatNumber(statsData.std_dev_price) },
            { label: '总评论数', value: statsData.total_comments || 0 },
            { label: '平均评论数', value: formatNumber(statsData.avg_comments) },
            { label: '最大评论数', value: statsData.max_comments || 0 }
        ];

        statsSummary.innerHTML = `
            <h3>价格与销量统计</h3>
            ${stats.map(s => `<p>${s.label}: ${s.value}</p>`).join('')}
        `;
    },

    getComponentName(type) {
        return this.componentNames[type] || type;
    }
};


document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('price')?.classList.contains('active')) {
        Visualization.init();
    }
});



document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('price')?.classList.contains('active')) {
        Visualization.init();
    }
});



document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('price')?.classList.contains('active')) {
        Visualization.init();
    }
});

// 防抖函数


// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}


// 收藏列表模块

function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]')?.content ||
                  document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    return token || '';
}

document.addEventListener('DOMContentLoaded', () => {
    App.init();
    document.querySelector('.modal .close').addEventListener('click', () => Detail.close());
    document.querySelector('.modal').addEventListener('click', (e) => {
        if (e.target === document.querySelector('.modal')) Detail.close();
    });
});

// 暴露全局对象
window.Navigation = Navigation;
window.Search = Search;
window.Favorites = Favorites;
window.Detail = Detail;
window.generateConfig = generateConfig;
window.showDetail = Detail.show;
window.closeModal = Detail.close;
window.generateConfig = Config.generateConfig;

document.addEventListener('DOMContentLoaded', () => {
    const favoritesSection = document.getElementById('favorites');
    if (favoritesSection && favoritesSection.classList.contains('active')) {
        Favorites.load();
    }
});