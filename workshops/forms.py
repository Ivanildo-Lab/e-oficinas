# F:\HD 1tb\...\workshops\forms.py
from django import forms
from .models import Mecanico

class MecanicoForm(forms.ModelForm):
    class Meta:
        model = Mecanico
        fields = ['nome', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nome'].widget.attrs.update({'class': 'form-control'})