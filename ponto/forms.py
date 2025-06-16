from django import forms
from .models import Profissional, RegistroPonto
from django.contrib.auth.models import User

class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['cpf', 'gestor', 'data_admissao', 'horario_entrada', 'intervalo_inicio', 'intervalo_fim', 'horario_saida']
        widgets = {
            'data_admissao': forms.DateInput(attrs={'type': 'date'}),
            'horario_entrada': forms.TimeInput(attrs={'type': 'time'}),
            'intervalo_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'intervalo_fim': forms.TimeInput(attrs={'type': 'time'}),
            'horario_saida': forms.TimeInput(attrs={'type': 'time'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        
class RegistroPontoForm(forms.ModelForm):
    hora = forms.TimeField(
        input_formats=['%H:%M'],              # aceita apenas HH:MM
        widget=forms.TimeInput(format='%H:%M')  # exibe apenas HH:MM
    )
    class Meta:
        model = RegistroPonto
        fields = ['hora']