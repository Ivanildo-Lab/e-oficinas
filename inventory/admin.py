from django.contrib import admin
from .models import GrupoProduto, ItemEstoque, MovimentoEstoque, Servico, Fornecedor, Setor


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'contato', 'ativo', 'oficina')
    search_fields = ('nome', 'contato')
    list_filter = ('oficina', 'ativo')


@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'responsavel', 'ativo', 'oficina')
    search_fields = ('nome', 'responsavel')
    list_filter = ('oficina', 'ativo')


@admin.register(GrupoProduto)
class GrupoProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'oficina')
    search_fields = ('nome',)
    list_filter = ('oficina',)


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    list_display = ('nome_item', 'marca', 'referencia', 'grupo', 'oficina', 'quantidade', 'preco_unitario', 'minimo_ideal')
    search_fields = ('nome_item', 'referencia', 'marca', 'grupo__nome')
    list_filter = ('oficina', 'grupo')


@admin.register(MovimentoEstoque)
class MovimentoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'item', 'quantidade', 'valor_unitario', 'fornecedor', 'setor_destino', 'data')
    search_fields = ('item__nome_item', 'item__referencia', 'fornecedor__nome', 'setor_destino__nome')
    list_filter = ('tipo', 'data')


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('nome_servico', 'oficina', 'preco')
    search_fields = ('nome_servico',)
    list_filter = ('oficina',)
