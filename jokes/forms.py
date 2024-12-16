from django import forms

class KeywordForm(forms.Form):
    keyword = forms.CharField(max_length=100, label="Enter a keyword for the joke")

class LanguageForm(forms.Form):
    language = forms.CharField(max_length=100, label="Enter language of joke")