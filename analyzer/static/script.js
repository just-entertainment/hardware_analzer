// 切换导航
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');

    document.querySelectorAll('.sidebar a').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`.sidebar a[onclick="showSection('${sectionId}')"]`).classList.add('active');

    // 加载对应数据
    if (sectionId === 'price') loadPriceData();
    if (sectionId === 'new') loadNewData();
}

// 搜索功能
document.getElementById('searchInput').addEventListener('input', function(e) {
    const query = e.target.value;
    const resultDiv = document.getElementById('searchResult');
    if (query) {
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultDiv.innerHTML = data.results.map(item => `<div>${item}</div>`).join('');
            })
            .catch(error => {
                resultDiv.innerHTML = '搜索出错，请稍后重试';
                console.error(error);
            });
    } else {
        resultDiv.innerHTML = '请输入关键词开始搜索';
    }
});

// 加载价格涨幅数据
function loadPriceData() {
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

// 加载新品数据
function loadNewData() {
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

// 生成配置单
function generateConfig() {
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

// 初始化加载默认数据
document.addEventListener('DOMContentLoaded', () => {
    showSection('search'); // 默认显示搜索
});