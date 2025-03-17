from django import forms

class SubmitUrl(forms.Form):
    url = forms.URLField(label="Input Video URL", max_length= 100)