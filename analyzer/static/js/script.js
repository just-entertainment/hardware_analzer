const App = {
    init() {
        Navigation.init();
        Search.init();
        Visualization.init();
        Config.init();
        Navigation.showSection('search');
    }
};

const Navigation = {
    init() {
        document.querySelectorAll('.sidebar a').forEach(link => {
            const sectionId = link.getAttribute('onclick').match(/'([^']+)'/)[1];
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSection(sectionId);
            });
        });
    },

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => section.classList.remove('active'));
        document.getElementById(sectionId).classList.add('active');
        document.querySelectorAll('.sidebar a').forEach(link => link.classList.remove('active'));
        document.querySelector(`.sidebar a[onclick*="${sectionId}"]`).classList.add('active');
        if (sectionId === 'price') Visualization.loadData();
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
                <div class="post" onclick="Detail.show('${item.type}', ${item.id})">
                    <div class="title">${item.title}</div>
                    <div class="info">
                        <span>参考价: ¥${item.reference_price}</span>
                        <span>京东价: ¥${item.jd_price}</span>
                    </div>
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
    }
};

const Detail = {
    show(componentType, id) {
        const modal = document.getElementById('detailModal');
        const modalContent = document.getElementById('modalContent');
        const modalLoading = document.getElementById('modalLoading');
        const modalError = document.getElementById('modalError');

        modal.style.display = 'block';
        modalLoading.style.display = 'block';
        র

modalContent.style.display = 'none';
        modalError.style.display = 'none';

        fetch(`/api/detail/${componentType}/${id}/`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP错误! 状态码: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.error) throw new Error(data.error);
                document.getElementById('detailTitle').textContent = data.title;
                document.getElementById('detailRefPrice').textContent = data.reference_price;
                document.getElementById('detailJDPrice').textContent = data.jd_price;
                document.getElementById('detailImage').src = data.product_image;
                const specsList = document.getElementById('detailSpecs');
                specsList.innerHTML = '';
                if (data.product_parameters) {
                    data.product_parameters.split('\n').forEach(param => {
                        if (param.trim()) {
                            const li = document.createElement('li');
                            li.textContent = param;
                            specsList.appendChild(li);
                        }
                    });
                }
                const jdLink = document.getElementById('detailJDLink');
                if (data.jd_link) {
                    jdLink.href = data.jd_link;
                    jdLink.style.display = 'inline-block';
                } else {
                    jdLink.style.display = 'none';
                }
                modalLoading.style.display = 'none';
                modalContent.style.display = 'block';
            })
            .catch(error => {
                modalLoading.style.display = 'none';
                modalError.textContent = `加载失败: ${error.message}`;
                modalError.style.display = 'block';
            });
    },

    close() {
        document.getElementById('detailModal').style.display = 'none';
    }
};

const Config = {
    init() {
        document.querySelector('.generate-btn').addEventListener('click', () => this.generateConfig());
    },

    async generateConfig() {
        const budget = document.getElementById('budgetInput').value;
        const usage = document.getElementById('usageSelect').value;
        const resultsDiv = document.getElementById('configResults');

        resultsDiv.innerHTML = '<div class="loading-spinner"></div> 生成中...';

        try {
            const components = [
                { type: 'cpu', budgetShare: 0.3 },
                { type: 'gpu', budgetShare: 0.3 },
                { type: 'ram', budgetShare: 0.1 },
                { type: 'motherboard', budgetShare: 0.1 },
                { type: 'ssd', budgetShare: 0.1 },
                { type: 'power_supply', budgetShare: 0.05 },
                { type: 'case', budgetShare: 0.05 }
            ];

            let totalPrice = 0;
            const configItems = await Promise.all(components.map(async (comp) => {
                const priceLimit = budget * comp.budgetShare;
                const response = await fetch(`/api/search/?type=${comp.type}&sort_by=reference_price&sort_order=asc&per_page=1`);
                const data = await response.json();
                if (data.results && data.results.length > 0) {
                    const item = data.results[0];
                    totalPrice += parseFloat(item.reference_price !== '暂无' ? item.reference_price : 0);
                    return { type: comp.type, title: item.title, price: item.reference_price };
                }
                return null;
            }));

            resultsDiv.innerHTML = `
                <div class="config-card">
                    <div class="config-header">
                        <span class="config-title">推荐配置 (${usage})</span>
                        <span class="config-price">总价: ¥${totalPrice.toFixed(2)}</span>
                    </div>
                    <div class="config-items">
                        ${configItems.filter(item => item).map(item => `
                            <div class="config-item">
                                <div class="item-name">${this.getComponentName(item.type)}: ${item.title}</div>
                                <div class="item-price">¥${item.price}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">生成配置失败: ${error.message}</div>`;
            console.error('配置生成错误:', error);
        }
    },

    getComponentName(type) {
        const names = {
            'cpu': 'CPU',
            'gpu': '显卡',
            'ram': '内存',
            'motherboard': '主板',
            'ssd': '固态硬盘',
            'cooler': '散热器',
            'power_supply': '电源',
            'case': '机箱'
        };
        return names[type] || type;
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

document.addEventListener('DOMContentLoaded', () => {
    App.init();
    document.querySelector('.modal .close').addEventListener('click', () => Detail.close());
    document.querySelector('.modal').addEventListener('click', (e) => {
        if (e.target === document.querySelector('.modal')) Detail.close();
    });
});

window.showDetail = Detail.show;
window.closeModal = Detail.close;
window.generateConfig = Config.generateConfig;