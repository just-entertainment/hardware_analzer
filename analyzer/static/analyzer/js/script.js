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
                if (!res.ok) throw new Error(`加载失败: ${res.status}`);
                return res.json();
            })
            .then(data => {
                console.log('API 响应:', data);
                title.textContent = data.title;
                content.innerHTML = `
                    <img src="${data.product_image}" alt="${data.title}" class="product-image">
                    <div class="price-info">
                        <span>参考价: ¥${data.reference_price}</span>
                        <span>京东价: ¥${data.jd_price}</span>
                    </div>
                    <p>京东链接: <a href="${data.jd_link || '#'}" target="_blank">${data.jd_link ? '点击购买' : '暂无链接'}</a></p>
                    <div class="specs-list">
                        <p>${data.product_parameters.replace(/\n/g, '<br>')}</p>
                    </div>
                    <div class="price-history">
                        <h3>历史价格趋势</h3>
                        <canvas id="priceChart" height="200"></canvas>
                    </div>
                `;

                const priceHistory = data.price_history || [];
                console.log('价格历史:', priceHistory);
                if (priceHistory.length > 0) {
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
                } else {
                    document.querySelector('.price-history').innerHTML = '<p class="no-data">暂无历史价格</p>';
                }
            })
            .catch(err => {
                console.error('加载详情失败:', err);
                content.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
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
            fetch(`/api/favorites/${type}/${id}/`, { method: 'DELETE' })
                .then(res => {
                    if (!res.ok) throw new Error('删除失败');
                    btn.closest('.favorite-item').remove();
                })
                .catch(err => {
                    console.error('删除收藏失败:', err);
                    alert('删除失败，请稍后重试');
                });
        }
    }
};
const Navigation = {
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
    // 获取 CSRF 令牌
    const csrfToken = btn.dataset.csrf;
    if (!csrfToken) {
        alert('CSRF 令牌缺失，请刷新页面！');
        return;
    }
    const type = btn.dataset.type;
    const id = btn.dataset.id;
    const isFavorited = btn.classList.contains('favorited');
    // 发送 AJAX 请求，POST 添加收藏，DELETE 取消收藏
    fetch(isFavorited ? '/api/favorite/delete/' : '/api/favorite/', {
        method: isFavorited ? 'DELETE' : 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ type, id })
    })
    .then(res => {
        if (res.status === 401) {
            alert('会话过期，请重新登录！');
            window.location.href = '/accounts/login/';
            return null;
        }
        if (!res.ok) throw new Error('请求失败');
        return res.json();
    })
    .then(data => {
        if (data && data.status === 'success') {
            // 更新按钮状态
            btn.textContent = isFavorited ? '收藏' : '取消收藏';
            btn.classList.toggle('favorited');
        }
    })
    .catch(err => {
        console.error('收藏失败:', err);
        alert('操作失败，请稍后重试');
    });
}
};


// 详情弹窗模块
// 确保 DOM 加载完成
// 详情弹窗模块




