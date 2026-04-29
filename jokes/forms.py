from django import forms
from django.core.exceptions import ValidationError
import re


class KeywordForm(forms.Form):
    keyword = forms.CharField(
        max_length=100,
        label="Enter keyword",
        widget=forms.TextInput(attrs={
            "placeholder": "Enter text",
            "pattern": "[A-Za-z ]+",
            "title": "Only English letters allowed"
        })
    )
    
    def clean_keyword(self):
        keyword = self.cleaned_data.get('keyword')
        if keyword and not re.match(r'^[A-Za-z ]+$', keyword):
            raise ValidationError('Only English letters and spaces are allowed.')
        return keyword
