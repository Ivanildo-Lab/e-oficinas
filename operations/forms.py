from django import forms
from .models import Cliente, Veiculo, OrdemServico
from workshops.models import Mecanico 

# 1. FORMULÁRIO DE CLIENTE
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'telefone', 'email', 'endereco','cpf','cnpj']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

# 2. FORMULÁRIO DE VEÍCULO (Removido o campo 'mecanico' daqui)
class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'cliente', 'placa', 'marca', 'modelo', 'ano', 
            'versao', 'motor', 'cor', 'chassi', 
            'transmissao', 'combustivel', 'portas', 'tem_abs'
        ]
    def __init__(self, *args, **kwargs):
        oficina = kwargs.pop('oficina', None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-control'})
        if oficina:
            self.fields['cliente'].queryset = Cliente.objects.filter(oficina=oficina)

# 3. FORMULÁRIO DA ORDEM DE SERVIÇO (Mecânico entra aqui!)
class ChecklistOSForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = [
            'mecanico', 'veiculo', 'whatsapp', 'onde_nos_conheceu', 
            'horario_orcamento', 'data_entrega', 'km_atual', 
            'servico_solicitado', 'ultima_troca_oleo_data', 
            'ultima_troca_oleo_km', 'luz_injecao_acesa','nivel_combustivel',
            'capa_protecao_frontal', 'capa_banco', 
            'filme_volante', 'filme_cambio_freio', 'conclusao_tecnica','mapa_avarias_base64', 'assinatura_cliente_base64'
        ]
        widgets = {
            'horario_orcamento': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'data_entrega': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'ultima_troca_oleo_data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'servico_solicitado': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'conclusao_tecnica': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'mecanico': forms.Select(attrs={'class': 'form-control'}),
            'nivel_combustivel': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }
    def __init__(self, *args, **kwargs):
        oficina = kwargs.pop('oficina', None)
        super().__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.TimeInput, forms.DateTimeInput, forms.Select, forms.Textarea)):
                field.widget.attrs.update({'class': 'form-control'})
        
        if oficina:
            self.fields['veiculo'].queryset = Veiculo.objects.filter(oficina=oficina)
            # Filtra mecânicos apenas da oficina logada
            self.fields['mecanico'].queryset = Mecanico.objects.filter(oficina=oficina, ativo=True)

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Campo customizado que utiliza o widget acima
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# Campo customizado que utiliza o widget acima
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
   
class OSFotoForm(forms.Form):
    fotos = MultipleFileField(label='Selecionar Fotos', required=False)