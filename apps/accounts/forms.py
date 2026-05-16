from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    institutional_email = forms.EmailField(required=False)
    institution = forms.CharField(max_length=255, required=False)
    field_of_study = forms.CharField(max_length=255, required=False)
    academic_status = forms.ChoiceField(choices=User.AcademicStatus.choices)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username',
                  'institutional_email', 'institution',
                  'field_of_study', 'academic_status', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'avatar', 'bio',
                  'institution', 'field_of_study', 'academic_status',
                  'location', 'title', 'orcid_id', 'website']