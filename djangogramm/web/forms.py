from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AppUser, UserProfile, Post, Tag
from cloudinary.forms import CloudinaryFileField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    class Meta:
        model = AppUser
        fields = ['username', 'email', 'password1', 'password2']


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Enter tag name'}
            )
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip().lower()
        return name


class PostForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas'
            }
        )
    )

    class Meta:
        model = Post
        fields = ['title', 'text', 'tags']

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
                Field(
                    'text',
                    css_class='form-control',
                    rows=4,
                    placeholder='Describe your post'
                ),
                css_class='form-floating mb-3 ms-3 pe-3'
            ),
            Div(
                Field(
                    'tags',
                    css_class='form-control',
                    placeholder='Enter tags separated by commas'
                ),
                css_class='form-floating mb-3 ms-3 pe-3'
            ),
            Div(
                Submit('submit', 'Create Post', css_class='btn btn-primary'),
                css_class='d-flex justify-content-center'
            ),
        )

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str:
            return []
        
        # Разбиваем строку на отдельные теги и очищаем их
        tag_names = [
            tag.strip().lower() for tag in tags_str.split(',') if tag.strip()
        ]
        return tag_names

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            # Обрабатываем теги
            tag_names = self.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
        return post


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    avatar = CloudinaryFileField()

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'birth_date', 'bio', 'avatar']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['avatar'].initial = user.avatar

    def save(self, commit=True, user=None):
        profile = super().save(commit=False)

        if user:
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.save()

            avatar = self.cleaned_data.get('avatar')

            if avatar:
                user.avatar = avatar
                user.save()

        if commit:
            profile.save()

        return profile
















