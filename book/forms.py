from django import forms

class SearchForm(forms.Form):
    keyword = forms.CharField(
        label='タイトル検索',
         max_length=100,
        required=False,

)
