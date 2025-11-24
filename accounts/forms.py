from django import forms
from django.contrib.auth import get_user_model

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput()
    )
    password = forms.CharField(
        widget=forms.PasswordInput()
    )


# For for signup
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ('email', 'username')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd["password"] != cd["password2"]:
            raise forms.ValidationError("Passwords don't match.")
        return cd["password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_str = "form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-text-light-body dark:text-dark-body focus:outline-0 focus:ring-0 border-none bg-transparent h-full placeholder:text-gray-400 dark:placeholder:text-gray-500 px-3 py-2 text-base font-normal leading-normal"
        for field in self.fields.values():
            field.widget.attrs['class'] = class_str
        
        if 'email' in self.fields:
            self.fields['email'].widget.attrs['placeholder'] = 'you@example.com'
        if 'password' in self.fields:
            self.fields['password'].widget.attrs['placeholder'] = '••••••••'
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs['placeholder'] = '••••••••'
        if 'username' in self.fields:
            self.fields['username'].widget.attrs['placeholder'] = 'Username'


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        user_id = self.instance.id
        if get_user_model().objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("Email already in use.")
        return email


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("date_of_birth", "photo")
