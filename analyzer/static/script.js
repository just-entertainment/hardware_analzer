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
                <select id="ramCapacity"><option value="">容量</option><option value="8">8GB</option><option value="16">16GB</option><option value="32">32GB</option></select>
                <select id="ramType"><option value="">类型</option><option value="DDR4">DDR4</option><option value="DDR5">DDR5</option></select>
                <select id="ramFrequency"><option value="">频率</option><option value="3200">3200MHz</option><option value="3600">3600MHz</option><option value="4800">4800MHz</option></select>
            `;
        } else if (componentType === 'gpu') {
            filterContainer.innerHTML = `
                <select id="gpuBrand">
                    <option value="">品牌</option>
                    <option value="NVIDIA">NVIDIA</option>
                    <option value="AMD">AMD</option>
                    <option value="intel">intel</option>
                </select>
            `;
        } else if (componentType === 'cpu') {
            filterContainer.innerHTML = `
                <select id="cpuBrand">
                    <option value="">品牌</option>
                    <option value="intel">intel</option>
                    <option value="AMD">AMD</option>
                </select>
            `;
        } else if (componentType === 'motherboard') {
            filterContainer.innerHTML = `
                <select id="motherboardBrand">
                    <option value="">品牌</option>
                    <option value="ASUS">ASUS</option>
                    <option value="Gigabyte">Gigabyte</option>
                    <option value="MSI">MSI</option>
                </select>
            `;
        }
    },

    searchComponent(page) {
        const query = document.getElementById('searchInput').value.trim();
        const componentType = document.getElementById('componentType').value;
        const sortValue = document.getElementById('sortBy').value;
        const resultDiv = document.getElementById('searchResult');
        const paginationDiv = document.getElementById('pagination');

        if (!query && !componentType) {
            resultDiv.innerHTML = '请输入关键词或选择配件类型';
            return;
        }

        const params = new URLSearchParams();
        if (componentType) params.append('type', componentType);
        if (query) params.append('q', query);
        params.append('page', page);

        if (sortValue) {
            const lastUnderscore = sortValue.lastIndexOf('_');
            const sortBy = sortValue.substring(0, lastUnderscore);
            const sortOrder = sortValue.substring(lastUnderscore + 1);
            params.append('sort_by', sortBy);
            params.append('sort_order', sortOrder);
        }

        const url = `/api/search/?${params.toString()}`;
        resultDiv.innerHTML = '搜索中...';
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    resultDiv.innerHTML = `错误: ${data.error}`;
                    return;
                }
                if (data.results.length > 0) {
                    resultDiv.innerHTML = data.results.map(item => `
                        <div class="post" onclick="showDetail('${item.type}', ${item.id})">
                            <div class="title">${item.title}</div>
                            <div class="info">参考价: ¥${item.reference_price} | 京东价: ¥${item.jd_price}</div>
                        </div>
                    `).join('');
                } else {
                    resultDiv.innerHTML = '未找到符合条件的配件';
                }

                paginationDiv.innerHTML = '';
                if (data.pages > 1) {
                    let paginationHTML = '';
                    if (data.has_previous) {
                        paginationHTML += `<button onclick="search.searchComponent(${data.current_page - 1})">上一页</button>`;
                    }
                    paginationHTML += `<span>第 ${data.current_page} 页 / 共 ${data.pages} 页 (总 ${data.total} 条)</span>`;
                    if (data.has_next) {
                        paginationHTML += `<button onclick="search.searchComponent(${data.current_page + 1})">下一页</button>`;
                    }
                    paginationDiv.innerHTML = paginationHTML;
                }
            })
            .catch(error => {
                resultDiv.innerHTML = `搜索出错: ${error.message}`;
                console.error('Fetch error:', error);
            });
    }
};

function showDetail(componentType, id) {
    const modal = document.getElementById('detailModal');
    const modalLoading = document.getElementById('modalLoading');
    const modalContent = document.getElementById('modalContent');
    const modalError = document.getElementById('modalError');

    modal.style.display = 'block';
    modalLoading.style.display = 'block';
    modalContent.style.display = 'none';
    modalError.style.display = 'none';

    fetch(`/api/detail/${componentType}/${id}/`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) {
                modalLoading.style.display = 'none';
                modalError.innerHTML = `错误: ${data.error}`;
                modalError.style.display = 'block';
                return;
            }

            document.getElementById('detailTitle').innerText = data.title;
            document.getElementById('detailRefPrice').innerText = data.reference_price;
            document.getElementById('detailJDPrice').innerText = data.jd_price;
            document.getElementById('detailImage').src = data.product_image;
            document.getElementById('detailSpecs').innerHTML = data.product_parameters.split('\n').map(param => `<li>${param}</li>`).join('');

            modalLoading.style.display = 'none';
            modalContent.style.display = 'block';
        })
        .catch(error => {
            modalLoading.style.display = 'none';
            modalError.innerHTML = `加载详情出错: ${error.message}`;
            modalError.style.display = 'block';
            console.error('Fetch error:', error);
        });
}

function closeModal() {
    document.getElementById('detailModal').style.display = 'none';
}

const config = {
    generateConfig() {
        document.getElementById('config-result').innerHTML = '功能暂未实现';
    }
};