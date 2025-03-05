from DrissionPage import ChromiumPage
from DrissionPage.common import Keys
import csv
import time

# 创建文件对象
f = open('', mode='w', encoding='utf-8', newline='')
# csv字典写入的方法
csv_writer = csv.DictWriter(f, fieldnames=['品牌','商品名称','规格', '价格', '店铺名称','链接地址'])
# 写入表头
csv_writer.writeheader()

# 搜索部分
dp = ChromiumPage()
dp.get('https://search.jd.com/search?keyword=%E5%86%85%E5%AD%98&spm=a.0.0&wq=%E5%86%85%E5%AD%98&cid3=680&psort=3')
# input=input()
time.sleep(5)
# dp.ele('#key').input('cpu')
# dp.ele('#key').input(Keys.ENTER)
# time.sleep(3)  # 等待搜索完成

# 定义监听函数
def handle_request(request):
    if 'api.jd.com' in request.url and 'price' in request.url:
        response_data = request.response.body  # 假设返回的是 JSON 数据
        print("捕获到价格请求:", response_data)
        # 解析 JSON 数据并提取价格
        price = response_data.get('price')

i=0
# 开始监听
dp.listen.start('api.jd.com', handle_request)

# 翻页循环
for page in range(1, 11):
    # 获取当前页所有商品
    time.sleep(3)
    dp.scroll.to_bottom()
    time.sleep(3)
    dp.scroll.to_bottom()
    time.sleep(3)

    products = dp.eles('tag:li@class=gl-item')
    # 遍历商品
    for product in products:
        # 获取商品链接并打开新标签页
        i=i+1
        print(i)
        product_link = product.ele('tag:a')
        shopname = product.ele('.p-shop').text      # 获取店铺名称
        tab = dp.new_tab(product_link.link)         # 激活新标签页
        time.sleep(5) # 等待新页面加载


        try:
            # 检查是否有规格选择区域
            spec_area = tab.ele('@id=choose-attrs') # 尝试获取规格区域
            if not spec_area:
                # 如果没有规格区域，直接获取价格
                band=tab.ele('#parameter-brand').ele('tag=li').attr('title')
                price = tab.ele('.p-price').text
                goodname=tab.ele('.=parameter2 p-parameter-list').ele('tag=li').attr('title')
                herf=tab.url
                dit = {
                    '品牌':band,
                    '商品名称':goodname,
                    '规格': '无规格',
                    '价格': price,
                    '店铺名称': shopname,
                    '链接地址':herf,
                }
                csv_writer.writerow(dit)
                print(dit)
            else:
                # 处理规格1（如果存在）
                spec1_wrapper = spec_area.ele('#choose-attr-1')
                if spec1_wrapper:
                    spec1_options = spec1_wrapper.ele('.=dd').eles('tag:a')
                    # spec_area = tab.ele('@id=choose-attrs')
                    spec2_wrapper = spec_area.ele('#choose-attr-2')
                    number_1_all = len(spec1_options)
                    if spec2_wrapper:
                        for i in range(0, number_1_all):
                            spec_area = tab.ele('@id=choose-attrs')
                            spec1_wrapper = spec_area.ele('#choose-attr-1')
                            spec1_options = spec1_wrapper.ele('.=dd').eles('tag:a')
                            time.sleep(3)
                            spec1_options[i].click()
                            time.sleep(3)
                            spec_area = tab.ele('@id=choose-attrs')
                            spec2_wrapper = spec_area.ele('#choose-attr-2')
                            spec2_options = spec2_wrapper.ele('.=dd').eles('@|class=item  selected@|class=item')
                            number_2_all=len(spec2_options)
                            for j in range(0,number_2_all):
                                spec_area = tab.ele('@id=choose-attrs')
                                spec2_wrapper = spec_area.ele('#choose-attr-2')
                                spec2_options =spec2_wrapper.ele('.=dd').eles('@|class=item  selected@|class=item')
                                time.sleep(3)
                                spec2_options[j].ele('tag:a').click()

                                # 获取价格
                                time.sleep(3)
                                spec_area = tab.ele('@id=choose-attrs')
                                spec1_wrapper = spec_area.ele('#choose-attr-1')
                                spec1_options = spec1_wrapper.ele('.=dd').eles('tag:a')
                                spec2_wrapper = spec_area.ele('#choose-attr-2')
                                spec2_options = spec2_wrapper.ele('.=dd').eles('@|class=item  selected@|class=item')
                                band = tab.ele('#parameter-brand').ele('tag=li').attr('title')
                                price = tab.ele('.p-price').text
                                goodname = tab.ele('.=parameter2 p-parameter-list').ele('tag=li').attr('title')
                                herf = tab.url
                                dit = {
                                    '品牌': band,
                                    '商品名称': goodname,
                                    '规格':   spec1_options[i].text+'+'+spec2_options[j].text,
                                    '价格': price,
                                    '店铺名称': shopname,
                                    '链接地址': herf,
                                }
                                csv_writer.writerow(dit)
                                print(dit)
                    else:
                        for i in range(0, number_1_all):
                            spec_area = tab.ele('@id=choose-attrs')
                            spec1_wrapper = spec_area.ele('#choose-attr-1')
                            spec1_options = spec1_wrapper.ele('.=dd').eles('tag:a')
                            time.sleep(3)
                            spec1_options[i].click()
                            time.sleep(3)
                            spec_area = tab.ele('@id=choose-attrs')
                            spec1_wrapper = spec_area.ele('#choose-attr-1')
                            spec1_options = spec1_wrapper.ele('.=dd').eles('tag:a')
                            band = tab.ele('#parameter-brand').ele('tag=li').attr('title')
                            price = tab.ele('.p-price').text
                            goodname = tab.ele('.=parameter2 p-parameter-list').ele('tag=li').attr('title')
                            herf = tab.url
                            dit = {
                                '品牌': band,
                                '商品名称': goodname,
                                '规格': spec1_options[i].text,
                                '价格': price,
                                '店铺名称': shopname,
                                '链接地址': herf,
                            }
                            csv_writer.writerow(dit)
                            print(dit)

        except Exception as e:
            print(f"处理商品时出错: {e}")
        finally:
            tab.close()  # 关闭当前标签页
            time.sleep(2)
    # 翻页操作

    next_btn = dp.ele('.pn-next')
    next_btn.click()
    time.sleep(3)  # 等待新页加载


# 停止监听
dp.listen.stop()
# 关闭文件
f.close()