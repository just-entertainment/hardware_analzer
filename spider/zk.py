from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time


# 创建文件对
f = open('csv/固.csv', mode='w', encoding='utf-8', newline='')
# csv字典写入的方法
csv_writer = csv.DictWriter(f, fieldnames=['标题', '参考价','京东价','京东链接', '产品图片','产品参数'])
# 写入表头
csv_writer.writeheader()


dp = ChromiumPage()
dp.get(""
       "https://detail.zol.com.cn/motherboard/cheap.html"
       "")
#
# for size in sizes:
dp.scroll.to_bottom()
while(1):
    # goods = dp.ele("@id=J_PicMode").eles("@@tag:li@!class=pic-mode-ads")
    goods = dp.ele("@id=J_PicMode").eles("tag:li@!class=pic-mode-ads")
    for good in goods:
        try:
            title = good.ele('tag:h3').ele('tag:a').texts()[0].strip()
            price= good.ele("@class=price-row").ele("@class=price price-normal").text
            jd_price=good.ele('.:item-b2cprice').text
            href=''
            if jd_price:
                jd_href=good.ele('.:item-b2cprice').ele('tag:a').attr('href')

                ##打开新页面
            good_link = good.ele('tag:h3').ele('tag:a')
            tab = dp.new_tab(good_link.link)
            good_x=tab.ele('@class=product-param-item pi-5 clearfix').text
            image=tab.ele('@class=item 0').ele('tag:a').ele('tag:img').attr('src')
            dit = {
                '标题': title,
                '参考价':price,
                '京东价':jd_price,
                '京东链接':jd_href,
                '产品图片':image,
                '产品参数':good_x,
            }
            csv_writer.writerow(dit)
            print(dit)
            tab.close()
            time.sleep(1)
        except Exception as e:
            print(f"处理商品时出错: {e}")
            continue
    next_button = dp.ele("@class=page-box").ele("@class=pagebar").ele("@class=next")
    if next_button:
        next_button.click()
        time.sleep(2)
    else:
        print("没有下一页了")
        break