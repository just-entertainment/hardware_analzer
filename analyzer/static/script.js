const navigation = {
    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');
        document.querySelectorAll('.sidebar a').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`.sidebar a[onclick*="${sectionId}"]`).classList.add('active');
    }
};

const search = {
    updateFilters() {
        const componentType = document.getElementById('componentType').value;
        const filterContainer = document.getElementById('dynamicFilters');
        filterContainer.innerHTML = '';

        if (componentType === 'ram') {
            filterContainer.innerHTML = `
                <select id="ramCapacity">
                    <option value="">容量</option>
                    <option value="8">8GB</option>
                    <option value="16">16GB</option>
                    <option value="32">32GB</option>
                </select>
                <select id="ramType">
                    <option value="">类型</option>
                    <option value="DDR3">DDR3</option>
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

        if (!query && !componentType) {
            resultDiv.innerHTML = '请输入关键词或选择配件类型';
            return;
        }

        const params = new URLSearchParams();
        if (componentType) params.append('type', componentType);
        if (query) params.append('q', query);

        resultDiv.innerHTML = '搜索中...';
        fetch(`/api/search/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length > 0) {
                    resultDiv.innerHTML = data.results.map(item => `
                        <div class="post">
                            <div class="title">${item.title}</div>
                            <div class="info">参考价: ¥${item.reference_price} | 京东价: ¥${item.jd_price}</div>
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
    }
};

const config = {
    generateConfig() {
        document.getElementById('config-result').innerHTML = '功能暂未实现';
    }
};