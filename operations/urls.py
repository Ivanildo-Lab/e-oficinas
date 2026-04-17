from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/novo/', views.novo_cliente, name='novo_cliente'),
    path('cliente/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('cliente/excluir/<int:pk>/', views.excluir_cliente, name='excluir_cliente'),
    
    path('veiculos/novo/', views.novo_veiculo, name='novo_veiculo'),
    path('veiculo/editar/<int:pk>/', views.editar_veiculo, name='editar_veiculo'),
    path('veiculo/excluir/<int:pk>/', views.excluir_veiculo, name='excluir_veiculo'),


    path('os/nova/', views.abrir_os, name='abrir_os'),
    path('os/', views.lista_os, name='lista_os'),
    path('os/<int:os_id>/', views.detalhes_os, name='detalhes_os'),
    path('os/editar/<int:os_id>/', views.editar_os, name='editar_os'),
    path('os/excluir/<int:os_id>/', views.excluir_os, name='excluir_os'),
    path('os/imprimir/<int:os_id>/', views.imprimir_os, name='imprimir_os'),    path('api/veiculo/<int:veiculo_id>/', views.buscar_dados_veiculo, name='buscar_dados_veiculo'),
]