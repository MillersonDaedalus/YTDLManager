# forms.py
from django import forms
from .models import YTMusicAuth

class YTMusicAuthForm(forms.ModelForm):
    class Meta:
        model = YTMusicAuth
        fields = ['auth_file']
        labels = {
            'auth_file': 'YouTube Music Authentication File'
        }