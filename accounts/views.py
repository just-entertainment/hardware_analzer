from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomUserChangeForm
from analyzer.models import Favorite, PriceAlert
import logging

# 初始化日志记录器
logger = logging.getLogger(__name__)

class RegisterView(View):
    """处理用户注册"""
    def get(self, request):
        """显示注册表单"""
        form = CustomUserCreationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        """处理注册表单提交"""
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "注册成功！欢迎加入配件分析平台！")
            return redirect('analyzer:index')
        messages.error(request, "注册失败，请检查输入信息")
        return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(View):
    """处理用户登录"""
    template_name = 'accounts/login.html'

    def get(self, request):
        """显示登录表单"""
        form = CustomAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """处理登录表单提交"""
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            logger.info(f"用户 {user.username} 登录成功")
            messages.success(request, "登录成功！")
            return redirect('analyzer:index')
        logger.error(f"登录失败: {form.errors}")
        messages.error(request, "登录失败，请检查输入信息")
        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    """处理用户登出"""
    def get(self, request):
        """登出用户并重定向到登录页"""
        logout(request)
        messages.success(request, "已成功登出")
        return redirect('accounts:login')

class ProfileView(LoginRequiredMixin, View):
    """显示用户个人资料、收藏和降价提醒"""
    def get(self, request):
        """查询用户收藏和降价提醒，渲染个人资料页面"""
        favorite_objects = Favorite.objects.filter(user=request.user).select_related('content_type')
        price_alerts = PriceAlert.objects.filter(user=request.user).select_related('favorite__content_type')
        return render(request, 'accounts/profile.html', {
            'user': request.user,
            'favorite_objects': favorite_objects,
            'price_alerts': price_alerts
        })

class ChangePasswordView(LoginRequiredMixin, View):
    """处理密码修改"""
    def get(self, request):
        """显示密码修改表单"""
        return render(request, 'accounts/change_password.html')

    def post(self, request):
        """处理密码修改提交"""
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "旧密码错误")
        elif new_password != confirm_password:
            messages.error(request, "新密码与确认密码不匹配")
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "密码修改成功，请重新登录")
            logout(request)
            return redirect('accounts:login')

        return render(request, 'accounts/change_password.html')

class EditProfileView(LoginRequiredMixin, View):
    """处理用户资料编辑"""
    def get(self, request):
        """显示资料编辑表单"""
        form = CustomUserChangeForm(instance=request.user)
        return render(request, 'accounts/edit_profile.html', {'form': form})

    def post(self, request):
        """处理资料编辑提交"""
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "个人资料更新成功")
            return redirect('accounts:profile')
        messages.error(request, "更新失败，请检查输入信息")
        return render(request, 'accounts/edit_profile.html', {'form': form})