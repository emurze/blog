from django import forms

from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.CharField(max_length=25)
    content = forms.CharField(required=False, widget=forms.Textarea)


class CommitForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']


class SearchForm(forms.Form):
    query = forms.CharField(max_length=128)
    