from DrissionPage import ChromiumPage
import csv
import time

# 创建文件对象
with open('csv/cpu.csv', mode='w', encoding='utf-8', newline='') as f:
    # 更新 fieldnames，添加品牌、系列、型号
    csv_writer = csv.DictWriter(f, fieldnames=['标题', '品牌', '系列', '型号', '参考价', '京东价'])
    csv_writer.writeheader()

    # 初始化浏览器
    dp = ChromiumPage()

    # 访问目标页面
    dp.get("https://detail.zol.com.cn/cpu/cheap.html")

    while(1):
        dp.scroll.to_bottom()
        time.sleep(1)  # 等待动态内容加载

        # 获取商品列表
        goods = dp.ele("@id=J_PicMode").eles("tag:li@!class=pic-mode-ads")

        for good in goods:
            try:
                # 获取 <h3><a> 的直接文本，排除 <span>
                title = good.ele('xpath:.//h3/a/text()').strip()

                # 分割标题
                parts = title.split()
                if len(parts) == 3:
                    brand, series, model = parts[0], parts[1], parts[2]
                elif len(parts) == 4:
                    brand, series, model = parts[0], f"{parts[1]} {parts[2]}", parts[3]
                else:
                    # 如果不是 3 或 4 部分，保留原始标题
                    brand, series, model = parts[0] if parts else '', '', title

                # 获取价格
                price = good.ele("@class=price-row").ele("@class=price price-normal").text.strip()
                jd_price_elem = good.ele('.:item-b2cprice', timeout=0.5)
                jd_price = jd_price_elem.text.strip() if jd_price_elem else '暂无'

                # 构造数据字典
                dit = {
                    '标题': title,
                    '品牌': brand,
                    '系列': series,
                    '型号': model,
                    '参考价': price,
                    '京东价': jd_price,
                }
                csv_writer.writerow(dit)
                print(dit)
            except Exception as e:
                print(f"处理商品时出错: {e}")
                continue

        # 点击下一页
        next_button = dp.ele("@class=page-box").ele("@class=pagebar").ele("@class=next")
        if next_button:
            next_button.click()
            time.sleep(2)
        else:
            print("没有下一页了")
            break

    # 关闭页面
    dp.quit()