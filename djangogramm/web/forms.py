from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AppUser, Post, Image
from cloudinary.forms import CloudinaryFileField
from django.forms import ModelForm
from .models import Photo
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit
from crispy_bootstrap5.bootstrap5 import FloatingField


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model = AppUser
        fields = ['username', 'email', 'password1', 'password2']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Field('title', css_class='form-control', placeholder='Post title'),
                css_class='form-floating mb-3 ms-3 pe-3'
            ),
            Div(
                Field('text', css_class='form-control', rows=4, placeholder='Describe your post'),
                css_class='form-floating mb-3 ms-3 pe-3'
            ),
            Div(
                Submit('submit', 'Create Post', css_class='btn btn-primary'),
                css_class='d-flex justify-content-center'
            ),
        )
