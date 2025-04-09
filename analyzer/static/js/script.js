/**
 * 硬件配件分析系统 - 主JavaScript文件
 * 包含功能：导航控制、搜索组件、详情展示、数据可视化
 */

// 全局图表引用
const globalCharts = {};

// 主应用模块
const App = {
    init() {
        // 初始化所有模块
        Navigation.init();
        Search.init();
        Visualization.init();
        
        // 默认加载第一个标签页内容
        Navigation.showSection('search');
    }
};

// 导航控制模块
const Navigation = {
    init() {
        // 绑定侧边栏点击事件
        document.querySelectorAll('.sidebar a').forEach(link => {
            const sectionId = link.getAttribute('onclick').match(/'([^']+)'/)[1];
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSection(sectionId);
            });
        });
    },

    showSection(sectionId) {
        // 隐藏所有内容区
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        
        // 显示目标内容区
        document.getElementById(sectionId).classList.add('active');
        
        // 更新侧边栏活动状态
        document.querySelectorAll('.sidebar a').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`.sidebar a[onclick*="${sectionId}"]`).classList.add('active');
        
        // 特殊处理可视化标签页
        if (sectionId === 'price') {
            Visualization.loadData();
        }
    }
};

// 搜索功能模块
const Search = {
    currentPage: 1,
    currentType: '',
    currentSort: '',

    init() {
        // 初始化组件类型下拉框
        document.getElementById('componentType').addEventListener('change', () => {
            this.updateFilters();
            this.currentPage = 1;
        });
        
        // 初始化搜索按钮
        document.querySelector('.search-bar button').addEventListener('click', () => {
            this.searchComponent(1);
        });
        
        // 初始化排序下拉框
        document.getElementById('sortBy').addEventListener('change', () => {
            this.searchComponent(1);
        });
        
        // 回车键搜索
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

        // CPU特殊过滤条件
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
            
            // 品牌选择事件
            document.getElementById('cpuBrand').addEventListener('change', function() {
                const brand = this.value;
                const seriesSelect = document.getElementById('cpuSeries');
                seriesSelect.innerHTML = '<option value="">所有系列</option>';
                
                if (!brand) return;
                
                // 加载系列数据
                fetch(`/api/get_cpu_series/?brand=${brand}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.series && data.series.length > 0) {
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
        // 其他组件类型的过滤条件可以在这里添加...
    },

    searchComponent(page) {
        this.currentPage = page;
        const query = document.getElementById('searchInput').value.trim();
        const componentType = document.getElementById('componentType').value;
        const sortValue = document.getElementById('sortBy').value;
        const resultDiv = document.getElementById('searchResult');
        const paginationDiv = document.getElementById('pagination');

        // 构建查询参数
        const params = new URLSearchParams();
        if (componentType) params.append('type', componentType);
        if (query) params.append('q', query);
        params.append('page', page);

        // 添加CPU过滤参数
        if (componentType === 'cpu') {
            const brand = document.getElementById('cpuBrand')?.value || '';
            const series = document.getElementById('cpuSeries')?.value || '';
            if (brand) params.append('brand', brand);
            if (series) params.append('series', series);
        }

        // 添加排序参数
        if (sortValue) {
            const [sortBy, sortOrder] = sortValue.split('_');
            params.append('sort_by', sortBy);
            params.append('sort_order', sortOrder);
        }

        // 显示加载状态
        resultDiv.innerHTML = '<div class="loading-spinner"></div> 搜索中...';
        
        // 发送请求
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
                
                // 渲染结果
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
        `).join('');} else {resultDiv.innerHTML = '<div class="no-results">未找到符合条件的配件</div>';
    }

        // 渲染分页
        this.renderPagination(data, paginationDiv);
    },

    renderPagination(data, container) {
        container.innerHTML = '';
        
        if (data.pages > 1) {
            const pagination = document.createElement('div');
            pagination.className = 'pagination';
            
            // 上一页按钮
            if (data.has_previous) {
                const prevBtn = document.createElement('button');
                prevBtn.className = 'page-btn';
                prevBtn.innerHTML = '&laquo; 上一页';
                prevBtn.addEventListener('click', () => this.searchComponent(data.current_page - 1));
                pagination.appendChild(prevBtn);
            }
            
            // 页码信息
            const pageInfo = document.createElement('span');
            pageInfo.className = 'page-info';
            pageInfo.textContent = `第 ${data.current_page} 页 / 共 ${data.pages} 页`;
            pagination.appendChild(pageInfo);
            
            // 下一页按钮
            if (data.has_next) {
                const nextBtn = document.createElement('button');
                nextBtn.className = 'page-btn';
                nextBtn.innerHTML = '下一页 &raquo;';
                nextBtn.addEventListener('click', () => this.searchComponent(data.current_page + 1));
                pagination.appendChild(nextBtn);
            }
            
            container.appendChild(pagination);
        }
    }
};

// 详情展示模块
const Detail = {
    show(componentType, id) {
        const modal = document.getElementById('detailModal');
        const modalContent = document.getElementById('modalContent');
        const modalLoading = document.getElementById('modalLoading');
        const modalError = document.getElementById('modalError');
        
        // 显示模态框和加载状态
        modal.style.display = 'block';
        modalLoading.style.display = 'block';
        modalContent.style.display = 'none';
        modalError.style.display = 'none';
        
        // 获取详情数据
        fetch(`/api/detail/${componentType}/${id}/`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP错误! 状态码: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.error) throw new Error(data.error);
                
                // 填充数据
                document.getElementById('detailTitle').textContent = data.title;
                document.getElementById('detailRefPrice').textContent = data.reference_price;
                document.getElementById('detailJDPrice').textContent = data.jd_price;
                document.getElementById('detailImage').src = data.product_image;
                
                // 处理参数列表
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
                
                // 处理京东链接
                const jdLink = document.getElementById('detailJDLink');
                if (data.jd_link) {
                    jdLink.href = data.jd_link;
                    jdLink.style.display = 'inline-block';
                } else {
                    jdLink.style.display = 'none';
                }
                
                // 显示内容
                modalLoading.style.display = 'none';
                modalContent.style.display = 'block';
            })
            .catch(error => {
                console.error('详情加载错误:', error);
                modalLoading.style.display = 'none';
                modalError.textContent = `加载失败: ${error.message}`;
                modalError.style.display = 'block';
            });
    },

    close() {
        document.getElementById('detailModal').style.display = 'none';
    }
};

