from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator
from django.utils import timezone
from haystack.forms import *

from coolcars.models import *


# register form
class RegisterForm(forms.ModelForm):
    username = forms.CharField(required=True, error_messages={'required': "user name cannot be empty!"})
    firstname = forms.CharField(required=True, error_messages={'required': "first name cannot be empty!"})
    lastname = forms.CharField(required=True, error_messages={'required': "last name cannot be empty!"})
    email = forms.EmailField(required=True, error_messages={'required': "email cannot be empty!"})
    password = forms.CharField(widget=forms.PasswordInput(),
                               max_length=30,
                               min_length=3,
                               required=True,
                               error_messages={'required': "password cannot be empty!"})
    password_confirm = forms.CharField(widget=forms.PasswordInput(),
                                       max_length=30,
                                       min_length=3,
                                       required=True,
                                       error_messages={'required': "password confirm cannot be empty!"})

    class Meta:
        model = User
        fields = ('username', 'firstname', 'lastname', 'email', 'password', 'password_confirm',)

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        if cleaned_data.get("password") != cleaned_data.get("password_confirm"):
            print("Password and Password Confirm don't match!")
            raise forms.ValidationError(
                "Password and Password Confirm don't match!"
            )

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken")
        return username

    def save(self, commit=True):
        cleaned_data = super(RegisterForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = User.objects.create(username=username)
        user.set_password(password)
        user.first_name = cleaned_data.get("firstname")
        user.last_name = cleaned_data.get("lastname")
        user.email = cleaned_data.get('email')
        user.last_login = timezone.now()
        if commit:
            user.save()
        return user


class MySearchForm(SearchForm):

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(SearchForm, self).search().order_by('-favorite')
        paginator = Paginator(sqs, int(10))
        page = paginator.page(int(3))
        sqs = sorted(page.object_list, key=lambda k: k['-favorite'])
        # sqs = SearchQuerySet().models(Post).order_by('-favorite', '-published_date')

        return sqs
