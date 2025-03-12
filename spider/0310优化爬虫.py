from DrissionPage import ChromiumPage
import csv
import time
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='jd_crawler.log'
)

# 进度记录文件
PROGRESS_FILE = 'progress.txt'
# CSV 文件路径
CSV_FILE = 'csv/jdgpu0310.csv'

# 初始化进度
current_page = 1
current_product_index = 0

# 如果进度文件存在，读取上次的爬取进度
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, 'r') as f:
        current_page, current_product_index = map(int, f.read().split(','))

# 打开 CSV 文件，使用追加模式
with open(CSV_FILE, mode='a', encoding='utf-8', newline='') as f:
    fieldnames = ['品牌', '商品名称', '商品编号', '价格', '店铺名称']
    csv_writer = csv.DictWriter(f, fieldnames=fieldnames)

    # 如果是第一次爬取，写入表头
    if current_page == 1 and current_product_index == 0:
        csv_writer.writeheader()

    # 初始化浏览器
    dp = ChromiumPage()
    dp.get(
        f'https://search.jd.com/search?keyword=%E6%98%BE%E5%8D%A1&wq=%E6%98%BE%E5%8D%A1&stock=1&pvid=fda3c8b12ae44bf7b67592f6fc0cf18e&cid3=679&cid2=677&psort=3&click=0&page={current_page}')

    for page in range(current_page, 11):
        logging.info(f'正在爬取第 {page} 页...')
        dp.scroll.to_bottom()
        products = dp.eles('tag:li@class=gl-item')

        for idx, product in enumerate(products[current_product_index:], start=current_product_index):
            try:
                product_link = product.ele('tag:a')
                shopname = product.ele('.p-shop').text  # 获取店铺名称

                # 打开新标签页获取商品详情
                tab_detail = dp.new_tab(product_link.link)
                price = tab_detail.ele('@class=p-price').text
                good_detail = tab_detail.ele('xpath:/html/body/div[10]/div[2]').ele('@id=detail').ele(
                    '@class=tab-con').ele('@class=p-parameter')
                good_band = good_detail.ele('@id=parameter-brand').text
                good_name = good_detail.ele('@class=parameter2 p-parameter-list').eles('tag:li')[0].text
                good_number = good_detail.ele('@class=parameter2 p-parameter-list').eles('tag:li')[1].text

                # 写入 CSV 文件
                dit = {
                    '品牌': good_band,
                    '商品名称': good_name,
                    '商品编号': good_number,
                    '价格': price,
                    '店铺名称': shopname,
                }
                csv_writer.writerow(dit)
                logging.info(f'已爬取: {dit}')

                # 更新进度
                current_product_index = idx + 1
                with open(PROGRESS_FILE, 'w') as pf:
                    pf.write(f'{page},{current_product_index}')

            except Exception as e:
                logging.error(f'爬取商品时出错: {e}')
            finally:
                tab_detail.close()  # 关闭当前标签页
                time.sleep(2)  # 随机延时，避免被封禁

        # 重置当前页的商品索引
        current_product_index = 0
        current_page += 1

        # 保存进度
        with open(PROGRESS_FILE, 'w') as pf:
            pf.write(f'{current_page},{current_product_index}')

        # 模拟翻页
        if page < 10:
            dp.ele('@class=pn-next').click()
            time.sleep(3)  # 等待页面加载

# 关闭浏览器
dp.close()
logging.info('爬取完成！')