const Config = {
     init() {
        console.log('Config initialized');
        // 初始化逻辑
    },

    async generateConfig() {
        const budget = document.getElementById('budgetInput').value;
        const usage = document.getElementById('usageSelect').value;
        const resultsDiv = document.getElementById('configResults');

        resultsDiv.innerHTML = '<div class="loading-spinner"></div> 生成中...';

        try {
            const response = await fetch(`/api/generate_configuration/?budget=${budget}&usage=${usage}`);
            const data = await response.json();

            if (data.error) {
                resultsDiv.innerHTML = `<div class="error">生成配置失败: ${data.error}</div>`;
                return;
            }

            // 渲染配置单
            const totalPrice = parseFloat(data.total_price);
            resultsDiv.innerHTML = `
                <div class="config-card">
                    <div class="config-header">
                        <span class="config-title">推荐配置</span>
                        <span class="config-price">总价: ¥${data.total_price.toFixed(2)}</span>
                    </div>
                    <div class="config-items">
                        ${data.configuration.map(item => `
                            <div class="config-item">
                                <div class="item-name">${item.type.toUpperCase()}: ${item.title}</div>
                                <div class="item-price">¥${item.price.toFixed(2)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">生成配置失败: ${error.message}</div>`;
        }
    }
};

const Visualization = {
    charts: {},
    currentType: 'cpu',

    init() {
        this.renderControls();
        this.loadData();
        this.bindEvents();
    },

    renderControls() {
        const controlsDiv = document.querySelector('.viz-controls');
        controlsDiv.innerHTML = `
            <select id="vizComponentType" class="filter-select">
                <option value="cpu">CPU</option>
                <option value="gpu">显卡</option>
                <option value="ram">内存</option>
                <option value="ssd">固态硬盘</option>
                <option value="motherboard">主板</option>
                <option value="cooler">散热器</option>
                <option value="power_supply">电源</option>
                <option value="case">机箱</option>
            </select>
            <button onclick="Visualization.loadData()">刷新数据</button>
        `;
    },

    bindEvents() {
        document.getElementById('vizComponentType').addEventListener('change', (e) => {
            this.currentType = e.target.value;
            this.loadData();
        });
        window.addEventListener('resize', () => {
            Object.values(this.charts).forEach(chart => chart?.resize());
        });
    },

    loadData: debounce(async function() {
        const priceChartCanvas = document.getElementById('priceDistributionChart');
        const trendChartCanvas = document.getElementById('averagePriceTrendChart');
        const statsSummary = document.getElementById('statsSummary');

        if (!priceChartCanvas || !trendChartCanvas || !statsSummary) return;

        priceChartCanvas.parentElement.classList.add('chart-loading');
        trendChartCanvas.parentElement.classList.add('chart-loading');
        statsSummary.innerHTML = '<div class="loading-spinner"></div>加载中...';

        try {
            const [statsResponse, trendResponse] = await Promise.all([
                fetch(`/api/price_stats/?type=${this.currentType}`),
                fetch(`/api/average_price_trend/?type=${this.currentType}`)
            ]);

            if (!statsResponse.ok || !trendResponse.ok) {
                throw new Error(`网络错误: ${statsResponse.status}, ${trendResponse.status}`);
            }

            const statsData = await statsResponse.json();
            const trendData = await trendResponse.json();

            priceChartCanvas.parentElement.classList.remove('chart-loading');
            trendChartCanvas.parentElement.classList.remove('chart-loading');

            if (statsData.status === 'error') {
                throw new Error(statsData.message);
            }
            if (trendData.error) {
                throw new Error(trendData.error);
            }

            this.renderPriceDistributionChart(statsData);
            this.renderAveragePriceTrendChart(trendData);
            this.renderStatsSummary(statsData);
        } catch (error) {
            priceChartCanvas.parentElement.innerHTML = `<div class="chart-error">加载失败: ${error.message}</div>`;
            trendChartCanvas.parentElement.innerHTML = `<div class="chart-error">加载失败: ${error.message}</div>`;
            statsSummary.innerHTML = `<div class="error">加载失败: ${error.message}</div>`;
            console.error('可视化数据加载失败:', error);
        }
    }, 300),

    renderPriceDistributionChart(statsData) {
        const ctx = document.getElementById('priceDistributionChart')?.getContext('2d');
        if (!ctx) return;

        if (this.charts.priceDistribution) {
            this.charts.priceDistribution.destroy();
        }

        const priceData = statsData.price_distribution || [];
        if (!priceData.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="chart-error">${statsData.message || '暂无价格分布数据'}</div>`;
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
                    title: {
                        display: true,
                        text: `${this.getComponentName(this.currentType)} 价格分布`,
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => `${ctx.parsed.y} 款产品`
                        }
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        formatter: value => value > 0 ? value : '',
                        color: '#333'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: '产品数量' }
                    },
                    x: {
                        title: { display: true, text: '价格区间 (¥)' }
                    }
                }
            },
            plugins: [ChartDataLabels]
        });
    },

    renderAveragePriceTrendChart(trendData) {
        const ctx = document.getElementById('averagePriceTrendChart')?.getContext('2d');
        if (!ctx) return;

        if (this.charts.averagePriceTrend) {
            this.charts.averagePriceTrend.destroy();
        }

        const data = trendData.data || [];
        if (!data.length) {
            ctx.canvas.parentElement.innerHTML = `<div class="chart-error">${trendData.message || '暂无价格趋势数据'}</div>`;
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
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${this.getComponentName(this.currentType)} 平均价格趋势`,
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: ctx => `¥${ctx.parsed.y.toFixed(2)}`
                        }
                    }
                },
                scales: {
                    x: { title: { display: true, text: '日期' } },
                    y: {
                        title: { display: true, text: '平均价格 (¥)' },
                        beginAtZero: false
                    }
                }
            }
        });
    },

    renderStatsSummary(statsData) {
        const statsSummary = document.getElementById('statsSummary');
        if (!statsData || statsData.total_count === 0) {
            statsSummary.innerHTML = `<div class="error">${statsData.message || '暂无统计数据'}</div>`;
            return;
        }

        statsSummary.innerHTML = `
            <p>总产品数: ${statsData.total_count}</p>
            <p>中位数价格: ¥${statsData.median_price ? statsData.median_price.toFixed(2) : '未知'}</p>
            <p>平均价格: ¥${statsData.avg_price ? statsData.avg_price.toFixed(2) : '未知'}</p>
            <p>价格标准差: ¥${statsData.std_dev_price ? statsData.std_dev_price.toFixed(2) : '未知'}</p>
        `;
    },

    getComponentName(type) {
        const names = {
            'cpu': 'CPU',
            'gpu': '显卡',
            'ram': '内存',
            'ssd': '固态硬盘',
            'motherboard': '主板',
            'cooler': '散热器',
            'power_supply': '电源',
            'case': '机箱'
        };
        return names[type] || type;
    }
};

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function generateConfiguration() {
    const budget = document.getElementById('budget').value;
    const usage = document.getElementById('usage').value;
    const brandPreference = document.getElementById('brand-preference').value;

    fetch(`/generate-configuration?budget=${budget}&usage=${usage}&brand_preference=${brandPreference}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('生成配置失败: ' + data.error);
                return;
            }

            // 显示配置结果
            displayConfiguration(data);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('生成配置时出错');
        });
}

function displayConfiguration(data) {
    const container = document.getElementById('configuration-result');
    container.innerHTML = '';

    // 显示总价和预算使用情况
    const summary = document.createElement('div');
    summary.className = 'configuration-summary';
    summary.innerHTML = `
        <h3>配置单总价: ¥${data.total_price.toFixed(2)} (预算: ¥${data.budget})</h3>
        <p>预算使用率: ${(data.budget_usage * 100).toFixed(2)}%</p>
    `;
    container.appendChild(summary);

    // 显示各个配件
    for (const [type, component] of Object.entries(data.configuration)) {
        const componentDiv = document.createElement('div');
        componentDiv.className = 'configuration-component';
        componentDiv.innerHTML = `
            <h4>${getComponentName(type)}</h4>
            <p>${component.title}</p>
            <p class="price">¥${component.price.toFixed(2)}</p>
            <a href="/detail/${type}/${component.id}" target="_blank">查看详情</a>
        `;
        container.appendChild(componentDiv);
    }
}

function getComponentName(type) {
    const names = {
        'cpu': '处理器',
        'gpu': '显卡',
        'ram': '内存',
        'motherboard': '主板',
        'ssd': '固态硬盘',
        'power_supply': '电源',
        'case': '机箱',
        'cooler': '散热器'
    };
    return names[type] || type;
}

const SearchByPrice = {
    search() {
        const minPrice = parseFloat(document.getElementById('minPriceInput').value);
        const maxPrice = parseFloat(document.getElementById('maxPriceInput').value);
        const componentType = document.getElementById('priceComponentType').value;
        const resultsDiv = document.getElementById('priceSearchResults');

        // 验证价格输入
        if (isNaN(minPrice) || isNaN(maxPrice) || minPrice < 0 || maxPrice < 0 || minPrice > maxPrice) {
            resultsDiv.innerHTML = '<div class="error">请输入有效的价格范围</div>';
            return;
        }

        resultsDiv.innerHTML = '<div class="loading-spinner"></div> 搜索中...';

        fetch(`/api/get_components_by_price/?min_price=${minPrice}&max_price=${maxPrice}&type=${componentType}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                    return;
                }

                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<div class="no-results">未找到符合条件的配件</div>';
                    return;
                }

                resultsDiv.innerHTML = data.results.map(item => `
                    <div class="post">
                        <div class="title">${item.title}</div>
                        <div class="info">
                            <span>参考价: ¥${item.reference_price}</span>
                            <span>京东价: ¥${item.jd_price}</span>
                        </div>
                    </div>
                `).join('');
            })
            .catch(error => {
                resultsDiv.innerHTML = `<div class="error">搜索出错: ${error.message}</div>`;
            });
    }
};


function toggleFavorite() {
    const btn = document.getElementById('favoriteBtn');
    const type = btn.dataset.type;
    const id = btn.dataset.id;
    const isFavorited = btn.classList.contains('favorited');
    fetch('/api/favorite/', {
        method: isFavorited ? 'DELETE' : 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ type, id })
    })
    .then(res => res.json())
    .then(data => {
        btn.textContent = isFavorited ? '收藏' : '取消收藏';
        btn.classList.toggle('favorited');
    });
}
// 收藏列表模块


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