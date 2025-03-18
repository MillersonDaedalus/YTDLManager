from django import forms


def LoginForm(forms.Form):

    username = forms.CharField(required=True)
    password = forms.PasswordInput()

