from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time
import os

dp = ChromiumPage()
# JD=dp.new_tab('https://item.jd.com/100120799071.html')
# shop_name=JD.ele('@class=crumb-wrap').ele('@class=w').ele('@class=contact fr clearfix shieldShopInfo').ele('@class=item').text
# comment_count=JD.ele('@id=comment-count').ele('tag:a').text
# print(comment_count)
hp=dp.new_tab('https://www.hisprice.cn/')
hp.ele('@class=search d1').ele('@id=kValId').input('https://union-click.jd.com/sem.php?unionId=281&siteid=20170818001&to=https://item.jd.com/100145512952.html')
hp.actions.type('\n')  # 模拟按 Enter 键
time.sleep(5)
history_items = hp.ele('@id=youhuiUl').eles('tag:li')
for history in history_items:
    history_price = history.ele('@class=time').text
    history_date = history.ele('@class=sinfo').text
    print(history_price)