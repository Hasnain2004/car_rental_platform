from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, SupportRequest, Booking
import datetime

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

class BookingForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().strftime('%Y-%m-%d')}),
        initial=datetime.date.today
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().strftime('%Y-%m-%d')}),
        initial=lambda: datetime.date.today() + datetime.timedelta(days=1)
    )
    
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date.")
            if start_date < datetime.date.today():
                raise forms.ValidationError("Start date cannot be in the past.")
        
        return cleaned_data 