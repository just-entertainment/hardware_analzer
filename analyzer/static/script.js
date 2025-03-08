// 导航模块
const navigation = {
    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');

        document.querySelectorAll('.sidebar a').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`.sidebar a[onclick="navigation.showSection('${sectionId}')"]`).classList.add('active');

        // 加载对应数据
        if (sectionId === 'price') price.loadPriceData();
        if (sectionId === 'new') newReleases.loadNewData();
    }
};

// 搜索模块
const search = {
    updateFilters() {
        const componentType = document.getElementById('componentType').value;
        const filterContainer = document.getElementById('dynamicFilters');
        filterContainer.innerHTML = '';

        if (componentType === 'cpu') {
            filterContainer.innerHTML = `
                <select id="cpuBrand">
                    <option value="">品牌</option>
                    <option value="Intel">Intel</option>
                    <option value="AMD">AMD</option>
                </select>
                <select id="cpuSeries">
                    <option value="">系列</option>
                    <option value="Core i">Core i</option>
                    <option value="Ryzen">Ryzen</option>
                </select>
            `;
        } else if (componentType === 'ram') {
            filterContainer.innerHTML = `
                <select id="ramCapacity">
                    <option value="">容量</option>
                    <option value="8">8GB</option>
                    <option value="16">16GB</option>
                    <option value="32">32GB</option>
                </select>
                <select id="ramType">
                    <option value="">类型</option>
                    <option value="DDR4">DDR4</option>
                    <option value="DDR5">DDR5</option>
                </select>
                <select id="ramFrequency">
                    <option value="">频率</option>
                    <option value="3200">3200MHz</option>
                    <option value="3600">3600MHz</option>
                    <option value="4800">4800MHz</option>
                </select>
            `;
        }
    },

    searchComponent() {
        const componentType = document.getElementById('componentType').value;
        const query = document.getElementById('searchInput').value.trim();
        const resultDiv = document.getElementById('searchResult');

        if (!componentType) {
            resultDiv.innerHTML = '请选择配件类型';
            return;
        }

        const params = new URLSearchParams();
        params.append('type', componentType);
        if (query) params.append('q', query);

        if (componentType === 'cpu') {
            const brand = document.getElementById('cpuBrand')?.value || '';
            const series = document.getElementById('cpuSeries')?.value || '';
            if (brand) params.append('brand', brand);
            if (series) params.append('series', series);
        } else if (componentType === 'ram') {
            const capacity = document.getElementById('ramCapacity')?.value || '';
            const ramType = document.getElementById('ramType')?.value || '';
            const frequency = document.getElementById('ramFrequency')?.value || '';
            if (capacity) params.append('capacity', capacity);
            if (ramType) params.append('ram_type', ramType);
            if (frequency) params.append('frequency', frequency);
        }

        resultDiv.innerHTML = '搜索中...';
        fetch(`/api/search/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    resultDiv.innerHTML = data.results.map(item => `
                        <div class="post">
                            <div class="title">${item.name}</div>
                            <div class="info">${search.formatInfo(item)}</div>
                        </div>
                    `).join('');
                } else {
                    resultDiv.innerHTML = '未找到符合条件的配件';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '搜索出错，请稍后重试';
                console.error(error);
            });
    },

    formatInfo(item) {
        if (item.type === 'cpu') {
            return `品牌: ${item.brand} | 系列: ${item.series} | 价格: ¥${item.price}`;
        } else if (item.type === 'ram') {
            return `容量: ${item.capacity}GB | 类型: ${item.ram_type} | 频率: ${item.frequency}MHz | 价格: ¥${item.price}`;
        }
        return '';
    }
};

// 价格涨幅模块
const price = {
    loadPriceData() {
        const priceDiv = document.getElementById('priceList');
        priceDiv.innerHTML = '加载中...';
        fetch('/api/price-changes/')
            .then(response => response.json())
            .then(data => {
                priceDiv.innerHTML = data.map(item => `
                    <div class="post">
                        <div class="title">${item.name}</div>
                        <div class="info">${item.change} - 当前 ¥${item.price}</div>
                    </div>
                `).join('');
            })
            .catch(error => {
                priceDiv.innerHTML = '加载失败，请稍后重试';
                console.error(error);
            });
    }
};

// 新品发布模块
const newReleases = {
    loadNewData() {
        const newDiv = document.getElementById('newList');
        newDiv.innerHTML = '加载中...';
        fetch('/api/new-releases/')
            .then(response => response.json())
            .then(data => {
                newDiv.innerHTML = data.map(item => `
                    <div class="post">
                        <div class="title">${item.name}</div>
                        <div class="info">发布日期: ${item.date} - 预计 ¥${item.price}</div>
                    </div>
                `).join('');
            })
            .catch(error => {
                newDiv.innerHTML = '加载失败，请稍后重试';
                console.error(error);
            });
    }
};

// 配置单模块
const config = {
    generateConfig() {
        const budget = document.getElementById('budgetInput').value;
        const resultDiv = document.getElementById('config-result');
        resultDiv.innerHTML = '';

        if (!budget || budget < 1000) {
            resultDiv.innerHTML = '<div class="config-item">请输入有效的预算（至少 ¥1000）！</div>';
            return;
        }

        fetch(`/api/generate-config/?budget=${budget}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `<div class="config-item">${data.error}</div>`;
                } else {
                    resultDiv.innerHTML = data.config.map(item => `
                        <div class="config-item">${item.name}: ${item.item} - ¥${item.price}</div>
                    `).join('') + `<div class="config-item">总计: ¥${data.total}</div>`;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '生成失败，请稍后重试';
                console.error(error);
            });
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    navigation.showSection('search');
});