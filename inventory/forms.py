from django import forms
from .models import GrupoProduto, ItemEstoque, MovimentoEstoque, Fornecedor, Setor


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'telefone', 'email', 'contato', 'observacao', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SetorForm(forms.ModelForm):
    class Meta:
        model = Setor
        fields = ['nome', 'responsavel', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ItemEstoqueForm(forms.ModelForm):
    class Meta:
        model = ItemEstoque
        fields = ['grupo', 'nome_item', 'marca', 'referencia', 'descricao', 'quantidade', 'preco_unitario', 'minimo_ideal']
        widgets = {
            'grupo': forms.Select(attrs={'class': 'form-control'}),
            'nome_item': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'preco_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'minimo_ideal': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        oficina = kwargs.pop('oficina', None)
        super().__init__(*args, **kwargs)
        if oficina is not None:
            self.fields['grupo'].queryset = GrupoProduto.objects.filter(oficina=oficina)

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is None or quantidade < 0:
            raise forms.ValidationError('A quantidade deve ser zero ou maior.')
        return quantidade

    def clean_preco_unitario(self):
        preco = self.cleaned_data.get('preco_unitario')
        if preco is None or preco < 0:
            raise forms.ValidationError('O preço unitário deve ser zero ou maior.')
        return preco


class MovimentoEstoqueForm(forms.ModelForm):
    item_search = forms.CharField(
        label='Produto',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'off',
            'list': 'item_search_list',
            'placeholder': 'Digite parte do nome ou referência',
        })
    )

    class Meta:
        model = MovimentoEstoque
        fields = ['item', 'tipo', 'quantidade', 'valor_unitario', 'fornecedor', 'setor_destino', 'observacao', 'data']
        widgets = {
            'item': forms.HiddenInput(),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'fornecedor': forms.Select(attrs={'class': 'form-control'}),
            'setor_destino': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'data': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        oficina = kwargs.pop('oficina', None)
        super().__init__(*args, **kwargs)
        if oficina is not None:
            self.fields['item'].queryset = ItemEstoque.objects.filter(oficina=oficina)
            self.fields['fornecedor'].queryset = Fornecedor.objects.filter(oficina=oficina, ativo=True)
            self.fields['setor_destino'].queryset = Setor.objects.filter(oficina=oficina, ativo=True)
        self.fields['valor_unitario'].required = False
        self.fields['fornecedor'].required = False
        self.fields['setor_destino'].required = False

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        if quantidade is None or quantidade <= 0:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        return quantidade

    def clean_valor_unitario(self):
        valor = self.cleaned_data.get('valor_unitario')
        item = self.cleaned_data.get('item')
        if (valor is None or valor == 0) and item is not None:
            return item.preco_unitario
        return valor

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        # Remove item_search dos dados processados, pois não é um campo do modelo
        if 'item_search' in cleaned_data:
            del cleaned_data['item_search']
        if not item:
            raise forms.ValidationError('Selecione um produto válido usando a lista de sugestões.')
        return cleaned_data
