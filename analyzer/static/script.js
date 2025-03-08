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
    searchCPU() {
        const query = document.getElementById('searchInput').value;
        const brand = document.getElementById('cpuBrand').value;
        const series = document.getElementById('cpuSeries').value;
        const type = document.getElementById('cpuType').value;
        const resultDiv = document.getElementById('searchResult');

        const params = new URLSearchParams();
        if (query) params.append('q', query);
        if (brand) params.append('brand', brand);
        if (series) params.append('series', series);
        if (type) params.append('type', type);

        resultDiv.innerHTML = '搜索中...';
        fetch(`/api/search/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    resultDiv.innerHTML = data.results.map(item => `
                        <div class="post">
                            <div class="title">${item.name}</div>
                            <div class="info">品牌: ${item.brand} | 系列: ${item.series} | 类型: ${item.type} | 价格: ¥${item.price}</div>
                        </div>
                    `).join('');
                } else {
                    resultDiv.innerHTML = '未找到符合条件的 CPU';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '搜索出错，请稍后重试';
                console.error(error);
            });
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