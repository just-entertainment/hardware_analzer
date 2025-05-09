from DrissionPage import ChromiumPage
import csv
import time
from datetime import datetime
import os
import re


class CPUCrawler:
    def __init__(self):
#############################################################
        self.products_file = 'csv/cpu_products.csv'
        self.prices_file = 'csv/cpu_price_history.csv'
        self._init_csv_files()

    def _init_csv_files(self):
        """初始化CSV文件，写入表头"""
        os.makedirs('csv', exist_ok=True)

        # CPU产品表
        if not os.path.exists(self.products_file):
            with open(self.products_file, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'product_id', 'title', 'reference_price', 'current_price', 'jd_url',
                    'image_url', 'specs', 'shop_name', 'comment_count', 'crawl_time'
                ])
                writer.writeheader()

        # 价格历史表
        if not os.path.exists(self.prices_file):
            with open(self.prices_file, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'record_id', 'product_id', 'price', 'date', 'crawl_time'
                ])
                writer.writeheader()

    def _extract_price(self, raw_price):
        """从复杂文本中提取纯数字价格"""
        if not raw_price:
            return None

        # 匹配各种价格格式
        match = re.search(r'(?:[:：]|价|￥)?\s*(\d+\.?\d*)\s*元?', raw_price)
        return float(match.group(1)) if match else None

    def _parse_history_date(self, date_str):
        """处理历史价格日期格式"""
        try:
            # 处理"2025-02-22 17:15"格式，只保留日期部分
            return date_str.split()[0]
        except:
            return date_str  # 如果格式不符，返回原始字符串

    def _generate_product_id(self, jd_url):
        """从京东URL提取商品ID"""
        if jd_url:
            # 从类似 https://item.jd.com/100012345678.html 的URL中提取数字
            return ''.join(filter(str.isdigit, jd_url.split('/')[-1]))
        return str(int(time.time()))  # 使用时间戳作为备用ID

    def _save_product(self, product_data):
        """保存CPU产品信息"""
        with open(self.products_file, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=product_data.keys())
            writer.writerow(product_data)

    def _save_price_history(self, price_data):
        """保存历史价格"""
        with open(self.prices_file, mode='a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=price_data.keys())
            writer.writerow(price_data)

    def _get_price_history(self, page, jd_url):
        """从历史价格网站获取价格数据"""
        if not jd_url:
            return []

        try:
            hp = page.new_tab('https://www.hisprice.cn/')
            hp.ele('@class=search d1').ele('@id=kValId').input(jd_url)
            hp.actions.type('\n')
            time.sleep(7)  # 等待加载

            history = []
            price_list = hp.ele('@id=youhuiUl', timeout=3).eles('tag:li') if hp.ele('@id=youhuiUl', timeout=3) else []

            for item in price_list:
                try:
                    # 提取日期和价格
                    date_text = item.ele('@class=time', timeout=1).text
                    price_text = item.ele('@class=sinfo', timeout=1).text

                    # 清洗数据
                    clean_price = self._extract_price(price_text)
                    clean_date = self._parse_history_date(date_text)

                    if clean_price and clean_date:
                        history.append({
                            'date': clean_date,
                            'price': clean_price
                        })
                except Exception as e:
                    print(f"解析单条价格记录时出错: {e}")
                    continue

            hp.close()
            print(f"获取到 {len(history)} 条历史价格记录")
            return history
        except Exception as e:
            print(f"获取历史价格失败: {e}")
            return []

    def crawl(self):
        """主爬虫函数"""
        dp = ChromiumPage()
        ########################################################################
        dp.get("https://detail.zol.com.cn/cpu/")

        while True:
            dp.scroll.to_bottom()
            goods = dp.ele("@id=J_PicMode").eles("tag:li@!class=pic-mode-ads")

            for good in goods:
                try:
                    # 1. 提取基本信息
                    title = good.ele('tag:h3').ele('tag:a').texts()[0].strip()

                    reference_price = good.ele("@class=price-row").ele("@class=price price-normal").text
                    jd_price = good.ele('.:item-b2cprice').text
                    jd_href = good.ele('.:item-b2cprice').ele('tag:a').attr('href') if jd_price else ''

                    # 2. 生成产品ID
                    product_id = self._generate_product_id(jd_href)
                    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # 3. 获取详情页信息
                    good_link = good.ele('tag:h3').ele('tag:a')
                    tab = dp.new_tab(good_link.link)
                    ##################################################################################################
                    specs = tab.ele('@class=section-content').ele('@class=product-param-item pi-28 clearfix').text
                    # specs =tab.ele("@id=proParamSection").ele('@class=section-content').ele('@class=clearfix').text
                    image = tab.ele('@class=big-pic').ele('tag:a').ele('tag:img').attr('src')

                    # 4. 获取京东信息
                    if jd_href:
                        JD = dp.new_tab(jd_href)
                        shop_name = JD.ele('@class=top-name').text
                        comment_count = JD.ele('@id=comment-count').ele('tag:a').text
                        JD.close()
                    else:
                        shop_name = ''
                        comment_count = ''

                    # 5. 保存CPU产品信息
                    product_data = {
                        'product_id': product_id,
                        'title': title,
                        'reference_price': self._extract_price(reference_price),
                        'current_price': self._extract_price(jd_price),
                        'jd_url': jd_href,
                        'image_url': image,
                        'specs': specs,
                        'shop_name': shop_name,
                        'comment_count': comment_count,
                        'crawl_time': crawl_time
                    }
                    self._save_product(product_data)
                    print(f"已保存CPU: {title}")

                    # 6. 获取并保存历史价格
                    if jd_href:
                        price_history = self._get_price_history(dp, jd_href)
                        for idx, record in enumerate(price_history):
                            price_data = {
                                'record_id': f"{product_id}_{idx}",
                                'product_id': product_id,
                                'price': record['price'],
                                'date': record['date'],
                                'crawl_time': crawl_time
                            }
                            self._save_price_history(price_data)

                    tab.close()
                    time.sleep(2)

                except Exception as e:
                    print(f"处理商品时出错: {e}")
                    continue

            # 翻页逻辑
            next_button = dp.ele("@class=page-box").ele("@class=pagebar").ele("@class=next")
            if next_button:
                next_button.click()
                time.sleep(3)
            else:
                print("爬取完成")
                break


if __name__ == "__main__":
    crawler = CPUCrawler()
    crawler.crawl()