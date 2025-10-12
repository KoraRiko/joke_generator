from django import forms


class KeywordForm(forms.Form):
    keyword = forms.CharField(
        max_length=100,
        label="Enter keyword",
        widget=forms.TextInput(attrs={"placeholder": "Enter text"})
    )


class LanguageForm(forms.Form):
    language = forms.CharField(
        max_length=100,
        required=False,
        label="Enter language",
        widget=forms.TextInput(attrs={"placeholder": "Enter text"})
    )
