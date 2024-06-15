from django import forms
from . import models
from django.core.validators import RegexValidator
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female')
]
class CustomDateInput(forms.widgets.DateInput):
    input_type = 'date'
class UserForm(forms.ModelForm):
    password = forms.CharField(max_length=150, label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'pattern': '(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
               'title': 'Password must contain: minimum 8 characters, 1 letter, 1 number', 'class': 'modal-placeholder' , 'autocomplete': 'on'}))
    confirm = forms.CharField(max_length=150, label='Confirm', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'modal-placeholder' , 'autocomplete': 'on'}))
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Username', 'pattern': '^[A-Za-z][A-Za-z0-9_]{6,12}$', 'title': 'Username must contain: minimum 6 characters, maximum 12 characters and no special character (@, #, $, ...)', 'class': 'modal-placeholder', 'autocomplete': 'on'}))
    
    class Meta():
        model = models.User
        fields = ('username', 'password')
        
class UserProfileInfoForm(forms.ModelForm):

    class Meta():
        model = models.UserProfileInfo
        exclude = ('user', 'hasSurvey', )