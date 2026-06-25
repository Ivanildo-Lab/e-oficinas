from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.lista_itens, name='lista_itens'),
    path('novo/', views.novo_item, name='novo_item'),
    path('editar/<int:pk>/', views.editar_item, name='editar_item'),
    path('excluir/<int:pk>/', views.excluir_item, name='excluir_item'),
    path('grupos/', views.lista_grupos, name='lista_grupos'),
    path('grupos/novo/', views.novo_grupo, name='novo_grupo'),
    path('grupos/editar/<int:pk>/', views.editar_grupo, name='editar_grupo'),
    path('grupos/excluir/<int:pk>/', views.excluir_grupo, name='excluir_grupo'),
    path('movimentos/', views.lista_movimentos, name='lista_movimentos'),
    path('movimentos/novo/', views.nova_movimentacao, name='nova_movimentacao'),
    path('movimentos/editar/<int:pk>/', views.editar_movimentacao, name='editar_movimentacao'),
    path('movimentos/excluir/<int:pk>/', views.excluir_movimentacao, name='excluir_movimentacao'),
    path('buscar-itens/', views.buscar_itens, name='buscar_itens'),
    path('buscar-fornecedores/', views.buscar_fornecedores, name='buscar_fornecedores'),
    path('buscar-setores/', views.buscar_setores, name='buscar_setores'),
    path('relatorio/', views.relatorio_estoque, name='relatorio_estoque'),
    path('relatorio/movimentacoes-produto/', views.relatorio_movimentacoes_produto, name='relatorio_movimentacoes_produto'),
    path('relatorio/sugestao-compras/', views.sugestao_compras, name='sugestao_compras'),
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/novo/', views.novo_fornecedor, name='novo_fornecedor'),
    path('fornecedores/editar/<int:pk>/', views.editar_fornecedor, name='editar_fornecedor'),
    path('fornecedores/excluir/<int:pk>/', views.excluir_fornecedor, name='excluir_fornecedor'),
    path('setores/', views.lista_setores, name='lista_setores'),
    path('setores/novo/', views.novo_setor, name='novo_setor'),
    path('setores/editar/<int:pk>/', views.editar_setor, name='editar_setor'),
    path('setores/excluir/<int:pk>/', views.excluir_setor, name='excluir_setor'),
]