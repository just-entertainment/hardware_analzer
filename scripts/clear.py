# scripts/remove_decimal_zero.py
from django.db import transaction
from analyzer.models import RAM   # 替换成你的模型

def run():
    # 找出所有 comment_count 以 .0 结尾的记录
    records =RAM.objects.filter(comment_count__endswith='.0')
    print(f"Found {records.count()} records to update")

    with transaction.atomic():  # 使用事务确保数据安全
        for record in records:
            if record.comment_count.endswith('.0'):
                # 去掉最后 2 个字符（即 .0）
                record.comment_count = record.comment_count[:-2]
                record.save(update_fields=['comment_count'])  # 只更新 comment_count 字段

    print("Update completed!")