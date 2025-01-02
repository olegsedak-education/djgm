from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AppUser, Post, Image
from cloudinary.forms import CloudinaryFileField
from django.forms import ModelForm
from .models import Photo


class PhotoForm(ModelForm):
    image = CloudinaryFileField()

    class Meta:
        model = Photo
        fields = ['image']



class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        print('>>>', data, initial)
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileFieldForm(forms.Form):
    file_field = MultipleFileField()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model = AppUser
        fields = ['username', 'email', 'password1', 'password2']


class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text']


class ImageOnPostCreationForm(forms.Form):
    image = MultipleFileField()
    class Meta:
        model = Image
        fields = ['image']
        widgets = {
            'image': MultipleFileInput(),
        }

