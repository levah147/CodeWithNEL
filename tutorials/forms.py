from django import forms
from .models import Subscriber

class NewsletterForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'flex-1 px-4 py-3 rounded-button border-none focus:ring-2 focus:ring-primary/20',
                'placeholder': 'Enter your email'
            }
        )
    )
    
    gdpr_consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                'class': 'mt-1',
                'id': 'gdpr'
            }
        )
    )
    
    class Meta:
        model = Subscriber
        fields = ['email', 'gdpr_consent']

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'w-full pl-12 pr-4 py-3 rounded-lg bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary/20 text-base',
                'placeholder': 'Search tutorials...'
            }
        )
    )

