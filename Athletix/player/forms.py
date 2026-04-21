from django import forms

from medical_staff.models import AthleteHealthRecord
from user.models import User, MedicalProfile


class DoctorChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        specialty = ''
        try:
            specialty = obj.medical_profile.specialty
        except MedicalProfile.DoesNotExist:
            specialty = ''
        if specialty:
            return f"Dr. {obj.name} ({specialty})"
        return f"Dr. {obj.name}"


class PlayerHealthReportForm(forms.ModelForm):
    doctor = DoctorChoiceField(
        queryset=User.objects.filter(role='medical', is_active=True).order_by('name'),
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = AthleteHealthRecord
        fields = [
            'doctor',
            'heart_rate',
            'blood_pressure',
            'weight_kg',
            'sleep_hours',
            'injury_status',
            'injury_notes',
            'recovery_status',
            'performance_notes',
        ]
        labels = {
            'doctor': 'Select Doctor (by designation/specialty)',
        }
        widgets = {
            'heart_rate': forms.NumberInput(attrs={'class': 'form-input', 'min': 30, 'max': 220}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '120/80'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1', 'min': 0, 'max': 24}),
            'injury_status': forms.Select(attrs={'class': 'form-input'}),
            'injury_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'recovery_status': forms.Select(attrs={'class': 'form-input'}),
            'performance_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
