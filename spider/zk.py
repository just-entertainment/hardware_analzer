from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time


# 创建文件对象
f = open('cvs/intelcpu', mode='w', encoding='utf-8', newline='')
# csv字典写入的方法
csv_writer = csv.DictWriter(f, fieldnames=['标题', '参考价'])
# 写入表头
csv_writer.writeheader()


dp = ChromiumPage()
dp.get("https://detail.zol.com.cn/cpu/intel/cheap.html")
#
# for size in sizes:
time.sleep(3)
dp.scroll.to_bottom()
count=0
for page in range(0,3):
    # goods = dp.ele("@id=J_PicMode").eles("@@tag:li@!class=pic-mode-ads")
    goods = dp.ele("@id=J_PicMode").eles("tag:li@!class=pic-mode-ads")
    for good in goods:
        try:
            title= good.ele("tag:h3").text
            price= good.ele("@class=price-row").ele("@class=price price-normal").text
            dit = {
                '标题': title,
                '参考价':price,
            }
            count=count+1
            csv_writer.writerow(dit)
            print(dit)
        except:
            continue
    dp.ele("@class=page-box").ele("@class=pagebar").ele("@class=next").click
print(count)