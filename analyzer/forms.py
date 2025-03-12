# forms.py
from django import forms

class MemorySearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100,
        required=False,
        label='搜索内存',
        widget=forms.TextInput(attrs={'placeholder': '输入内存标题或价格范围'})
    )