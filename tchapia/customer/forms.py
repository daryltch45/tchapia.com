from django import forms
from .models import Project, Customer, PROJECT_STATUS_CHOICES, PRIORITY_CHOICES
from userauths.models import User, REGION_CHOICES, SERVICE_CHOICES, CITIES
from datetime import date

class PostProjectForm(forms.ModelForm):
    service = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Project
        fields = [
            'name', 'description', 'service', 'budget_min', 'budget_max',
            'location_address', 'city', 'region', 'priority', 'deadline'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Réparation plomberie urgente'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre projet en détail...'
            }),
            'budget_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Budget minimum en XAF (optionnel)'
            }),
            'budget_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Budget maximum en XAF (optionnel)'
            }),
            'location_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Adresse complète du projet'
            }),
            'city': forms.Select(
                choices=CITIES,
                attrs={'class': 'form-select'}
            ),
            'region': forms.Select(
                choices=REGION_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'priority': forms.Select(
                choices=PRIORITY_CHOICES,
                attrs={'class': 'form-select'}
            ),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            },  format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add empty choice for service
        service_choices = [('', 'Sélectionnez un service')] + list(SERVICE_CHOICES)
        self.fields['service'].choices = service_choices

        # Make optional fields
        self.fields['deadline'].required = False
        self.fields['budget_min'].required = False
        self.fields['budget_max'].required = False

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get('budget_min')
        budget_max = cleaned_data.get('budget_max')
        deadline = cleaned_data.get('deadline')

        # valid budget 
        if budget_min and budget_max:
            if budget_min >= budget_max:
                raise forms.ValidationError("Le budget maximum doit être supérieur au budget minimum.")
        
        # Deadline cannot be in the past 
        if deadline and deadline <  date.today(): 
            self.add_error('deadline', "La date limite ne peut pas être dans le passé.")


        return cleaned_data

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'preferred_payment_method', 'mobile_money_number'
        ]
        widgets = {
            'preferred_payment_method': forms.Select(
                choices=[
                    ('', 'Sélectionnez un mode de paiement'),
                    ('mobile_money', 'Mobile Money'),
                    ('bank_transfer', 'Virement bancaire'),
                    ('cash', 'Espèces'),
                    ('credit_card', 'Carte de crédit'),
                ],
                attrs={'class': 'form-select'}
            ),
            'mobile_money_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro Mobile Money'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional
        self.fields['preferred_payment_method'].required = False
        self.fields['mobile_money_number'].required = False

class CustomerUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'region', 'bio', 'address', 'city'
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