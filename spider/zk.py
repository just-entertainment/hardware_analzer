from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time


# 创建文件对
f = open('csv/RAM.csv', mode='w', encoding='utf-8', newline='')
# csv字典写入的方法
csv_writer = csv.DictWriter(f, fieldnames=['标题', '参考价','京东价','京东链接', '产品图片','产品参数', '京东店铺','评论数'])
# 写入表头
csv_writer.writeheader()


dp = ChromiumPage()
dp.get(""
       "https://detail.zol.com.cn/cpu/intel/"
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
            jd_href=''
            if jd_price:
                jd_href=good.ele('.:item-b2cprice').ele('tag:a').attr('href')

            ##打开新页面
            good_link = good.ele('tag:h3').ele('tag:a')
            tab = dp.new_tab(good_link.link)

            # good_x=tab.ele("@id=proParamSection").ele('@class=section-content').ele('@class=clearfix').text
            good_x = tab.ele('@class=section-content').ele('@class=product-param-item pi-3 clearfix').text
            image=tab.ele('@class=big-pic').ele('tag:a').ele('tag:img').attr('src')

            # 打开一个京东页面
            JD = dp.new_tab(jd_href)
            shop_name=JD.ele('@class=crumb-wrap').ele('@class=w').ele('@class=contact fr clearfix shieldShopInfo').ele('@class=item').text
            comment_count=JD.ele('@id=comment-count').ele('tag:a').text

            dit = {
                '标题': title,
                '参考价':price,
                '京东价':jd_price,
                '京东链接':jd_href,
                '产品图片':image,
                '产品参数':good_x,
                '京东店铺':shop_name,
                '评论数':comment_count,
            }
            csv_writer.writerow(dit)
            print(dit)
            tab.close()


            # 打开历史价格查询页面
            hp = dp.new_tab('https://www.hisprice.cn/')
            hp.ele('@class=search d1').ele('@id=kValId').input(jd_href)
            hp.actions.type('\n')  # 模拟按 Enter 键
            historys = hp.ele('tag:ul').eles('tag:li')
            for history in historys:
                history_price = history.ele('@class=time').text
                history_date = history.ele('@class=sinfo').text


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