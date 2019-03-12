from django import forms
from django.forms import widgets
from app import models
from django.core.exceptions import ValidationError


class MyForm(forms.Form):
    username = forms.CharField(max_length=8, min_length=3, label='用户名',
                               error_messages={'required': '不能为空', 'max_length': '太长', 'min_length': '太短'},
                               widget=widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=9, min_length=4, label='密码',
                               error_messages={'required': '不能为空', 'max_length': '太长', 'min_length': '太短'},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_password = forms.CharField(max_length=9, min_length=4, label='确认密码',
                                  error_messages={'required': '不能为空', 'max_length': '太长', 'min_length': '太短'},
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}))



    email = forms.EmailField(label='邮箱', widget=widgets.EmailInput(attrs={'class': 'form-control'}),
                             error_messages={'required': '不能为空'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        user = models.UserInfo.objects.filter(username=username).first()
        if user:
            raise ValidationError('用户已存在')
        return username

    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password == re_password:
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致')
