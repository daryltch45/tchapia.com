from django import forms
from .models import Project, PROJECT_STATUS_CHOICES, PRIORITY_CHOICES
from userauths.models import REGION_CHOICES, SERVICE_CHOICES

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
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Douala'
            }),
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

        # Only validate budget relationship if both values are provided
        if budget_min and budget_max:
            if budget_min >= budget_max:
                raise forms.ValidationError("Le budget maximum doit être supérieur au budget minimum.")

        return cleaned_data