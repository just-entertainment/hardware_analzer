from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time


# 创建文件对象
f = open('csv/ramDDR40310.csv', mode='w', encoding='utf-8', newline='')
# csv字典写入的方法
csv_writer = csv.DictWriter(f, fieldnames=['标题', '参考价','京东价'])
# 写入表头
csv_writer.writeheader()


dp = ChromiumPage()
dp.get(""
       "https://detail.zol.com.cn/memory/s2951_p26895/hebei/"
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
            dit = {
                '标题': title,
                '参考价':price,
                '京东价':jd_price,
            }
            csv_writer.writerow(dit)
            print(dit)
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