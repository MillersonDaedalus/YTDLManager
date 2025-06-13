# forms.py
from django import forms
from .models import YtmusicAuth

class YTMusicAuthForm(forms.ModelForm):
    class Meta:
        model = YtmusicAuth
        fields = ['auth_file']
        labels = {
            'auth_file': 'YouTube Music Authentication File'
        }