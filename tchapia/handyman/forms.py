from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import Handyman, ProjectOffer
from userauths.models import User, REGION_CHOICES, SERVICE_CHOICES, CITIES

class HandymanProfileForm(forms.ModelForm):
    class Meta:
        model = Handyman
        fields = [
            'experience_years', 'hourly_rate', 'skills',
            'availability', 'id_card_number', 'id_card_image'
        ]
        widgets = {
            'experience_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre d\'années d\'expérience'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tarif horaire en XAF',
                'step': '0.01'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez vos compétences et spécialités...'
            }),
            'availability': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'id_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de carte d\'identité'
            }),
            'id_card_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['hourly_rate'].required = False
        self.fields['id_card_number'].required = False
        self.fields['id_card_image'].required = False

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'service', 'region', 'bio', 'address', 'city'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de téléphone'
            }),
            'service': forms.Select(
                choices=SERVICE_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'region': forms.Select(
                choices=REGION_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Parlez-nous de vous...'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Votre adresse'
            }),
            'city': forms.Select(
                choices=CITIES,
                attrs={'class': 'form-select'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['phone'].required = False
        self.fields['bio'].required = False
        self.fields['address'].required = False
        self.fields['city'].required = False


class ProjectOfferForm(forms.ModelForm):
    class Meta:
        model = ProjectOffer
        fields = ['message', 'proposed_budget', 'estimated_duration']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre approche pour ce projet, votre expérience pertinente...'
            }),
            'proposed_budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre budget proposé en XAF',
                'step': '0.01'
            }),
            'estimated_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 3 jours, 1 semaine, 2 semaines'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['proposed_budget'].required = False
        self.fields['estimated_duration'].required = False