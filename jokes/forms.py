from django import forms

class KeywordForm(forms.Form):
    keyword = forms.CharField(max_length=100, label="Enter a keyword ")

class LanguageForm(forms.Form):
    language = forms.CharField(max_length=100, label="Enter language ")