from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time
# 创建文件对象
f = open('csv/jdgpu0310.csv', mode='w', encoding='utf-8', newline='')
# csv字典写入的方法
csv_writer = csv.DictWriter(f, fieldnames=['品牌','商品名称','商品编号', '价格','店铺名称'])
# 写入表头
csv_writer.writeheader()

# 搜索部分
dp = ChromiumPage()
dp.get('https://search.jd.com/search?keyword=%E6%98%BE%E5%8D%A1&wq=%E6%98%BE%E5%8D%A1&stock=1&pvid=fda3c8b12ae44bf7b67592f6fc0cf18e&cid3=679&cid2=677&psort=3&click=0')

for page in range(1, 11):
    productnumber
    dp.scroll.to_bottom()
    products = dp.eles('tag:li@class=gl-item')
    for product in products:
        productnumber=productnumber+1
        try:
            product_link = product.ele('tag:a')
            shopname = product.ele('.p-shop').text  # 获取店铺名称
            tab_detail = dp.new_tab(product_link.link)  # 激活新标签页
            price=tab_detail.ele('@class=p-price').text
            # good_detail=tab_detail.ele('xpath:http://html/body/div[10]/div[2]')
            good_detail = tab_detail.ele('xpath:/html/body/div[10]/div[2]').ele('@id=detail').ele('@class=tab-con').ele('@class=p-parameter')
            good_band=good_detail.ele('@id=parameter-brand').text
            good_name=good_detail.ele('@class=parameter2 p-parameter-list').eles('tag:li')[0].text
            good_number=good_detail.ele('@class=parameter2 p-parameter-list').eles('tag:li')[1].text
            # good_series=good_detail.ele('@class=parameter2 p-parameter-list').eles('tag:li')[2].text
            dit = {
                '品牌':  good_band,
                '商品名称': good_name,
                '商品编号':good_number,
                # '系列':good_series,
                '价格': price,
                '店铺名称': shopname,
            }
            csv_writer.writerow(dit)
            print(dit)
        except Exception as e:
            print(e)
        finally:
            tab_detail.close()  # 关闭当前标签页
            time.sleep(2)