// 数据可视化模块
const Visualization = {
    charts: {},
    chartContainers: null,
    currentComponent: 'cpu',

    init() {
        // 初始化图表容器
        this.chartContainers = {
            price: document.getElementById('priceDistributionChart'),
            brand: document.getElementById('brandDistributionChart')
        };

        // 验证元素
        if (!this.chartContainers.price || !this.chartContainers.brand) {
            console.error('图表容器元素未找到:', {
                price: !!this.chartContainers.price,
                brand: !!this.chartContainers.brand
            });
            return;
        }

        // 初始化控件事件
        document.getElementById('vizComponentType').addEventListener('change', (e) => {
            this.currentComponent = e.target.value;
            this.loadData();
        });

        this.loadData();
    },

    loadData() {
        // 显示加载状态
        this.showLoading();

        fetch(`/api/price_stats/?type=${this.currentComponent}`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.status === 'error') throw new Error(data.message);
                this.renderCharts(data);
            })
            .catch(error => {
                console.error('加载数据失败:', error);
                this.showError(error);
            });
    },

    renderCharts(data) {
        try {
            // 销毁旧图表
            if (this.charts.price) this.charts.price.destroy();
            if (this.charts.brand) this.charts.brand.destroy();

            // 渲染价格图表
            this.renderPriceChart(data.price_distribution);

            // 渲染品牌图表（如果有数据）
            if (data.brand_distribution?.length > 0) {
                this.renderBrandChart(data.brand_distribution);
            } else {
                this.showNoData(this.chartContainers.brand, '无品牌数据');
            }
        } catch (e) {
            console.error('渲染图表失败:', e);
            this.showError(e);
        }
    },

    renderPriceChart(data) {
        this.charts.price = new Chart(
            this.chartContainers.price.getContext('2d'),
            {
                type: 'bar',
                data: {
                    labels: data.map(d => d.range),
                    datasets: [{
                        label: '产品数量',
                        data: data.map(d => d.count),
                        backgroundColor: 'rgba(54, 162, 235, 0.7)'
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: { display: true, text: '价格分布' }
                    }
                }
            }
        );
    },

    renderBrandChart(data) {
        this.charts.brand = new Chart(
            this.chartContainers.brand.getContext('2d'),
            {
                type: 'pie',
                data: {
                    labels: data.map(d => d.brand),
                    datasets: [{
                        data: data.map(d => d.count),
                        backgroundColor: [
                            '#4e79a7', '#f28e2b', '#e15759', '#76b7b2'
                        ]
                    }]
                }
            }
        );
    },

    showLoading() {
        // 可以添加加载动画
    },

    showError(error) {
        // 显示错误信息
        const msg = error.message.includes('<!DOCTYPE')
            ? '服务器返回HTML而不是JSON'
            : error.message;

        [this.chartContainers.price, this.chartContainers.brand].forEach(el => {
            el.style.display = 'none';
            el.insertAdjacentHTML('afterend', `
                <div class="chart-error">${msg}</div>
            `);
        });
    },

    showNoData(element, message) {
        element.style.display = 'none';
        element.insertAdjacentHTML('afterend', `
            <div class="chart-no-data">${message}</div>
        `);
    }
};

// 页面加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    App.init();
    
    // 绑定模态框关闭事件
    document.querySelector('.modal .close').addEventListener('click', () => Detail.close());
    document.querySelector('.modal').addEventListener('click', (e) => {
        if (e.target === document.querySelector('.modal')) Detail.close();
    });
});

// 全局函数（为了兼容HTML中的onclick属性）
window.showDetail = Detail.show;
window.closeModal = Detail.close;