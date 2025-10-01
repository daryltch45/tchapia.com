from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, USER_TYPE, REGION_CHOICES, SERVICE_CHOICES

# Add empty choice for service selection
SERVICE_FORM_CHOICES = [('', 'Sélectionnez un service')] + list(SERVICE_CHOICES)

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Prénom'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nom de famille'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'votre@email.com'
    }))
    phone = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': '677123456'
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Douala'
    }))
    region = forms.ChoiceField(
        choices=REGION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE,
        initial='client',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    service = forms.ChoiceField(
        choices=SERVICE_FORM_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'service-field'
        })
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "city", "region", "user_type", "service", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le mot de passe'
        })

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        service = cleaned_data.get('service')

        if user_type == 'artisan' and not service:
            raise forms.ValidationError("Les artisans doivent sélectionner un service.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'votre@email.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Mot de passe'
    }))