from .models import Post
from .models import Comment
from django import forms
from django.forms import ModelForm


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']

        def clean_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError('Необнаружен текст Вашего поста')
            return data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

        def clean_text(self):
            data = self.cleaned_data['text']
            if data == '':
                raise forms.ValidationError(
                    'Необнаружен текст Вашего комментария'
                )
            return data
