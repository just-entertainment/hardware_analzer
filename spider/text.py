from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time

dp = ChromiumPage()
# dp.get(""
#        "https://detail.zol.com.cn/solid_state_drive/good.html"
#        "")
# #
# # for size in sizes:
# dp.scroll.to_bottom()
# while(1):
#     # goods = dp.ele("@id=J_PicMode").eles("@@tag:li@!class=pic-mode-ads")
#     goods = dp.ele("@id=J_PicMode").eles("tag:li@!class=pic-mode-ads")
#     for good in goods:
#         good_link=good.ele('tag:h3').ele('tag:a')
tab = dp.new_tab('https://detail.zol.com.cn/vga/index1309963.shtml')
good_x=tab.ele("@id=proParamSection").ele('@class=section-content').ele('@class=clearfix').text
# image=tab.ele('@class=item 0').ele('tag:a').ele('tag:img').attr('src')
# text=tab.ele('@class=product-param-item pi-5 clearfix').text
print(good_x)
# print(text)
#
# tab.close()